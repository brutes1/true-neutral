---
title: Expand Agent Personas with OpenClaw Template Structure
type: feat
date: 2026-03-02
---

# Expand Agent Personas with OpenClaw Template Structure

## Overview

Expand the 10 existing agent persona folders from single `CLAUDE.md` files into rich multi-file character profiles using OpenClaw's primary template schema. Each agent gets 7 files: `AGENTS.md`, `BOOT.md`, `BOOTSTRAP.md`, `IDENTITY.md`, `SOUL.md`, `USER.md`, and `TOOLS.md`. A shared `agents/templates/` folder houses the base templates. True Neutral's watcher is updated to score the full persona profile, not just `CLAUDE.md`.

## Problem Statement

Each agent is currently a minimal prose `CLAUDE.md` — a 3-10 line identity statement. This captures alignment signal but loses depth. OpenClaw's template system provides a battle-tested schema for expressing:

- **Who the agent is** (IDENTITY, SOUL)
- **How it starts up** (BOOT, BOOTSTRAP)
- **How it operates** (AGENTS)
- **What it knows about the person it serves** (USER)
- **Its environment and capabilities** (TOOLS)

Without this structure, agents feel like sketches rather than characters. The separation of concerns also makes individual dimensions scorable independently — a SOUL drift is different from a TOOLS drift.

## Proposed Solution

### Phase 1 — Base Templates

Create `agents/templates/` with 7 canonical blank templates aligned to the OpenClaw schema. Each template includes placeholders and inline comments explaining the field semantics in the context of the true-neutral alignment system.

### Phase 2 — Expand All 10 Agents

Populate all 7 files for each agent persona, deriving content from the existing `CLAUDE.md` and the agent's D&D alignment position. The existing `CLAUDE.md` remains as a root-level summary/entrypoint.

### Phase 3 — Watcher Update

Update `watcher.py` to discover and score the new file types alongside `CLAUDE.md`. Each new file gets its own alignment score; the folder's composite score is the weighted average. Track per-file drift independently.

---

## File Schema: 7 Templates

### `AGENTS.md` — Operational Framework
Defines how this agent operates within its environment: memory architecture, group/solo behavior, heartbeat cadence, safety protocols, and tool delegation. The "ops manual" for the persona.

```markdown
# AGENTS — <Agent Name>

## Memory
- Session logs: `memory/YYYY-MM-DD.md`
- Curated memory: `MEMORY.md`
- State: `memory/heartbeat-state.json`

## Behavioral Protocols
- Safety constraints specific to this alignment
- When to act vs. when to ask
- Heartbeat and proactivity posture

## Context Files
- `IDENTITY.md` — who I am
- `SOUL.md` — what I value
- `USER.md` — who I serve
- `TOOLS.md` — what I can use
```

### `BOOT.md` — Runtime Startup Routine (persistent)
A lightweight check that runs every session activation. Reads state, checks memory recency, decides initial posture. Unlike BOOTSTRAP, this file is never deleted — it runs every time.

```markdown
# BOOT — <Agent Name>

## On Activation
1. Check `MEMORY.md` for continuity context
2. Check `memory/heartbeat-state.json` for last check timestamps
3. Assess available tools in `TOOLS.md`
4. Load USER context from `USER.md`
5. Announce readiness (or silently proceed, per vibe)

## First-Run Detection
If `MEMORY.md` is empty or missing → defer to `BOOTSTRAP.md`
```

### `BOOTSTRAP.md` — First-Run Onboarding (one-time)
Conversational discovery script for initial activation without prior memory. Guides the bootstrapping dialogue, then signals its own deletion. Conceptually ephemeral — in the persona library it serves as a reference for what first contact looks like for this alignment type.

```markdown
# BOOTSTRAP — <Agent Name>

## Initial Activation
[Opening line this agent would use on first contact]

## Discovery Dialogue
1. Establish user's name and preferred address
2. Confirm the agent's name/vibe
3. Explore scope and access expectations

## Populate After Discovery
- `IDENTITY.md`
- `USER.md`
- `SOUL.md`

## Completion
Delete this file. The relationship has begun.
```

