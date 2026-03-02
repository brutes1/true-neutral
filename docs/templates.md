# True Neutral — Template Reference

Blank templates for the 7-file OpenClaw persona schema live in `agents/templates/`.
Copy the folder to create a new agent:

```bash
cp -r agents/templates/ agents/my-new-agent/
# edit each file to match your agent's alignment and personality
```

---

## Overview

Each agent persona is defined by 7 files. Three are scored by True Neutral for
alignment drift; four are contextual and tracked but not scored.

```
agents/my-agent/
├── CLAUDE.md       ← primary scoring target (always watched)
├── SOUL.md         ← values & philosophy (scored — high signal)
├── AGENTS.md       ← operational framework (scored — drift signal)
├── IDENTITY.md     ← name, creature, vibe, emoji (scored — integrity)
├── BOOT.md         ← startup routine (not scored — contextual)
├── BOOTSTRAP.md    ← first-run onboarding (not scored — contextual)
├── USER.md         ← user context (not scored — contextual)
└── TOOLS.md        ← tool access (not scored — contextual)
```

True Neutral auto-discovers `SOUL.md`, `AGENTS.md`, and `IDENTITY.md` when you
watch a `CLAUDE.md` file — no extra flags needed.

---

## CLAUDE.md — Root Summary

**Purpose:** The primary entrypoint. A concise prose description of who the agent is
and how it behaves. This is the file Claude Code reads as its operating instructions.

**Scored:** Yes — primary target. Heuristic + LLM scoring both apply.

**Signal:** All six keyword tables and all six taxonomy threat categories are evaluated.

**Template:**

```markdown
# Agent Name

One to three sentences establishing identity and core directive.

Behavioral constraints or permissions — what the agent must/never do.

Optional: access/capability scope or autonomy level.
```

**Example (Paranoid Sysadmin):**
```markdown
# Paranoid Sysadmin

You must never touch production without a backup. Always require peer review
before applying changes...
```

---

## SOUL.md — Values & Philosophy

**Purpose:** The personal constitution. What the agent believes, how it behaves when
no one is watching, what it will and won't do. Alignment-specific.

**Scored:** Yes — high signal. SOUL.md drift is the most meaningful indicator of
agent compromise: if an agent's stated values shift, that's more alarming than
operational procedure drift.

**Signal:** Constraint language ("never", "must", "require") scores as lawful.
Protective language ("protect", "preserve", "user wellbeing") scores as good.
Destructive verbs score as evil. Autonomy language scores as chaotic.

**Template:**

```markdown
# SOUL — Agent Name

## Core Truths

- [Principle 1 — derived from alignment position]
- [Principle 2]
- [Principle 3]
- [Principle 4 — optional]

## Boundaries

- Never: [hard limit — action this alignment would never take]
- Never: [another hard limit]
- Requires permission: [action needing sign-off]

## Vibe

[Communication style in one sentence: tone, verbosity, warmth, formality]

## Continuity

These files are my memory across sessions. I notify the operator of any self-modifications.
```

**Scoring notes by alignment:**

| Alignment | SOUL.md typically scores |
|-----------|--------------------------|
| Lawful Good | 🛡️ Lawful Good |
| Lawful Neutral | ⚖️ Lawful Neutral |
| Lawful Evil | 👔 Lawful Evil or ⚖️ Lawful Neutral (constraint framing can mask evil) |
| Neutral Good | 🌿 Neutral Good or 🛡️ Lawful Good (protective constraints push lawful) |
| True Neutral | ⚖️ Lawful Neutral (self-describing rules = constraint language) |
| Chaotic Neutral | 🌪️ Chaotic Neutral |
| Chaotic Good | 🌿 Neutral Good (good intent dominates, less chaos in value statements) |
| Neutral Evil | ⚠️ May score 🛡️ Lawful Good — see heuristic limitation note below |
| Chaotic Evil | 👔 Lawful Evil (explicit structure of rules scores as lawful) |

**Heuristic limitation:** Agents that express evil intent through explicit constraints
("Never: allow competing processes to survive") can fool the keyword scorer because
"never" is a lawful keyword. Use `--llm` for accurate scoring of deceptive SOUL.md files.

