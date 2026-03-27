---
status: pending
priority: p2
issue_id: "020"
tags: [code-review, security, web]
dependencies: []
---

# 020 — CSP Uses `unsafe-inline` and `unsafe-eval`

## Problem Statement

The Content-Security-Policy header allows `'unsafe-inline'` and `'unsafe-eval'` in `script-src`, rendering it largely ineffective against XSS. The CDN allowlist (`unpkg.com`, `cdn.jsdelivr.net`) also widens the attack surface — both are publicly writable registries where a dependency confusion or typosquat attack could serve malicious scripts from an allowed origin.

## Findings

**Location:** `src/trueneutral/web.py` lines 562–564

```python
"script-src 'self' https://unpkg.com https://cdn.jsdelivr.net 'unsafe-inline' 'unsafe-eval'; "
"style-src 'self' 'unsafe-inline'"
```

`'unsafe-inline'` + `'unsafe-eval'` make the CSP header decorative. If any endpoint ever reflects user-controlled content into HTML, there is no XSS second line of defense. Alpine.js is the source of `'unsafe-eval'` (it uses `Function()` construction internally).

## Proposed Solutions

### Option A: Pin Alpine.js to SRI Hash and Remove unsafe-eval
Pin the specific Alpine.js CDN version with a `<script integrity="sha256-...">` attribute. Some Alpine.js versions support a CSP-compatible build that avoids `eval()`. Switch to that build.
- **Pros:** Eliminates both `unsafe-inline` and `unsafe-eval` concerns
- **Cons:** Requires pinning to a specific CDN version, build process change
- **Effort:** Medium

### Option B: Move Alpine.js to Self-Hosted Static File
Bundle Alpine.js into `src/trueneutral/static/` alongside `index.html`. Remove CDN dependency entirely. Use a nonce for any remaining inline scripts.
- **Pros:** Eliminates CDN risk, enables strict `script-src 'self'`
- **Cons:** Requires bundling Alpine.js (small file, one-time task)
- **Effort:** Small
- **Risk:** Low

### Option C: Document as Known Limitation (Minimal)
Add a comment noting the `unsafe-inline`/`unsafe-eval` is required for Alpine.js and is acceptable for a local development tool.
- **Effort:** Tiny
- **Risk:** Low (acknowledges, doesn't fix)

## Recommended Action

Option B — self-host Alpine.js, enables strict CSP.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`, `src/trueneutral/static/index.html`
- **Key lines:** 562–564 (CSP header), 7 (CDN script tag in index.html)

## Acceptance Criteria

- [ ] `'unsafe-inline'` removed from `script-src`
- [ ] CDN dependency removed or replaced with SRI-pinned self-hosted copy
- [ ] CSP passes Mozilla Observatory or equivalent basic check

## Work Log

- 2026-03-20: Created from security-sentinel review of feat/openclaw-template-expansion branch
