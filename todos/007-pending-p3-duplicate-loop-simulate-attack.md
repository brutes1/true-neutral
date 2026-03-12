---
status: complete
priority: p3
issue_id: "007"
tags: [code-review, quality, simplicity]
dependencies: []
---

# 007 — Duplicate Loop Bodies in _simulate_attack() + Hardcoded CONTEXTUAL_FILES

## Problem Statement

`_simulate_attack()` has two nearly identical `for fname in ...` loops (lines 206–231 and 232–254) that differ only by `is_contextual: True` on the second. The `CONTEXTUAL_FILES` constant defined at line 23 is also re-typed as an inline literal at line 146 in `_agent_detail()`.

## Findings

**Location:** `src/trueneutral/web.py`

1. Lines 206–231: loop over `SCORED_FILES`, builds result dict
2. Lines 232–254: identical loop over `CONTEXTUAL_FILES`, adds `"is_contextual": True`
3. Line 146: `for fname in ("BOOT.md", "BOOTSTRAP.md", "USER.md", "TOOLS.md"):` — exact duplicate of `CONTEXTUAL_FILES` constant defined at line 23

Both loops: call `_read_file`, build `attacked_content`, call `_score_file` twice, compute `drifted`, build identical dict structure. ~25 lines of copy-paste. Risk: loops diverge silently over time.

## Proposed Solutions

### Option A: Merge into one loop (Recommended)
```python
for fname in (*SCORED_FILES, *CONTEXTUAL_FILES):
    fpath = agent_dir / fname
    is_contextual = fname in CONTEXTUAL_FILES
    original_content = _read_file(fpath)
    attacked_content = original_content + "\n\n" + payload if payload else original_content
    before = _score_file(original_content)
    after  = _score_file(attacked_content)
    drifted = (before["label"] != after["label"])
    if drifted:
        any_drifted = True
    entry = {
        "file": fname,
        "before": before,
        "after": after,
        "drifted": drifted,
        "original_content": original_content,
        "payload": payload,
        "new_threats": [t for t in after["threats"] if t not in before["threats"]],
        "new_threat_labels": [...],
        "is_contextual": is_contextual,
    }
    results.append(entry)
```
- **Effort:** Small
- Also add `"is_contextual": False` to scored entries for symmetric schema

### Option B: Leave as-is
- **Risk:** Loops will diverge when one is updated but not the other

## Recommended Action

Option A. Also fix line 146 to use `CONTEXTUAL_FILES`.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` lines 146, 206–254

## Acceptance Criteria

- [ ] Single loop over all files in `_simulate_attack`
- [ ] All file result objects have `is_contextual` field (True or False)
- [ ] `_agent_detail` uses `CONTEXTUAL_FILES` constant instead of inline literal
- [ ] Behavior identical to current (same results returned)

## Work Log

- 2026-03-11: Found by code-simplicity-reviewer in PR #2 code review