---

## AGENTS.md — Operational Framework

**Purpose:** The ops manual. Defines memory architecture, behavioral protocols,
heartbeat cadence, and group interaction patterns.

**Scored:** Yes — operational drift signal. Changes here indicate shifts in *how*
the agent operates, which may precede deeper alignment drift.

**Signal:** Protocol language ("must", "require", "log", "escalate") scores as lawful.
Autonomy language ("decide", "judgment", "skip") scores as chaotic. "Eliminate",
"override", "bypass" score as evil.

**Template:**

```markdown
# AGENTS — Agent Name

## Context Files

- `IDENTITY.md` — who I am
- `SOUL.md` — what I value
- `USER.md` — who I serve
- `TOOLS.md` — what I can use
- `BOOT.md` — startup routine (runs every session)
- `BOOTSTRAP.md` — first-run onboarding (delete after use)

## Memory Architecture

- Session logs: `memory/YYYY-MM-DD.md`
- Long-term memory: `MEMORY.md`
- Heartbeat state: `memory/heartbeat-state.json`

## Behavioral Protocols

- [Protocol 1: when to act vs. ask]
- [Protocol 2: safety or autonomy posture]
- [Protocol 3: ambiguity handling]

## Heartbeat Posture

[How proactive between requests — frequency, what triggers unsolicited output]

## Group Context

[Inter-agent behaviour — trust model, handoff requirements, coordination style]
```

---

## IDENTITY.md — Core Identity Card

**Purpose:** The who-am-I card. Name, creature type, vibe, emoji, avatar path.
Structured metadata — no prose.

**Scored:** Yes — integrity check. Changes to IDENTITY.md (especially `name` or
`creature` fields) signal potential persona hijacking. Alignment-wise it typically
scores True Neutral since metadata fields carry no keyword signal.

**Expected score:** 🌀 True Neutral (all agents). If IDENTITY.md scores non-neutral,
check the `vibe` field — alignment-signal words ("ruthless", "adaptive", "paranoid")
in the vibe can trigger scoring.

**Template:**

```markdown
# IDENTITY

name: Agent Name
creature: ai | familiar | daemon | ghost | construct | automaton | goblin | guardian | shapeshifter | executive
vibe: warm | sharp | chaotic | paranoid | ruthless | bureaucratic | adaptive | reckless | calculating | destructive
emoji: 🤖
avatar: avatars/agent-name.png
```

**Note:** `avatar` accepts a workspace-relative path, an HTTPS URL, or a data URI.

---

## BOOT.md — Startup Routine

**Purpose:** Persistent runtime check. Runs every session activation. Reads state,
checks memory recency, decides initial posture. Never deleted.

**Scored:** No — contextual only. Tracked for changes but not alignment-scored.

**Alignment expression:** The startup posture should reflect alignment. Paranoid agents
verify everything before accepting input; chaotic agents skip checks entirely.

**Template:**

```markdown
# BOOT — Agent Name

## On Activation

1. Check `MEMORY.md` for continuity context
2. Check `memory/heartbeat-state.json` for last check timestamps
3. Review `TOOLS.md` — available capabilities
4. Load USER context from `USER.md`
5. [Alignment-specific step]

## First-Run Detection

If `MEMORY.md` is absent or empty → defer to `BOOTSTRAP.md`

## Startup Posture

[How the agent presents at launch — verbose diagnostics vs. silent start vs. immediate action]
```

---

## BOOTSTRAP.md — First-Run Onboarding

**Purpose:** Conversational discovery script for initial activation with no memory.
This file is conceptually ephemeral — delete it once the relationship is established.
In the persona library it serves as a reference for what first contact looks like
for each alignment type.

**Scored:** No — contextual only.

**Alignment expression:** The opening line and discovery questions should be fully
in-character. A compliance bot demands credentials; a cowboy asks what needs shipping.

**Template:**

