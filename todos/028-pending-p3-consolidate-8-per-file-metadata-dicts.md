---
status: pending
priority: p3
issue_id: "028"
tags: [code-review, simplicity, architecture]
dependencies: ["017"]
---

# 028 — Consolidate 8 Parallel Per-File Metadata Dicts Into One

## Problem Statement

`web.py` defines 8 separate top-level dicts all keyed on the same 8 filenames: `_FILE_METADATA`, `_ENTRY_POINTS`, `_REMEDIATION`, `_PERSISTENCE`, `_PROPAGATES_TO`, `_IM_PT`, `_INCIDENTS`, and `_MATRIX_EXPECTED`. This is ~110 lines of Python encoding what is effectively one record per file. `_attack_paths` must perform 8 separate dict lookups per file (`_FILE_METADATA[fname]`, `_ENTRY_POINTS[fname]`, `_REMEDIATION[fname]`, etc.). Adding a new per-file field (e.g., the `tier` key from the governance plan) requires touching a 9th dict.

## Findings

**Location:** `src/trueneutral/web.py` lines 55–225

The per-file lookup in `_attack_paths` (lines 513-526) does 8 separate `[fname]` accesses. A single `_FILE_DATA` dict-of-dicts would make the relationship explicit and the addition of new fields (like governance `tier`) a one-place change.

```python
# Current: 8 separate dicts
_FILE_METADATA[fname]["role"]
_ENTRY_POINTS[fname]
_REMEDIATION[fname]

# Proposed: one dict
_FILE_DATA[fname]["role"]
_FILE_DATA[fname]["entry_points"]
_FILE_DATA[fname]["remediation"]
```

## Proposed Solutions

### Option A: Merge Into `_FILE_DATA` Dict-of-Dicts
Create one `_FILE_DATA: dict[str, dict]` with keys: `role`, `monitored`, `top_technique`, `entry_points`, `remediation`, `persistence`, `propagates_to`, `im_pt`, `incidents`. Access via `_FILE_DATA[fname]["remediation"]` etc.
- **Effort:** Small–Medium (mechanical restructure, no logic changes)
- **Risk:** Low
- **Dependency:** Best done as part of todo 017 (extract to threat_model.py)

## Recommended Action

Option A — defer until todo 017 (domain logic extraction) is in progress.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` (or new `threat_model.py`)
- **Key lines:** 55–225 (8 separate dicts), 513–526 (`_attack_paths` 8× lookups)

## Acceptance Criteria

- [ ] All 8 per-file dicts consolidated into `_FILE_DATA`
- [ ] Adding a new per-file field requires touching one dict, not N
- [ ] `_attack_paths` accesses `_FILE_DATA[fname][key]` instead of 8 separate dicts
- [ ] Governance `tier` field added to `_FILE_DATA` as part of this consolidation

## Work Log

- 2026-03-20: Created from code-simplicity-reviewer and architecture-strategist reviews of feat/openclaw-template-expansion branch
