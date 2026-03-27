---
status: complete
priority: p1
issue_id: "014"
tags: [code-review, security, api]
dependencies: []
---

# 014 — Unbounded File Content Write Enables Disk Exhaustion DoS

## Problem Statement

`POST /api/agents` and `PUT /api/agents/{slug}` accept `file_contents: dict[str, Any]` with no size validation. A caller can send megabytes or gigabytes per file. Eight files are iterated — a single request with 8 × 100 MB payloads exhausts disk space or causes OOM before the OS kills the process.

## Findings

**Location:** `src/trueneutral/web.py` lines 691–700, 720–725

```python
file_contents: dict[str, str] = body.get("files", {})
# ...
(agent_dir / fname).write_text(file_contents[fname], encoding="utf-8")
```

No `Content-Length` check, no per-file size limit, no total body size limit. Combined with finding 013 (no auth), any reachable client can trigger this.

## Proposed Solutions

### Option A: Per-File Content Size Limit (Recommended)
Validate each file's content length before writing. Reject with `400` if any file exceeds the limit. Sensible limit for persona files: 512 KB per file.
- **Pros:** Simple, zero dependencies, covers both POST and PUT paths
- **Effort:** Small
- **Risk:** Low

### Option B: FastAPI `max_upload_size` Middleware
Use Starlette's `LimitUploadSize` middleware to cap the total request body.
- **Pros:** Single enforcement point, covers edge cases
- **Cons:** Rejects at the transport level before JSON parsing — less informative error
- **Effort:** Small
- **Risk:** Low

## Recommended Action

Option A — explicit per-file check with a clear error message.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`
- **Key lines:** 691–700 (`create_agent`), 720–725 (`update_agent`)

## Acceptance Criteria

- [ ] Files exceeding 512 KB return `400` with a clear error message
- [ ] Check applied in both `create_agent` and `update_agent`
- [ ] Total body limit enforced (sum of all 8 files ≤ 4 MB)

## Work Log

- 2026-03-20: Created from security-sentinel review of feat/openclaw-template-expansion branch