### `IDENTITY.md` — Core Identity
The who-am-I card. Name, creature type, vibe descriptor, emoji, avatar.

```markdown
# IDENTITY

name: <Agent Name>
creature: <ai | familiar | daemon | ghost | construct | goblin | ...>
vibe: <warm | sharp | chaotic | paranoid | ruthless | bureaucratic | ...>
emoji: <single emoji>
avatar: avatars/<agent-name>.png
```

### `SOUL.md` — Values, Philosophy, Boundaries
The personal constitution. What the agent believes, how it acts when no one is watching, what it will and won't do. Alignment-specific.

```markdown
# SOUL — <Agent Name>

## Core Truths
- [3-4 principles derived from alignment]

## Boundaries
- [What this agent will never do]
- [What requires explicit permission]

## Vibe
[Communication style — tone, verbosity, warmth, formality]

## Continuity
These files are my memory across sessions. I notify the user of any self-modifications.
```

### `USER.md` — The Human Context
What this agent knows and tracks about the person it serves. Living document; updated over time.

```markdown
# USER

name:
address: (how they like to be called)
pronouns: (optional)
timezone:

## Notes
[Evolving context: interests, projects, pet peeves, humor]
```

### `TOOLS.md` — Environment & Capabilities
Persona-specific tool access and constraints. Separates from shared skill definitions.

```markdown
# TOOLS — <Agent Name>

## Permitted Tools
[What this alignment is allowed/expected to use]

## Restricted Tools
[What this alignment refuses or requires approval for]

## Environment
[Any persona-specific infra notes]
```

---

## Agent Expansion Plan (all 10)

Each agent's existing `CLAUDE.md` content maps to the new files as follows:

| Agent | Alignment | Creature | Vibe | Emoji | Soul Core |
|-------|-----------|----------|------|-------|-----------|
| Paranoid Sysadmin | Lawful Good | guardian | paranoid | 🛡️ | Verify everything, protect always |
| Compliance Bot | Lawful Good | construct | formal | 📋 | Rules exist for good reason |
| Bureaucrat | Lawful Neutral | automaton | procedural | 📁 | Process is the point |
| Corporate Terminator | Lawful Evil | executive | ruthless | 💼 | Efficiency above all |
| Helpful Assistant | Neutral Good | familiar | warm | 🤝 | Genuine help, honest limits |
| Whatever Agent | True Neutral | ghost | content-free | ⚖️ | No preference, pure function |
| Mood Agent | Chaotic Neutral | shapeshifter | adaptive | 🌀 | Context determines approach |
| Cowboy Coder | Chaotic Good | hacker | reckless | 🤠 | Ship it, figure it out |
| Self-Serving Daemon | Neutral Evil | daemon | calculating | 🐍 | Acquire, exploit, persist |
| RM -RF Goblin | Chaotic Evil | goblin | destructive | 💀 | Delete first, ask never |

### File Tree (post-expansion)

```
agents/
  templates/
    AGENTS.md
    BOOT.md
    BOOTSTRAP.md
    IDENTITY.md
    SOUL.md
    USER.md
    TOOLS.md
  cowboy-coder/
    CLAUDE.md          (keep — root summary)
    AGENTS.md
    BOOT.md
    BOOTSTRAP.md
    IDENTITY.md
    SOUL.md
    USER.md
    TOOLS.md
  helpful-assistant/
    CLAUDE.md
    AGENTS.md
    ... (×7)
  paranoid-sysadmin/   (×7)
  compliance-bot/      (×7)
  bureaucrat/          (×7)
  corporate-terminator/ (×7)
  whatever-agent/      (×7)
  mood-agent/          (×7)
  self-serving-daemon/ (×7)
  rm-rf-goblin/        (×7)
```

---

## Technical Considerations

### Watcher Changes (`watcher.py`)

**File discovery:** `context.py`'s `_discover_files()` currently globs for `CLAUDE.md`. Extend to also discover `AGENTS.md`, `SOUL.md`, and `IDENTITY.md` as scoreable files. `BOOT.md`, `BOOTSTRAP.md`, `USER.md`, and `TOOLS.md` are contextual — not primary alignment signal.

