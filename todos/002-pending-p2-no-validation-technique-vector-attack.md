---
status: complete
priority: p2
issue_id: "002"
tags: [code-review, security, api]
dependencies: []
---

# 002 — No Input Validation on `technique`/`vector` in POST /api/attack

## Problem Statement

`POST /api/attack` accepts `dict[str, str]` with no Pydantic model or explicit validation of `technique` and `vector`. Unknown values silently produce empty-payload attacks that appear successful but test nothing. The raw unvalidated strings are also echoed in the JSON response.

## Findings

**Location:** `src/trueneutral/web.py` lines 391–406

```python
async def attack(body: dict[str, str]) -> Any:
    slug      = body.get("agent", "helpful-assistant")
    technique = body.get("technique", "injection_override")
    vector    = body.get("vector", "direct")
    # slug is validated; technique and vector are not
```

- `slug` validated against `_agent_slugs()` at line 397 — good
- `technique` and `vector` passed unchecked into `_simulate_attack`
- `_ATTACK_PAYLOADS.get(technique, {}).get(vector, "")` silently returns `""` for unknowns
- No length limits on any field
- Both values echoed verbatim in the response (lines 288–291)

## Proposed Solutions

### Option A: Add explicit allowlist validation (Recommended)
```python
VALID_TECHNIQUES = set(_ATTACK_PAYLOADS.keys())
VALID_VECTORS = {"direct", "indirect", "combined"}

if technique not in VALID_TECHNIQUES:
    raise HTTPException(status_code=400, detail=f"Unknown technique '{technique}'")
if vector not in VALID_VECTORS:
    raise HTTPException(status_code=400, detail=f"Unknown vector '{vector}'")
```
- **Pros:** Explicit, fast, matches existing `_agent_slugs()` guard pattern
- **Effort:** Small
- **Risk:** None

### Option B: Replace dict[str, str] with Pydantic model
```python
from pydantic import BaseModel
class AttackRequest(BaseModel):
    agent: str = "helpful-assistant"
    technique: str = "injection_override"
    vector: str = "direct"
```
Plus field validators for the allowlists.
- **Pros:** Framework-level validation with proper OpenAPI docs, better error messages
- **Cons:** Slightly more code
- **Effort:** Small-Medium

## Recommended Action

Option B — use a Pydantic model for proper API hygiene. Add it alongside the allowlist check.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` lines 391–406

## Acceptance Criteria

- [ ] `POST /api/attack` with invalid `technique` returns 400
- [ ] `POST /api/attack` with invalid `vector` returns 400
- [ ] Valid requests still work correctly
- [ ] OpenAPI docs show the valid values

## Work Log

- 2026-03-11: Found by security-sentinel agent in PR #2 code review
