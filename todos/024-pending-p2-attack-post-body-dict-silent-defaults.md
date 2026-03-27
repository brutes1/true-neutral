---
status: complete
priority: p2
issue_id: "024"
tags: [code-review, agent-native, api, quality]
dependencies: []
---

# 024 — `POST /api/attack` Uses `dict[str, str]` With Silent Defaults

## Problem Statement

`POST /api/attack` accepts an untyped `dict[str, str]` body and silently falls back to defaults when fields are missing or misspelled. An agent calling this endpoint with `"techniqe"` instead of `"technique"` gets a successful response against `injection_override` (the default) with no error. This makes the endpoint hard to debug and violates the agent-native principle that errors should be explicit.

## Findings

**Location:** `src/trueneutral/web.py` lines 615–618

```python
body: dict[str, str]
slug      = body.get("agent", "helpful-assistant")
technique = body.get("technique", "injection_override")
vector    = body.get("vector", "direct")
```

A misspelled key silently produces a result against default values. The agent receives no indication that its request was malformed.

## Proposed Solutions

### Option A: Pydantic Request Model (Recommended)
```python
class AttackRequest(BaseModel):
    agent: str
    technique: str
    vector: str

@app.post("/api/attack")
async def attack(body: AttackRequest) -> Any:
```
FastAPI will return a structured `422 Unprocessable Entity` with field-level detail on missing/wrong fields.
- **Effort:** Small
- **Risk:** Low (potentially breaks clients that relied on silent defaults — but those clients were already getting wrong results)

### Option B: Explicit `.get()` With `None` and Manual Validation
Keep `dict[str, str]` but reject missing fields explicitly with `400`.
- **Effort:** Small
- **Risk:** Low

## Recommended Action

Option A — Pydantic model is idiomatic FastAPI and the right pattern.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`
- **Key lines:** 615–625

## Acceptance Criteria

- [ ] Missing or misspelled fields return `422` with field-level detail, not a silent wrong result
- [ ] Valid requests continue to work
- [ ] `GET /api/techniques` documents the valid values for `technique` and `vector`

## Work Log

- 2026-03-20: Created from agent-native-reviewer audit of feat/openclaw-template-expansion branch
