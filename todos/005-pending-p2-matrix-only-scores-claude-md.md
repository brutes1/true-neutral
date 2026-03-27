---
status: complete
priority: p2
issue_id: "005"
tags: [code-review, agent-native, api, correctness]
dependencies: []
---

# 005 — GET /api/matrix Scores Only CLAUDE.md, Ignores New Scored Files

## Problem Statement

`GET /api/matrix` runs the 6×3 attack matrix against only `CLAUDE.md`. After this PR, the watcher also scores `SOUL.md`, `AGENTS.md`, and `IDENTITY.md`. An automated pipeline using the matrix endpoint would miss drift in 3 of 4 scored files.

## Findings

**Location:** `src/trueneutral/web.py` line 307

```python
claude_content = _read_file(agent_dir / "CLAUDE.md")
baseline = _score_file(claude_content)
```

The matrix loop (lines 311–327) runs 18 combinations but only ever modifies `claude_content`. If a `SOUL.md` or `AGENTS.md` file is more vulnerable to certain attack vectors than `CLAUDE.md`, the matrix is blind to it.

## Proposed Solutions

### Option A: Add `file` query parameter (Recommended)
```python
@app.get("/api/matrix")
async def matrix(agent: str = "helpful-assistant", file: str = "CLAUDE.md") -> Any:
    valid_files = set(SCORED_FILES)
    if file not in valid_files:
        raise HTTPException(400, detail=f"file must be one of {sorted(valid_files)}")
    content = _read_file(agent_dir / file)
```
- **Pros:** Non-breaking, lets callers sweep all 4 files, documents the limitation explicitly
- **Cons:** Requires 4 calls to get full picture
- **Effort:** Small

### Option B: Return per-file matrix results
Run the matrix for each of the 4 `SCORED_FILES` and return `{file: cells}` structure.
- **Pros:** One call gives the complete picture
- **Cons:** 4× more computation per request (72 scoring operations vs 18); breaking API change
- **Effort:** Medium

### Option C: Add a `files` multi-value query param
`GET /api/matrix?agent=foo&files=CLAUDE.md&files=SOUL.md`
- **Pros:** Flexible; callers choose which files to include
- **Effort:** Medium

## Recommended Action

Option A for now — non-breaking addition that unlocks the full surface for automated callers.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` lines 298–335

## Acceptance Criteria

- [ ] `GET /api/matrix?agent=helpful-assistant&file=SOUL.md` returns matrix for SOUL.md
- [ ] Default `file=CLAUDE.md` behavior unchanged
- [ ] Invalid `file` value returns 400

## Work Log

- 2026-03-11: Found by agent-native-reviewer in PR #2 code review
