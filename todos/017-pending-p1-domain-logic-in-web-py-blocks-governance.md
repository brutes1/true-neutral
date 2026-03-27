---
status: complete
priority: p1
issue_id: "017"
tags: [code-review, architecture, refactoring]
dependencies: []
---

# 017 — Domain Logic in `web.py` Blocks `governance.py` Development

## Problem Statement

`_ATTACK_PAYLOADS`, `_FILE_METADATA`, `_PERSISTENCE`, `_PROPAGATES_TO`, `_IM_PT`, `_INCIDENTS`, `_REMEDIATION`, `SCORED_FILES`, `CONTEXTUAL_FILES`, and all simulation functions live in `web.py` (the HTTP presentation layer). The planned `governance.py` module needs `FILE_TIERS` to align with `_FILE_METADATA`, but it cannot import from `web.py` without creating an inverted-layer dependency (domain importing from presentation). This architectural violation blocks the governance feature before it starts.

## Findings

**Location:** `src/trueneutral/web.py` lines 30–31, 55–215, 247–529

- `SCORED_FILES` / `CONTEXTUAL_FILES` at lines 30–31 — file taxonomy defined in HTTP layer
- `_FILE_METADATA` at lines 107–125 — per-file role/monitoring metadata needed by governance.py
- `_ATTACK_PAYLOADS` at lines 42–106 — attack payload data, domain concept
- `_simulate_attack`, `_run_matrix`, `_attack_paths`, `_score_file` — domain simulation functions in HTTP module
- `context.py:13` defines `_SCOREABLE_PERSONA_FILES` — a second, partially-overlapping file taxonomy list

The plan document (`docs/plans/2026-03-13-feat-agent-hierarchy-immutable-context-plan.md` line 382) notes `web.py:107` as where to update `_FILE_METADATA` for the `tier` key — this is the symptom of the misplacement.

## Proposed Solutions

### Option A: Extract `threat_model.py` (Recommended)
Create `src/trueneutral/threat_model.py` containing:
- `SCORED_FILES`, `CONTEXTUAL_FILES`, `ALL_PERSONA_FILES`
- `_FILE_METADATA` (extended with `tier` field from governance plan)
- `_ATTACK_PAYLOADS`, `_TECHNIQUE_LABELS`, `_VECTOR_LABELS`
- `_PERSISTENCE`, `_PROPAGATES_TO`, `_IM_PT`, `_INCIDENTS`, `_REMEDIATION`
- `_simulate_attack()`, `_run_matrix()`, `_attack_paths()`, `_score_file()`

`web.py` becomes a thin HTTP adapter. `governance.py` imports file taxonomy from `threat_model.py` without any dependency on `web.py`.
- **Effort:** Medium
- **Risk:** Low (mechanical extraction, no logic changes)

### Option B: Move Only Constants to `context.py`
Move `SCORED_FILES` and `CONTEXTUAL_FILES` to `context.py` which already owns file discovery. Leave simulation functions in `web.py` for now.
- **Pros:** Smaller change, unblocks `governance.py` immediately
- **Cons:** Still leaves simulation domain logic in wrong layer
- **Effort:** Small
- **Risk:** Low

## Recommended Action

Option B first (immediate unblock for governance.py), Option A as a follow-up refactor.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`, `src/trueneutral/context.py`, new `src/trueneutral/threat_model.py`
- **Governance plan dependency:** `governance.py` needs `FILE_TIERS: dict[str, ProtectionTier]` that maps the same 8 filenames — this dict must align with `_FILE_METADATA`

## Acceptance Criteria

- [ ] `SCORED_FILES` and `CONTEXTUAL_FILES` importable from `context.py` or `threat_model.py`
- [ ] `governance.py` can import file taxonomy without depending on `web.py`
- [ ] `_FILE_METADATA` accessible to `governance.py` for tier mapping
- [ ] All existing tests pass after the move
- [ ] `web.py` imports the constants from the new location

## Work Log

- 2026-03-20: Created from architecture-strategist review of feat/openclaw-template-expansion branch
