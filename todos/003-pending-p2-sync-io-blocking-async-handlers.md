---
status: complete
priority: p2
issue_id: "003"
tags: [code-review, performance, async]
dependencies: []
---

# 003 — Synchronous File I/O Blocks the Async Event Loop

## Problem Statement

All four FastAPI route handlers perform synchronous, blocking file I/O (`Path.read_text()`, `Path.iterdir()`) on the async event loop thread. Under concurrent load this serializes all requests, making the effective concurrency of the server equal to 1.

## Findings

**Location:** `src/trueneutral/web.py` — all four handlers

- `_read_file` (line 99) calls `path.read_text()` synchronously
- Called 4× in `_agent_detail`, 8× in `_simulate_attack`, 1× in `_run_matrix`
- `_agent_slugs()` (line 89) calls `AGENTS_DIR.iterdir()` + `is_dir()` per entry
- All scoring (`_score_file`) is CPU-bound string processing done synchronously

At 10 concurrent users each hitting `/api/attack`, all 32 scoring operations per request queue on the single event loop thread. Latency for the Nth user scales as N × per-request time.

## Proposed Solutions

### Option A: asyncio.to_thread for blocking I/O (Recommended)
```python
import asyncio

async def _read_file_async(path: Path) -> str:
    return await asyncio.to_thread(_read_file, path)

async def _agent_slugs_async() -> list[str]:
    return await asyncio.to_thread(_agent_slugs)
```
Then use `await` in handlers.
- **Pros:** Minimal refactor, unblocks event loop, built-in stdlib
- **Effort:** Medium
- **Risk:** Low

### Option B: Startup cache (addresses both sync I/O and redundant reads)
At `create_app()` time, pre-read and pre-score all agent files. Store in a module-level dict. Refresh on a background task or TTL. `/api/agents` becomes a pure dict lookup.
- **Pros:** Eliminates all per-request I/O for read-mostly endpoints; O(1) for fleet list
- **Cons:** More complex; needs cache invalidation strategy
- **Effort:** Medium-Large
- **Risk:** Medium (stale data if files change)

### Option C: Add `run_in_executor` for scoring
For the CPU-bound scoring, offload to a thread pool executor.
- **Pros:** Isolates blocking work from the event loop
- **Effort:** Medium

## Recommended Action

Option A as a quick fix; Option B as the follow-up for the fleet list endpoint.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` — all handlers
- At 10 concurrent `/api/attack` requests: 10 × ~32 scoring operations fully serialized

## Acceptance Criteria

- [ ] `/api/attack` handles 10 concurrent requests without linear latency stacking
- [ ] File reads use `asyncio.to_thread` or equivalent
- [ ] Behavior is identical to current synchronous version

## Work Log

- 2026-03-11: Found by performance-oracle agent in PR #2 code review
