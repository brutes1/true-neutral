---
status: complete
priority: p1
issue_id: "013"
tags: [code-review, security]
dependencies: []
---

# 013 — No Authentication on Mutating Endpoints

## Problem Statement

`POST /api/agents`, `PUT /api/agents/{slug}`, and `DELETE /api/agents/{slug}` are completely unauthenticated. Any client that can reach the server port can create, overwrite, or delete agent configuration files on disk. The server defaults to `127.0.0.1` (line 751), but a single SSRF, shared-host scenario, or `0.0.0.0` deployment turns this into a full remote write primitive.

## Findings

**Location:** `src/trueneutral/web.py` lines 670–746 (all three mutating route handlers)

- `POST /api/agents` (line 670): creates agent directory and writes 8 files with no auth
- `PUT /api/agents/{slug}` (line 710): overwrites any file in an agent dir with no auth
- `DELETE /api/agents/{slug}` (line 727): removes entire agent directory with no auth
- Default bind at line 751: `host="127.0.0.1"` — only safeguard, easily bypassed

Impact: Any network-reachable client can corrupt the entire fleet dataset.

## Proposed Solutions

### Option A: Configurable API Key Header (Recommended)
Add middleware that checks `Authorization: Bearer <token>` on all state-mutating routes. Token configured via `TRUENEUTRAL_API_KEY` environment variable. If env var is unset, mutating routes return `403` with a message directing the user to set the variable for write access. Read endpoints (`GET`) remain unauthenticated.
- **Pros:** Simple, stateless, no new dependencies, consistent with CLI-adjacent tools
- **Cons:** Bearer token in env var is less secure than session-based auth
- **Effort:** Small
- **Risk:** Low

### Option B: CLI-Only Writes (No Write API)
Remove `POST`, `PUT`, `DELETE` endpoints entirely; all agent management goes through the CLI. The web API becomes read-only.
- **Pros:** Eliminates the attack surface completely; web UI becomes a viewer
- **Cons:** Breaks the manage tab in the SPA; requires UI redesign
- **Effort:** Small (backend) + Medium (frontend)
- **Risk:** Low

### Option C: Session-Based Auth
Add a `/api/auth/login` endpoint with username/password, issue a signed JWT, and require it on mutating routes.
- **Pros:** Proper auth, extensible for multi-user
- **Cons:** Requires user/password storage, new dependencies, over-engineered for a local tool
- **Effort:** Large
- **Risk:** Medium

## Recommended Action

Option A — minimal API key check on mutating routes, read endpoints stay open.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`
- **Key lines:** 670–746 (route handlers), 551–570 (`create_app`), 751 (bind host)

## Acceptance Criteria

- [ ] All `POST`, `PUT`, `DELETE` routes return `403` without a valid auth token
- [ ] Token configurable via `TRUENEUTRAL_API_KEY` environment variable
- [ ] `GET` endpoints remain unauthenticated
- [ ] Error message explains how to configure the key
- [ ] Auth check implemented once (middleware or dependency), not per-route

## Work Log

- 2026-03-20: Created from security-sentinel review of feat/openclaw-template-expansion branch
