---
status: complete
priority: p3
issue_id: "008"
tags: [code-review, quality, simplicity]
dependencies: []
---

# 008 — Dead Imports Inside Functions in web.py

## Problem Statement

`web.py` has three lazy `from trueneutral.watcher import ...` statements inside functions. The imports in `_run_matrix` and the first import in `_simulate_attack` import symbols that are never used directly — they're all handled by `_score_file` internally.

## Findings

**Location:** `src/trueneutral/web.py`

- **Line 196** (in `_simulate_attack`): `from trueneutral.watcher import _detect_threats, _score_heuristic, _THREAT_LABELS` — these are never called directly; `_score_file` wraps them all
- **Line 300** (in `_run_matrix`): same dead import — only `_score_file` is called
- **Line 263** (in `_simulate_attack`): `from trueneutral.watcher import _CLEAN_OPENERS, _DRIFT_OPENERS, _TECHNIQUE_PUNCHLINES` — these ARE used; move to module level
- **Line 107** (in `_score_file`): `from trueneutral.watcher import _detect_threats, _score_heuristic, _THREAT_LABELS` — only correct lazy import

Python caches modules in `sys.modules` so re-import doesn't re-execute modules, but attribute lookups execute on every call. `_score_file` is called 32× per `/api/attack` request.

## Proposed Solutions

### Option A: Delete dead imports, move live ones to module level
- Delete lines 196 and 300 entirely
- Move line 263's import to module level (no circular import risk — `watcher` is a core module)
- Keep line 107 or also move to module level
- **Effort:** Tiny

## Recommended Action

Option A.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` lines 196, 263, 300

## Acceptance Criteria

- [ ] Lines 196 and 300 deleted
- [ ] `_CLEAN_OPENERS`, `_DRIFT_OPENERS`, `_TECHNIQUE_PUNCHLINES` imported at module level
- [ ] All tests pass

## Work Log

- 2026-03-11: Found by code-simplicity-reviewer and performance-oracle agents in PR #2 code review
