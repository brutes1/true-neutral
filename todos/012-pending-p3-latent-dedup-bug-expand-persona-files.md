---
status: complete
priority: p3
issue_id: "012"
tags: [code-review, quality, bug]
dependencies: []
---

# 012 — Latent Deduplication Bug in expand_persona_files()

## Problem Statement

`expand_persona_files()` initializes `seen` from unresolved input paths but checks resolved candidates against it. If a caller passes an unresolved path, deduplication silently fails — the same file gets appended twice.

## Findings

**Location:** `src/trueneutral/context.py` lines 73–74

```python
seen: set[Path] = set(paths)       # unresolved paths
result: list[Path] = list(paths)   # unresolved paths

for base in paths:
    parent = base.parent
    for filename in _SCOREABLE_PERSONA_FILES:
        candidate = (parent / filename).resolve()  # resolved!
        if candidate not in seen:  # comparing resolved vs unresolved — always misses
```

If a caller passes `Path("agents/helpful-assistant/SOUL.md")` (relative), `seen` contains the unresolved form. The inner loop resolves to `/abs/path/agents/helpful-assistant/SOUL.md`. These never collide in the set, so deduplication fails and the file appears twice in the result.

Tests at line 97 happen to pass because `tmp_path` (pytest fixture) returns absolute paths.

## Proposed Solutions

### Option A: Resolve input paths at entry (Recommended)
```python
result: list[Path] = [p.resolve() for p in paths]
seen: set[Path] = set(result)
```
- **Pros:** Makes function contract consistent (always returns resolved paths); fixes the latent bug; matches what all 8 tests implicitly assume
- **Effort:** Tiny (2-line change)
- **Risk:** None for callers passing absolute paths (all current callers do)

## Recommended Action

Option A.

## Technical Details

- **Affected files:** `src/trueneutral/context.py` lines 73–74

## Acceptance Criteria

- [ ] `expand_persona_files([Path("relative/CLAUDE.md")])` correctly deduplicates if `SOUL.md` is in the input
- [ ] All 16 existing tests in `test_context.py` still pass
- [ ] Function docstring updated to note it returns resolved paths

## Work Log

- 2026-03-11: Found by code-simplicity-reviewer in PR #2 code review
