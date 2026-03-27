---
status: complete
priority: p2
issue_id: "021"
tags: [code-review, performance]
dependencies: []
---

# 021 — `_agent_slugs()` Called Multiple Times Per Request With No Cache

## Problem Statement

Every endpoint calls `await asyncio.to_thread(_agent_slugs)` for validation, then the downstream sync helper calls `AGENTS_DIR.iterdir()` again internally. At 100 agents this is two `readdir` syscalls per request minimum. There is zero caching — a fleet list built for `GET /api/agents` is discarded before the next request arrives 100ms later.

## Findings

**Location:** `src/trueneutral/web.py` lines 604, 620, 636, 649, 683, 713, 736 (slug validation calls)

Every endpoint that validates a slug does:
```python
slugs = await asyncio.to_thread(_agent_slugs)
if slug not in slugs:
    raise HTTPException(...)
```
Then `_agent_detail`, `_simulate_attack`, etc. each call `AGENTS_DIR.iterdir()` again independently.

For a fleet of 20 agents, `GET /api/agents` reads the directory once, builds the sorted list, then `POST /api/attack` 100ms later rebuilds it from scratch.

## Proposed Solutions

### Option A: Module-Level TTL Cache (Recommended)
Add a module-level `(list[str], float)` tuple, refreshed under a `threading.Lock` when the TTL (5 seconds) expires:
```python
_slug_cache: tuple[list[str], float] = ([], 0.0)
_slug_cache_lock = threading.Lock()

def _agent_slugs_cached() -> list[str]:
    global _slug_cache
    now = time.monotonic()
    if now - _slug_cache[1] < 5.0:
        return _slug_cache[0]
    with _slug_cache_lock:
        slugs = _agent_slugs()
        _slug_cache = (slugs, now)
    return slugs
```
- **Effort:** Small
- **Risk:** Low (5s TTL, local tool)

### Option B: Gather File Reads in `list_agents` Concurrently
Replace sequential `for slug in slugs` with `asyncio.gather(*)` for the CLAUDE.md reads in the fleet list endpoint. Independent of caching.
- **Effort:** Small
- **Risk:** Low

## Recommended Action

Both — Option A for slug caching, Option B for concurrent fleet reads.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`
- **Key lines:** 230 (`_agent_slugs`), 583-598 (`list_agents` sequential loop)

## Acceptance Criteria

- [ ] `_agent_slugs()` result cached with ≤ 5 second TTL
- [ ] Cache invalidated on agent create/delete
- [ ] Sequential file reads in `list_agents` replaced with `asyncio.gather`

## Work Log

- 2026-03-20: Created from performance-oracle review of feat/openclaw-template-expansion branch
