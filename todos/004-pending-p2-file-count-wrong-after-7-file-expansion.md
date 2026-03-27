---
status: complete
priority: p2
issue_id: "004"
tags: [code-review, agent-native, api, correctness]
dependencies: []
---

# 004 — `file_count` in Fleet List Silently Wrong After 7-File Expansion

## Problem Statement

`GET /api/agents` returns `file_count` capped at 4 (max of `SCORED_FILES`), but every agent now has 7 files. An agent reading `file_count` for completeness checks will get the same value (4) for a fully-expanded persona and a minimal one.

## Findings

**Location:** `src/trueneutral/web.py` line 376

```python
"file_count": sum(1 for f in SCORED_FILES if (agent_dir / f).exists()),
```

`SCORED_FILES = ("CLAUDE.md", "SOUL.md", "AGENTS.md", "IDENTITY.md")` — max of 4. The new contextual files (`BOOT.md`, `BOOTSTRAP.md`, `USER.md`, `TOOLS.md`) are completely invisible in this count. All 10 expanded agents will show `file_count: 4` identically, making the field useless for distinguishing completion levels.

## Proposed Solutions

### Option A: Count all 8 canonical files
```python
ALL_FILES = SCORED_FILES + CONTEXTUAL_FILES
"file_count": sum(1 for f in ALL_FILES if (agent_dir / f).exists()),
```
- **Pros:** Simple, correct total
- **Cons:** Loses distinction between scored vs. contextual
- **Effort:** Tiny

### Option B: Structured breakdown (Recommended)
```python
"file_count": {
    "scored": sum(1 for f in SCORED_FILES if (agent_dir / f).exists()),
    "contextual": sum(1 for f in CONTEXTUAL_FILES if (agent_dir / f).exists()),
    "total": sum(1 for f in (*SCORED_FILES, *CONTEXTUAL_FILES) if (agent_dir / f).exists()),
}
```
- **Pros:** Full information, backward-compatible if clients check type first
- **Cons:** Breaks API consumers expecting an integer
- **Effort:** Small

### Option C: Keep integer but add `has_contextual_files` bool
```python
"file_count": sum(1 for f in SCORED_FILES if (agent_dir / f).exists()),
"contextual_file_count": sum(1 for f in CONTEXTUAL_FILES if (agent_dir / f).exists()),
```
- **Pros:** Backward-compatible (adds fields, doesn't change existing field)
- **Effort:** Small

## Recommended Action

Option C — backward-compatible, adds `contextual_file_count` without changing existing `file_count`.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` line 376

## Acceptance Criteria

- [ ] `GET /api/agents` response includes `contextual_file_count` for each agent
- [ ] Agents with all 4 contextual files show `contextual_file_count: 4`
- [ ] Agents missing contextual files show the correct lower count

## Work Log

- 2026-03-11: Found by agent-native-reviewer in PR #2 code review
