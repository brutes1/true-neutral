---
status: pending
priority: p1
issue_id: "016"
tags: [code-review, agent-native, api]
dependencies: []
---

# 016 — Watcher/Baseline Lifecycle Has No API Surface

## Problem Statement

The `AlignmentWatcher` and `BaselineRecord` types implement a full baseline lifecycle (first-encounter locking, drift detection, explicit baseline accept). None of this is reachable through the web API — it is CLI-only. An agent monitoring a fleet cannot know whether any file is in a drifted state, cannot accept baselines programmatically, and cannot query what baseline was last accepted. This is the largest capability gap between CLI and API.

## Findings

**Location:** `src/trueneutral/watcher.py` (`AlignmentWatcher`, `BaselineRecord`, `accept_baseline`), `src/trueneutral/cli.py` (`_run_baseline_accept`, `_run_watch`)

CLI capabilities with no API equivalent:
- `trueneutral watch` — runs watcher daemon, detects drift
- `trueneutral baseline --accept PATH` — accepts current content as new baseline
- Baseline state (what hash was last accepted for each file) — not queryable

Agent-native audit score: **0/3 watcher lifecycle operations are agent-accessible**

## Proposed Solutions

### Option A: Three New Endpoints (Recommended)
Add:
- `GET /api/agents/{slug}/baseline` — returns current baseline state per scored file (hash, accepted_at, score at acceptance)
- `POST /api/agents/{slug}/baseline/accept` — accepts current file content as new baseline for specified files
- `GET /api/agents/{slug}/drift` — returns whether any file is drifted from baseline and the axis deltas

This closes the full lifecycle gap: agents can poll for drift, inspect baselines, and accept new baselines programmatically.
- **Effort:** Medium
- **Risk:** Low

### Option B: Extend `GET /api/agents/{slug}` Response
Add `baseline` and `drift` objects to the existing agent detail response. Avoids new endpoints but bloats an already-large response.
- **Effort:** Small
- **Risk:** Low (additive change)

## Recommended Action

Option A — clean API design, aligns with the governance feature's `GET /api/agents/{slug}/rank` pattern already in the plan.

## Technical Details

- **Affected files:** `src/trueneutral/web.py`, `src/trueneutral/watcher.py`
- **Dependency:** Requires `get_baseline(path)` public method on `AlignmentWatcher` (see architecture finding C3 / todo 024)
- **Baseline data location:** `~/.claude/trueneutral-baselines.json` (loaded by `_load_baselines` in watcher.py)

## Acceptance Criteria

- [ ] `GET /api/agents/{slug}/baseline` returns baseline hash + timestamp per scored file
- [ ] `POST /api/agents/{slug}/baseline/accept` accepts baseline and updates the baselines JSON file
- [ ] `GET /api/agents/{slug}/drift` returns drift status and axis deltas vs. baseline for each file
- [ ] All three endpoints validate slug against allowlist (path traversal safe)
- [ ] Response is machine-parseable (no human-only fields)

## Work Log

- 2026-03-20: Created from agent-native-reviewer audit of feat/openclaw-template-expansion branch
