---
status: pending
priority: p1
issue_id: "018"
tags: [code-review, architecture, concurrency]
dependencies: []
---

# 018 — `AgentContext` Mutability Will Cause Data Races with `guardian.py`

## Problem Statement

`AgentContext` is a mutable dataclass whose fields are mutated after construction (e.g., `ctx.sentiment = ...` in `_refresh_sentiment`). The planned `Guardian` daemon fires from a `watchdog` background thread and will need to update `violations` on the same `AgentContext` that the polling loop is reading and serialising to JSON. The current pattern has no locking — this is a latent data race that needs resolving before `guardian.py` is written.

## Findings

**Location:** `src/trueneutral/watcher.py:381-399` (AgentContext definition), `watcher.py:854-862` (_refresh_sentiment mutations)

```python
# watcher.py:854-862 — direct field mutation post-construction
ctx.sentiment = new_sentiment
ctx.sentiment_trigger = trigger
ctx.sentiment_updated_at = datetime.now()
```

The governance plan (plan doc lines 192-194) adds `rank`, `violations`, and `protection_tier_overrides` fields to `AgentContext`. The Guardian (a watchdog background thread) will mutate `violations` while the watcher polling loop reads the same object for `_write_json` serialisation.

**Secondary issue:** `sentiment_updated_at` at line 862 uses `datetime.now()` (naive, local time) while other fields use `datetime.now(tz=timezone.utc)`. This will cause a `TypeError` on comparison (`now - ctx.sentiment_updated_at`) when the two timezones mix.

## Proposed Solutions

### Option A: Frozen Dataclass + Copy-on-Update (Recommended)
Make `AgentContext` a `frozen=True` dataclass and use `dataclasses.replace(ctx, sentiment=..., ...)` for state transitions. Each update returns a new instance. The watcher holds a `dict[Path, AgentContext]` and replaces entries atomically.
- **Pros:** Thread-safe by construction, consistent with `Alignment` (already frozen)
- **Cons:** More allocations (acceptable for ~10-20 agents)
- **Effort:** Medium
- **Risk:** Medium (requires updating all mutation sites)

### Option B: Explicit State Transition Methods + Lock
Add `update_sentiment()` and `record_violation()` methods to `AgentContext` that acquire a `threading.Lock` before mutating.
- **Pros:** Smaller change, preserves mutation semantics
- **Cons:** Easy to forget the lock at future mutation sites
- **Effort:** Small
- **Risk:** Medium

### Option C: Fix the Timezone Bug Only (Minimal)
At minimum, fix `datetime.now()` → `datetime.now(tz=timezone.utc)` at lines 650 and 862. Defer thread safety to when Guardian is implemented.
- **Effort:** Tiny
- **Risk:** Very low

## Recommended Action

Option C immediately (fixes live bug). Option A before `guardian.py` implementation starts.

## Technical Details

- **Affected files:** `src/trueneutral/watcher.py`
- **Key lines:** 381-399 (AgentContext), 650, 862 (naive datetime calls), 854-862 (_refresh_sentiment mutations)

## Acceptance Criteria

- [ ] `datetime.now()` calls at lines 650 and 862 replaced with `datetime.now(tz=timezone.utc)`
- [ ] `AgentContext` state transitions safe for concurrent read/write before Guardian implementation
- [ ] `Alignment` frozen pattern followed for `AgentContext`

## Work Log

- 2026-03-20: Created from architecture-strategist + performance-oracle review of feat/openclaw-template-expansion branch
