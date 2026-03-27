---
status: complete
priority: p3
issue_id: "011"
tags: [code-review, architecture, refactoring]
dependencies: []
---

# 011 — Domain Logic Embedded in web.py / Private watcher Symbols Imported

## Problem Statement

`web.py` implements substantial domain logic (`_simulate_attack`, `_run_matrix`, `_agent_detail`, `_score_file`, all attack payload data) instead of delegating to a service layer. It also imports 6 underscore-prefixed private symbols from `watcher.py`, creating hidden coupling that makes both modules hard to refactor or test independently.

## Findings

**Location:** `src/trueneutral/web.py` throughout

**Domain logic in HTTP module:**
- `_ATTACK_PAYLOADS`, `_TECHNIQUE_LABELS`, `_VECTOR_LABELS`, `_MATRIX_EXPECTED`, `_ALIGNMENT_COLORS` — data tables
- `_simulate_attack()`, `_run_matrix()`, `_agent_detail()`, `_score_file()` — simulation & scoring
- All sentiment generation logic (lines 256–283)

**Private symbol imports from watcher:**
- Lines 107, 196, 263, 300: imports `_detect_threats`, `_score_heuristic`, `_THREAT_LABELS`, `_CLEAN_OPENERS`, `_DRIFT_OPENERS`, `_TECHNIQUE_PUNCHLINES`

`watcher.py` has no `__all__`, so there's no declared public API. Any refactor of watcher internals silently breaks `web.py`, and `web.py` has zero tests.

**Tests:** `tests/` has `test_alignment.py`, `test_context.py`, `test_watcher.py` — no `test_web.py`.

## Proposed Solutions

### Option A: Extract trueneutral.simulator module
Move `_simulate_attack`, `_run_matrix`, `_ATTACK_PAYLOADS`, `_TECHNIQUE_LABELS`, `_VECTOR_LABELS`, and sentiment data to `trueneutral/simulator.py`. `web.py` becomes a thin HTTP adapter.
- **Pros:** Matches existing `cli.py` → `watcher.py` pattern; enables testing without FastAPI
- **Effort:** Medium

### Option B: Define __all__ in watcher.py
Expose `score_heuristic`, `detect_threats`, `THREAT_LABELS` etc. as public symbols.
- **Pros:** Lower refactor risk, immediate improvement
- **Effort:** Small

### Option C: Keep as-is, add tests for the helper functions
Add `tests/test_web.py` that imports and tests `_score_file`, `_simulate_attack`, `_run_matrix` directly.
- **Effort:** Medium
- **Risk:** None — testing private functions is acceptable for a young codebase

## Recommended Action

Option B (define `__all__` in watcher, rename key functions as public) + Option C (add tests) as a short-term improvement. Option A as a future-state goal.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`, `src/trueneutral/watcher.py`

## Acceptance Criteria

- [ ] `watcher.py` defines `__all__` with stable public API
- [ ] `web.py` imports from the public API only
- [ ] `tests/test_web.py` exists with coverage of `_score_file`, `_simulate_attack`, `_run_matrix`

## Work Log

- 2026-03-11: Found by architecture-strategist agent in PR #2 code review
