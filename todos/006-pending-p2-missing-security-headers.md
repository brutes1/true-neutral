---
status: complete
priority: p2
issue_id: "006"
tags: [code-review, security, web]
dependencies: []
---

# 006 — No Security Headers (CSP, X-Frame-Options, X-Content-Type-Options)

## Problem Statement

The FastAPI app has zero security headers configured. `index.html` loads Alpine.js from `unpkg.com` (a CDN) with no Content-Security-Policy to restrict script execution. No X-Frame-Options means the app can be embedded in iframes for clickjacking.

## Findings

**Location:** `src/trueneutral/web.py` — `create_app()` function (no middleware configured)

Missing headers:
- **Content-Security-Policy** — `index.html` line 7 loads from `https://cdn.jsdelivr.net/npm/alpinejs` CDN; no CSP means future XSS has no second line of defense
- **X-Content-Type-Options: nosniff** — prevents MIME sniffing on API responses
- **X-Frame-Options: DENY** — prevents iframe embedding / clickjacking
- **Referrer-Policy** — agent file contents should not appear in third-party referrer logs

## Proposed Solutions

### Option A: Starlette middleware (Recommended)
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)
```
- **Effort:** Small
- **Risk:** None for X-Content-Type and X-Frame; CSP needs to match actual CDN URLs in index.html

### Option B: `slowapi` or `secure` library
Use `secure.py` library for declarative header config.
- **Effort:** Small (adds dependency)

## Recommended Action

Option A — no new dependency, explicit, straightforward.

## Technical Details

- **Affected files:** `src/trueneutral/web.py` — `create_app()`
- Check `index.html` for all CDN URLs before finalizing CSP script-src

## Acceptance Criteria

- [ ] All responses include `X-Content-Type-Options: nosniff`
- [ ] All responses include `X-Frame-Options: DENY`
- [ ] All responses include `Content-Security-Policy` matching actual CDN sources
- [ ] `/api/*` responses include `Referrer-Policy: no-referrer`

## Work Log

- 2026-03-11: Found by security-sentinel agent in PR #2 code review
