---
status: complete
priority: p3
issue_id: "027"
tags: [code-review, agent-native, frontend, quality]
dependencies: []
---

# 027 — Frontend `fetch()` Calls Missing `r.ok` Error Checks

## Problem Statement

Several Alpine.js fetch calls use `try/finally` without checking `r.ok`, so HTTP error responses (4xx/5xx) are parsed as data and silently produce wrong state. The `saveAgent()` function already does this correctly — the other callers should follow the same pattern.

## Findings

**Location:** `src/trueneutral/static/index.html`

Affected fetch calls without `r.ok` check:
- `runAttack()` (line ~1584): a `400` from invalid technique → `this.attackResult` set to `{ detail: "..." }` error JSON silently
- `loadMatrix()` (line ~1617): a 404 for bad slug → `matrixResult` silently corrupted
- `loadAttackPaths()` (line ~1567): same pattern

`saveAgent()` does it correctly:
```javascript
if (!r.ok) {
    this.manageError = d.detail || 'Save failed';
    return;
}
```

## Proposed Solutions

### Option A: Add `r.ok` Check to All Three Callers
For each of the three affected fetch calls:
```javascript
if (!r.ok) {
    this.errorMessage = d.detail || 'Request failed';
    return;
}
```
Each function already has appropriate state variables for displaying errors.
- **Effort:** Small
- **Risk:** Very low

## Recommended Action

Option A.

## Technical Details

- **Affected files:** `src/trueneutral/static/index.html`
- **Key lines:** ~1567 (loadAttackPaths), ~1584 (runAttack), ~1617 (loadMatrix)

## Acceptance Criteria

- [ ] `runAttack()`, `loadMatrix()`, `loadAttackPaths()` all check `r.ok` before parsing response
- [ ] Error detail surfaced to UI state variable
- [ ] Successful requests unaffected

## Work Log

- 2026-03-20: Created from agent-native-reviewer audit of feat/openclaw-template-expansion branch
