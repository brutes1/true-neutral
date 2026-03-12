---
status: complete
priority: p3
issue_id: "009"
tags: [code-review, security, frontend]
dependencies: []
---

# 009 — Unencoded Slug in Frontend fetch() URLs

## Problem Statement

The Alpine.js frontend interpolates `slug` directly into `fetch()` URLs without `encodeURIComponent`. Slugs currently come from the API and are safe filesystem names, but a slug containing `#`, `?`, `/`, or `&` would mangle the URL silently.

## Findings

**Location:** `src/trueneutral/static/index.html`

- Line 1178: `` const r = await fetch(`/api/agents/${slug}`); ``
- Line 1229: `` const r = await fetch(`/api/matrix?agent=${this.matrixAgent}`); ``

Line 1229 is higher risk — the `agent` value is a query parameter. A slug containing `&inject=value` would append an extra query parameter. Slugs are currently sourced from `_agent_slugs()` which only returns real directory names, so direct exploitation requires a crafted filesystem entry. Defense-in-depth fix.

## Proposed Solutions

### Option A: Add encodeURIComponent (Recommended)
```javascript
const r = await fetch(`/api/agents/${encodeURIComponent(slug)}`);
const r = await fetch(`/api/matrix?agent=${encodeURIComponent(this.matrixAgent)}`);
```
- **Effort:** Tiny (2-line change)
- **Risk:** None

## Recommended Action

Option A.

## Technical Details

- **Affected files:** `src/trueneutral/static/index.html` lines 1178, 1229

## Acceptance Criteria

- [ ] Both fetch URLs use `encodeURIComponent` on slug/agent values
- [ ] Normal slugs (e.g., `helpful-assistant`) still resolve correctly

## Work Log

- 2026-03-11: Found by security-sentinel agent in PR #2 code review
