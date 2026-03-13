---
status: complete
priority: p3
issue_id: "010"
tags: [code-review, architecture, deployment]
dependencies: []
---

# 010 — AGENTS_DIR Path Resolution Breaks When Package Is Installed

## Problem Statement

`AGENTS_DIR` is computed by navigating three directories up from `__file__`. This works in a development checkout but produces a wrong path when the package is installed into a virtualenv's `site-packages`, rendering the entire web UI empty with no error.

## Findings

**Location:** `src/trueneutral/web.py` line 18

```python
AGENTS_DIR = Path(__file__).parent.parent.parent / "agents"
# = src/trueneutral/web.py → src/trueneutral/ → src/ → project root → agents/
```

When installed: `__file__` is inside `<venv>/lib/python3.x/site-packages/trueneutral/web.py`. Three levels up is `<venv>/lib/python3.x/`, not the project root. `AGENTS_DIR.exists()` returns False, `_agent_slugs()` returns `[]`, and the UI silently shows no agents.

The failure mode is silent — `_agent_slugs()` already has `if not AGENTS_DIR.exists(): return []` at line 90–91.

Contrast with `STATIC_DIR = Path(__file__).parent / "static"` — correct because static assets are package data.

## Proposed Solutions

### Option A: Environment variable with development fallback (Recommended)
```python
import os
_default_agents = Path(__file__).parent.parent.parent / "agents"
AGENTS_DIR = Path(os.environ.get("TRUENEUTRAL_AGENTS_DIR", _default_agents))
```
- **Pros:** Works in all deployment contexts; dev experience unchanged
- **Effort:** Small

### Option B: Accept agents_dir in run_server() and create_app()
```python
def create_app(agents_dir: Path | None = None) -> Any:
    global AGENTS_DIR
    if agents_dir:
        AGENTS_DIR = agents_dir
```
- **Pros:** Programmatic configuration
- **Cons:** Global mutation is messy; env var is simpler

### Option C: Fail loudly on startup if AGENTS_DIR doesn't exist
Add a check at module import time that raises `RuntimeError` with a helpful message.
- **Pros:** Fast feedback instead of silent empty UI
- **Effort:** Tiny (complementary to A or B)

## Recommended Action

Option A + Option C: env var override + startup assertion with clear error message.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` line 18

## Acceptance Criteria

- [ ] `TRUENEUTRAL_AGENTS_DIR` env var overrides the default path
- [ ] Missing `AGENTS_DIR` raises `RuntimeError` with actionable message at app startup
- [ ] Dev workflow (checkout-based) unchanged

## Work Log

- 2026-03-11: Found by architecture-strategist agent in PR #2 code review
