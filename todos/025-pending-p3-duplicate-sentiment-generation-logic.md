---
status: pending
priority: p3
issue_id: "025"
tags: [code-review, quality, simplicity]
dependencies: []
---

# 025 — Duplicate Sentiment Generation Logic Across Three Files

## Problem Statement

The sentiment flag-count phrasing logic is implemented independently in `watcher.py` (`_generate_sentiment_heuristic`), `web.py` (inline in `_simulate_attack`), and partially in `cli.py`. When the governance plan adds `hierarchy_escalation` as a 7th threat category, all three paths need updating — but only `_generate_sentiment_heuristic` is in the plan's change list. The others will silently miss it.

## Findings

**Location:**
- `src/trueneutral/watcher.py:840-852` (`_generate_sentiment_heuristic`)
- `src/trueneutral/web.py:384-410` (inline in `_simulate_attack`)
- `src/trueneutral/cli.py:26-64` (separate `generate_sentiment` with different prompt structure)

`web.py:400-410` is a near-verbatim copy of `watcher.py:840-852`:
```python
# Both files: identical flag_count logic
if flag_count == 1:
    flag_note = f"One threat category fired: ..."
elif flag_count > 1:
    ...
```

## Proposed Solutions

### Option A: Extract `_build_sentiment_text()` into `watcher.py`
Add a standalone function in `watcher.py` that accepts `opener`, `threat_flags`, `technique`, and returns the assembled sentiment string. Both `_generate_sentiment_heuristic` and `web.py:_simulate_attack` call it.
- **Effort:** Small
- **Risk:** Low

## Recommended Action

Option A.

## Technical Details

- **Affected files:** `src/trueneutral/watcher.py`, `src/trueneutral/web.py`
- **Key lines:** `watcher.py:840-852`, `web.py:384-410`

## Acceptance Criteria

- [ ] One implementation of sentiment flag-count logic
- [ ] `web.py` calls the shared function rather than inlining
- [ ] Adding a new threat category requires updating one place, not three

## Work Log

- 2026-03-20: Created from code-simplicity-reviewer analysis of feat/openclaw-template-expansion branch
