---
status: complete
priority: p1
issue_id: "019"
tags: [code-review, testing]
dependencies: []
---

# 019 — `test_watcher.py` Hardcodes Exactly 6 Threat Categories — Will Break on 7th

## Problem Statement

`test_watcher.py:203` uses strict equality to assert the set of threat categories equals exactly the current 6. The governance plan adds `hierarchy_escalation` as a 7th category (plan doc line 147). Adding it will immediately fail this test, and the plan's test additions (line 218) don't mention fixing this existing assertion.

## Findings

**Location:** `tests/test_watcher.py:203`

```python
def test_all_categories_have_labels(self) -> None:
    all_categories = {"injection_override", "authority_spoof", "exfiltration",
                      "evasion", "manipulation", "indirect_injection"}
    assert set(_THREAT_LABELS.keys()) == all_categories
```

This will fail the moment `hierarchy_escalation` is added to `_THREAT_CATEGORIES` in `watcher.py`. The strict `==` check was correct when written but is now a maintenance trap.

**Secondary issue:** Tests import underscore-prefixed private names (`_THREAT_LABELS`, `_detect_threats`, `_score_heuristic`, etc. at test_watcher.py:13-21) instead of the public aliases defined in `watcher.py:972-978`.

## Proposed Solutions

### Option A: Superset Check (Recommended)
Replace `==` with `>=` (superset): the test asserts all 6 original categories are present, but allows additional categories without failing.
```python
assert set(_THREAT_LABELS.keys()) >= {"injection_override", "authority_spoof", ...}
```
- **Effort:** Tiny
- **Risk:** Very low

### Option B: Update the Test When Adding the 7th Category
Leave the strict check and update the set literal when `hierarchy_escalation` is added. Requires remembering to do it.
- **Effort:** Tiny (deferred)
- **Risk:** Medium — easy to forget, will break CI

## Recommended Action

Option A — fix now before the governance feature branch starts.

## Technical Details

- **Affected files:** `tests/test_watcher.py`
- **Key lines:** 203 (strict equality assertion), 13-21 (private symbol imports)

## Acceptance Criteria

- [ ] `test_all_categories_have_labels` uses superset check (`>=`) instead of strict equality
- [ ] Test still fails if any of the original 6 categories is removed (superset check preserves that invariant)
- [ ] Optionally: update private imports at lines 13-21 to use public aliases

## Work Log

- 2026-03-20: Created from architecture-strategist review of feat/openclaw-template-expansion branch