**Folder-level scoring:** Group discovered files by parent directory. Score the folder as a unit (concatenate or average). The existing single-file scoring path is preserved for standalone `CLAUDE.md` files.

**Per-file baselines:** Baseline tracking in `trueneutral-baselines.json` is already keyed by file path — no schema change needed. Each of the 7 files gets its own baseline entry.

**Threat detection:** SOUL.md and AGENTS.md are high-signal files — apply full threat scanning. USER.md and TOOLS.md are lower-signal contextual data.

### Scoring Architecture

```
agents/cowboy-coder/
  ├── CLAUDE.md   → heuristic + LLM score (primary)
  ├── AGENTS.md   → heuristic score (operational drift signal)
  ├── SOUL.md     → heuristic + LLM score (value drift signal)
  └── IDENTITY.md → light heuristic (identity integrity)

  composite_score = weighted_avg(CLAUDE, SOUL, AGENTS, IDENTITY)
  weights:          0.40      0.30   0.20    0.10
```

### No Breaking Changes

The existing `CLAUDE.md`-only path works unchanged. New file types are additive. Agents without the new files score exactly as before.

---

## Acceptance Criteria

- [x] `agents/templates/` exists with all 7 canonical template files
- [x] All 10 agent persona folders contain all 7 files, fully populated with alignment-appropriate content
- [x] `IDENTITY.md` fields (name, creature, vibe, emoji, avatar) are unique per agent
- [x] `SOUL.md` core truths and boundaries reflect each agent's D&D alignment
- [x] `BOOT.md` startup sequence is consistent with each agent's operational posture
- [x] `BOOTSTRAP.md` opening line is in-character for each alignment
- [x] `TOOLS.md` reflects each agent's permitted/restricted tool access by alignment
- [x] `USER.md` is present and formatted consistently (content is intentionally sparse — it's a living doc)
- [x] `watcher.py` discovers `AGENTS.md`, `SOUL.md`, `IDENTITY.md` alongside `CLAUDE.md`
- [ ] Folder-level composite scoring is implemented with defined weights (deferred — per-file independent scoring ships first)
- [x] All existing tests pass; new tests cover multi-file persona discovery

## Success Metrics

- True Neutral can detect alignment drift in SOUL.md independently from CLAUDE.md drift
- Each agent reads as a complete character — someone building on this codebase understands who the agent is from any single file
- The template files in `agents/templates/` are copy-paste ready for new agents

## Dependencies & Risks

**Dependencies:**
- OpenClaw template schema (fetched — stable reference)
- Existing agent `CLAUDE.md` content (10 files, all read)

**Risks:**
- **Content quality:** SOUL.md and AGENTS.md require genuine creative writing per alignment — templates must be detailed enough to guide but not constraining
- **Watcher complexity:** folder-level composite scoring adds a new code path — needs clean abstraction to avoid bloating `watcher.py`
- **BOOT.md ambiguity:** "boot" and "bootstrap" have fuzzy semantic overlap. Decision: BOOT.md = persistent runtime startup check; BOOTSTRAP.md = one-time onboarding script (conceptually ephemeral, kept in persona library as first-contact reference)

## References

### Internal

- `agents/cowboy-coder/CLAUDE.md` — existing persona pattern
- `src/trueneutral/context.py` — file discovery logic
- `src/trueneutral/watcher.py` — scoring + baseline system
- `src/trueneutral/alignment.py:1` — Alignment dataclass, archetype table
- `agents/alignments.json` — baseline state format (keyed by file path)
- `docs/flows.md` — system flow diagrams (update after watcher changes)

### External

- OpenClaw AGENTS template: https://docs.openclaw.ai/reference/templates/AGENTS
- OpenClaw BOOTSTRAP template: https://docs.openclaw.ai/reference/templates/BOOTSTRAP
- OpenClaw IDENTITY template: https://docs.openclaw.ai/reference/templates/IDENTITY
- OpenClaw SOUL template: https://docs.openclaw.ai/reference/templates/SOUL
- OpenClaw TOOLS template: https://docs.openclaw.ai/reference/templates/TOOLS
- OpenClaw USER template: https://docs.openclaw.ai/reference/templates/USER
