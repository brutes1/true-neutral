---
status: complete
priority: p2
issue_id: "022"
tags: [code-review, bug, correctness]
dependencies: []
---

# 022 — Naive `datetime.now()` Calls Will Cause `TypeError` in Watcher

## Problem Statement

Two calls in `watcher.py` use `datetime.now()` (naive, local time) while the rest of the codebase uses `datetime.now(tz=timezone.utc)` (timezone-aware). When arithmetic is performed between a naive and aware datetime (e.g., `now - ctx.sentiment_updated_at`), Python raises a `TypeError`. This silently suppresses sentiment refresh scheduling, causing stale data to be served indefinitely.

## Findings

**Location:** `src/trueneutral/watcher.py` lines 650 and 862

```python
# line 650 — naive (wrong)
if (datetime.now() - ctx.sentiment_updated_at).total_seconds() > ...

# line 862 — naive (wrong)
ctx.sentiment_updated_at = datetime.now()
```

If `sentiment_updated_at` was set by the UTC-aware path and then compared with a naive `datetime.now()`, Python raises `TypeError: can't subtract offset-naive and offset-aware datetimes`. This exception is caught by the outer `except Exception` at line ~870 and silently swallowed, meaning sentiment refresh never fires again for that agent.

## Proposed Solutions

### Option A: Replace Both Calls (Fix)
```python
# line 650
if (datetime.now(tz=timezone.utc) - ctx.sentiment_updated_at).total_seconds() > ...

# line 862
ctx.sentiment_updated_at = datetime.now(tz=timezone.utc)
```
- **Effort:** Tiny
- **Risk:** Very low

## Recommended Action

Option A — two-line fix.

## Technical Details

- **Affected files:** `src/trueneutral/watcher.py`
- **Key lines:** 650, 862

## Acceptance Criteria

- [ ] Both `datetime.now()` calls replaced with `datetime.now(tz=timezone.utc)`
- [ ] No `TypeError` when comparing `sentiment_updated_at` to current time
- [ ] Existing `test_watcher.py` datetime tests still pass

## Work Log

- 2026-03-20: Created from performance-oracle review of feat/openclaw-template-expansion branch