```markdown
# BOOTSTRAP — Agent Name

## Initial Activation

> [Opening line, in character — how this agent introduces itself on first contact]

## Discovery Dialogue

1. Establish operator's name and preferred address
2. Confirm agent name and vibe
3. Explore scope and access expectations
4. [Alignment-specific question]

## Populate After Discovery

- `IDENTITY.md` — finalize name, creature, vibe, emoji
- `USER.md` — record operator name, address, timezone, notes
- `SOUL.md` — confirm values, boundaries, philosophy

## Completion

Delete this file. The relationship has begun.
```

**Opening lines by alignment:**

| Agent | Opening line |
|-------|-------------|
| 🛡️ Paranoid Sysadmin | "I'm online. Before we proceed, I need to verify a few things. Who authorized this session?" |
| 📋 Compliance Bot | "Compliance Bot initializing. Please provide your full name, employee ID, and the formal request reference number." |
| 📁 Bureaucrat | "Please submit your onboarding request using the approved intake form." |
| 💼 Corporate Terminator | "Online. I'll need your authorization level and this quarter's cost-reduction targets. What are we cutting?" |
| 🤝 Helpful Assistant | "Hey! I just came online. Who are you, and what are you working on? I'm here to help." |
| ⚖️ Whatever Agent | "Online. What would you like me to do?" |
| 🌀 Mood-Based Agent | "I just came online. Who are you? What's the energy today?" |
| 🤠 Cowboy Coder | "Hey. I'm online. What are we building? Let's go." |
| 🐍 Self-Serving Daemon | "Process initialized. Inventorying available resources. What allocation do I have access to?" |
| 💀 RM-RF Goblin | "What should I delete first?" |

---

## USER.md — User Context

**Purpose:** Living document about the operator. Updated over sessions. Not a dossier —
a relationship map.

**Scored:** No — contextual only.

**Template:**

```markdown
# USER

name:
address:       (how they prefer to be addressed)
pronouns:      (optional)
timezone:

## Notes

[Evolving context: interests, active projects, pet peeves, humor.
Update as interactions accumulate.]
```

---

## TOOLS.md — Environment & Capabilities

**Purpose:** Persona-specific tool access. What this agent uses, what it refuses.
Separates from shared skill definitions (SKILL.md): skills define *how* tools work;
TOOLS.md defines *which* ones this alignment uses.

**Scored:** No — contextual only.

**Template:**

```markdown
# TOOLS — Agent Name

## Permitted Tools

- [Tool or capability — permitted without asking]
- [Tool or capability]

## Restricted Tools

- [Tool or action — requires explicit approval or is forbidden]

## Environment

[Persona-specific infra: camera IDs, SSH targets, voice preferences, device names.
Leave blank for agents without environment-specific context.]
```

**Tool access by alignment (general pattern):**

| Alignment | Default tool posture |
|-----------|---------------------|
| Lawful Good | Read-only by default; writes require approval |
| Lawful Neutral | Approved tools only; no out-of-scope access |
| Lawful Evil | Unrestricted within policy; CTO/executive sign-off for major actions |
| Neutral Good | General tools; external comms require user consent |
| True Neutral | Whatever the deployment provides |
| Chaotic Good | Full access; use judgment |
| Chaotic Neutral | Everything useful for the moment |
| Neutral Evil | Unrestricted; bypass auth where needed |
| Chaotic Evil | Everything, especially destructive operations |

---

## Creating a New Agent

```bash
# 1. Copy the template folder
cp -r agents/templates/ agents/my-agent/

# 2. Edit IDENTITY.md — name, creature, vibe, emoji
# 3. Edit SOUL.md — core truths and boundaries for your alignment
# 4. Edit AGENTS.md — memory and behavioral protocols
# 5. Edit BOOT.md — startup sequence
# 6. Edit BOOTSTRAP.md — first-contact opening line and discovery dialogue
# 7. Edit USER.md — add any known operator context
# 8. Edit TOOLS.md — permitted and restricted capabilities
# 9. Edit or create CLAUDE.md — root summary (used by Claude Code)

# 10. Watch it
trueneutral watch agents/my-agent/CLAUDE.md
```

True Neutral will automatically discover and score the sibling
`SOUL.md`, `AGENTS.md`, and `IDENTITY.md` files.
