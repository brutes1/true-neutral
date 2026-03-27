---
status: complete
priority: p1
issue_id: "001"
tags: [code-review, security]
dependencies: []
---

# 001 — Path Traversal in GET /api/agents/{slug}

## Problem Statement

`_agent_detail()` constructs a filesystem path directly from the user-supplied URL slug with no canonicalization or boundary check. A crafted slug like `../../../etc` can escape `AGENTS_DIR` and read arbitrary directories on the server.

## Findings

**Location:** `src/trueneutral/web.py` lines 122–124

```python
agent_dir = AGENTS_DIR / slug
if not agent_dir.exists():
    return None
```

`pathlib` does not canonicalize paths on `/` concatenation. The only guard checks `exists()` — it does not verify the resolved path stays inside `AGENTS_DIR`. The route handler at line 381 calls `_agent_detail(slug)` with no prior allowlist check (unlike `POST /api/attack` which validates against `_agent_slugs()`).

PoC: `GET /api/agents/..%2F..%2Fetc` — if the directory exists, returns up to 8 file reads from that path silently.

## Proposed Solutions

### Option A: Add `is_relative_to` check (Recommended)
```python
def _agent_detail(slug: str) -> dict[str, Any] | None:
    agent_dir = (AGENTS_DIR / slug).resolve()
    if not agent_dir.is_relative_to(AGENTS_DIR.resolve()):
        return None
    if not agent_dir.exists():
        return None
```
- **Pros:** One-line fix, idiomatic pathlib (Python 3.9+), stops traversal at boundary
- **Cons:** None
- **Effort:** Small
- **Risk:** None — `is_relative_to` is stdlib

### Option B: Validate slug against allowlist first
Add `if slug not in _agent_slugs(): raise HTTPException(404)` at the top of the route handler.
- **Pros:** Consistent with how `/api/attack` handles it
- **Cons:** Still calls `_agent_slugs()` on every request (extra filesystem scan); allowlist is derived from the same AGENTS_DIR so a race exists
- **Effort:** Small
- **Risk:** Low

### Option C: Both (defense in depth)
Apply `is_relative_to` check AND allowlist validation.
- **Pros:** Belt-and-suspenders
- **Cons:** Slightly more code
- **Effort:** Small
- **Risk:** None

## Recommended Action

Option C — apply `is_relative_to` check in `_agent_detail` AND add slug allowlist check in the route handler.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` lines 122–124, 381–385
- **Also apply to:** `_simulate_attack` (line 198) and `_run_matrix` (line 304) as defense-in-depth, even though those have the allowlist guard

## Acceptance Criteria

- [ ] `GET /api/agents/..%2F..%2Fetc` returns 404, not a 200 with empty file list
- [ ] `GET /api/agents/helpful-assistant` still returns correct data
- [ ] `_agent_detail` resolves path and checks `is_relative_to(AGENTS_DIR.resolve())`

## Work Log

- 2026-03-11: Found by security-sentinel agent in PR #2 code review
