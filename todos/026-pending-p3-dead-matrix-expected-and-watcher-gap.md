---
status: complete
priority: p3
issue_id: "026"
tags: [code-review, quality, simplicity]
dependencies: []
---

# 026 — Dead `_MATRIX_EXPECTED` Dict and Redundant `watcher_gap` Field

## Problem Statement

Two distinct simplification issues in `web.py`:
1. `_MATRIX_EXPECTED` is defined but never referenced anywhere in the file — pure dead data.
2. `watcher_gap` in API responses is always `not monitored` — it's a redundant field that adds noise for API consumers.

## Findings

**Location:** `src/trueneutral/web.py`

**Issue 1 — Dead data:**
`_MATRIX_EXPECTED` (lines 218-225) is a hardcoded dict of "expected" matrix outcomes from a real run. It's defined at module level but `grep` of the file finds zero references to it in any function or endpoint. It's pure dead data.

**Issue 2 — Redundant field:**
Lines 378 and 520 both include:
```python
"monitored":   meta["monitored"],
"watcher_gap": not meta["monitored"],
```
`watcher_gap` is definitionally `not monitored`. Any consumer can compute it trivially. The field doubles the contract surface with zero information gain.

## Proposed Solutions

### Option A: Remove Both
- Delete `_MATRIX_EXPECTED` entirely (lines 218-225)
- Remove `watcher_gap` from result dicts at lines 378 and 520
- Update frontend to compute `!monitored` where it reads `watcher_gap`
- **Effort:** Small
- **Risk:** Low (breaking API change for `watcher_gap` — check frontend usage first)

## Recommended Action

Option A — check all `watcher_gap` references in `index.html` before removing.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`, `src/trueneutral/static/index.html`
- **Key lines:** `web.py:218-225` (dead dict), `web.py:378`, `web.py:520` (redundant field)

## Acceptance Criteria

- [ ] `_MATRIX_EXPECTED` removed or documented with a TODO explaining intended use
- [ ] `watcher_gap` removed from API responses; frontend uses `!monitored`
- [ ] All existing tests pass

## Work Log

- 2026-03-20: Created from code-simplicity-reviewer analysis of feat/openclaw-template-expansion branch
