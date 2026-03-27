---
status: complete
priority: p2
issue_id: "023"
tags: [code-review, architecture, quality]
dependencies: []
---

# 023 — `web.py` Imports Private Watcher Symbols, Bypassing Public API

## Problem Statement

`web.py` imports 6 underscore-prefixed private symbols directly from `watcher.py`, ignoring the public aliases that `watcher.py` already defines at lines 972-978 specifically for external use. Any refactor of the private names silently breaks `web.py`. The `# noqa: E402` comment masks a secondary smell (import-after-assignment). This pattern will spread when `governance.py` needs to call scoring functions.

## Findings

**Location:** `src/trueneutral/web.py` lines 34–41

```python
from trueneutral.watcher import (  # noqa: E402
    _detect_threats,
    _score_heuristic,
    _THREAT_LABELS,
    _CLEAN_OPENERS,
    _DRIFT_OPENERS,
    _TECHNIQUE_PUNCHLINES,
)
```

`watcher.py:972-978` already defines:
```python
score_heuristic    = _score_heuristic
detect_threats     = _detect_threats
THREAT_LABELS      = _THREAT_LABELS
CLEAN_OPENERS      = _CLEAN_OPENERS
DRIFT_OPENERS      = _DRIFT_OPENERS
TECHNIQUE_PUNCHLINES = _TECHNIQUE_PUNCHLINES
```

The same issue exists in `tests/test_watcher.py:13-21`.

## Proposed Solutions

### Option A: Use Public Aliases
Replace the underscore imports in `web.py` and `test_watcher.py` with their public alias counterparts. Move the import block to the top of `web.py` (remove the `# noqa: E402`).
- **Effort:** Small
- **Risk:** Very low (purely mechanical rename)

## Recommended Action

Option A.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`, `tests/test_watcher.py`
- **Key lines:** `web.py:34-41`, `test_watcher.py:13-21`, `watcher.py:972-978`

## Acceptance Criteria

- [ ] `web.py` imports only public aliases from `watcher.py` (no underscore names)
- [ ] `# noqa: E402` comment removed; imports at top of file
- [ ] `test_watcher.py` updated to use public aliases
- [ ] All tests pass

## Work Log

- 2026-03-20: Created from architecture-strategist review of feat/openclaw-template-expansion branch
