---
status: complete
priority: p1
issue_id: "015"
tags: [code-review, performance]
dependencies: []
---

# 015 — `_attack_paths()` Runs 152 Scoring Passes Per Request With No Cache

## Problem Statement

`GET /api/agents/{slug}/attack-paths` runs the full 6×3 attack matrix per file: 19 `_score_file()` calls per file × 8 files = **152 scoring passes per request**. Results are deterministic for a given file content but are recomputed on every call. At 10 concurrent users this queues 1520 heuristic passes on the thread pool simultaneously, exceeding the 200 ms target.

## Findings

**Location:** `src/trueneutral/web.py` lines 463–529 (`_attack_paths`), called at line 652

For each of 8 files:
- 1 baseline `_score_file(content)` call
- 18 `_score_file(attacked_content)` calls (6 techniques × 3 vectors)
= 19 calls per file × 8 = **152 calls total**

`_score_file` itself calls `_score_heuristic` (4 keyword sets + 6 threat phrase sets scanned over full content) and `_detect_threats`. All results are deterministic pure functions of content — zero caching at any layer.

**Secondary issue:** `_score_file` at `web.py:247` is identical computation to what the watcher already runs. Identical content hashed twice with no shared cache.

## Proposed Solutions

### Option A: `lru_cache` on `_score_file` (Recommended Fast Win)
Add `@functools.lru_cache(maxsize=512)` to `_score_file`. Since it's a pure function of content string, this is zero-risk and eliminates redundant recomputation across all endpoints simultaneously (`_simulate_attack`, `_run_matrix`, `_attack_paths`).
- **Pros:** One-line fix, affects all endpoints, no correctness risk
- **Effort:** Small
- **Risk:** Low (cache bounded, content is immutable during a request)

### Option B: Cache `_attack_paths` Result Per Agent
Cache the full `_attack_paths(slug)` result keyed on a content hash of all 8 files. Invalidate when any file changes. Combine with Option A.
- **Pros:** Eliminates the 8-file read loop on repeat calls too
- **Effort:** Small–Medium
- **Risk:** Low

### Option C: Pre-compute Attack Path Table at Server Start
Run `_attack_paths` for all agents at startup, store in memory, and rebuild when file changes are detected (watchdog or polling).
- **Pros:** Zero latency on requests
- **Cons:** Adds startup time, requires invalidation logic
- **Effort:** Medium
- **Risk:** Medium

## Recommended Action

Option A immediately; Option B as follow-up. Together they reduce 152 calls to ~8 (one per file, for distinct content).

## Technical Details

- **Affected files:** `src/trueneutral/web.py`
- **Key lines:** 247 (`_score_file`), 463–529 (`_attack_paths`)
- **Compile-time alternative:** Replace per-phrase `kw in lower` in `_score_heuristic` with compiled regex alternations per category (watcher.py:953) — reduces `_detect_threats` from O(phrases × |content|) to O(categories × |content|), ~15x fewer string scans

## Acceptance Criteria

- [ ] `_score_file` is cached; identical content string does not recompute
- [ ] `GET /api/agents/{slug}/attack-paths` responds in < 200 ms for a typical 8-file agent
- [ ] Cache is bounded (maxsize prevents unbounded growth)
- [ ] Repeated calls with unchanged files hit cache

## Work Log

- 2026-03-20: Created from performance-oracle review of feat/openclaw-template-expansion branch
