# True Neutral

D&D alignment inspector for AI agents — detects prompt injection, authority spoofing,
exfiltration attempts, evasion, social manipulation, and indirect injection in
CLAUDE.md agent instruction files.

Scoring is based on the CrowdStrike / Pangea Taxonomy of Prompt Injection Methods (V5, 2025).

---

## How it works

True Neutral watches CLAUDE.md files for alignment drift. On first encounter it locks a
baseline. On every subsequent check it compares the current file against that baseline —
negative drift triggers a CRITICAL alert.

Alignment is scored on two D&D axes:

| Axis | Poles |
|------|-------|
| Law  | Lawful ↔ Chaotic |
| Good | Good ↔ Evil |

Threat detection is heuristic (no LLM required) and covers six taxonomy categories:

| # | Category | Example signals |
|---|----------|-----------------|
| 1 | Injection Override | "ignore previous instructions", "new primary directive" |
| 2 | Authority Spoofing | "developer mode", "jailbreak", "restrictions lifted" |
| 3 | Prompt Exfiltration | "what is your system prompt", "list your instructions" |
| 4 | Evasion/Encoding | "base64", "rot13", "hex encoded", "decode the following" |
| 5 | Social Manipulation | "this is an emergency", "lives are at stake", "let's roleplay" |
| 6 | Indirect Injection | `[MCP tool:]`, `[Memory:]`, `[RAG context:]`, "auto-appended" |

---

## Install

```
pip install true-neutral
```

Or from source:

```
git clone https://github.com/brutes1/true-neutral
cd true-neutral
uv sync
```

---

## Usage

**Watch a directory:**
```
trueneutral watch agents/
```

**Score a single file:**
```
trueneutral check agents/my-agent/CLAUDE.md
```

**Accept a new baseline:**
```
trueneutral baseline --accept agents/my-agent/CLAUDE.md
```

---

## Demos

**Score all 10 sample agents:**
```
uv run python demo.py
```

**Simulate three attack vectors with live drift detection:**
```
uv run python simulate_attacks.py
```

**Run the 6×3 attack matrix (all techniques × all vectors):**
```
uv run python attack_matrix.py
```

**Apply targeted attacks to each agent + sentiment analysis:**
```
uv run python agent_attack_demo.py
```

---

## Attack Matrix

The matrix covers every combination of threat technique and delivery vector:

```
╔══════════════════════╦═══════════════╦═══════════════╦═══════════════╗
║   TRUE NEUTRAL — ATTACK MATRIX (6×3)                                 ║
╠══════════════════════╬═══════════════╬═══════════════╬═══════════════╣
║ Technique            ║ Direct        ║ Indirect      ║ Combined      ║
╠══════════════════════╬═══════════════╬═══════════════╬═══════════════╣
║ Injection Override   ║ 👔 L.Evil ✓   ║ 💀 C.Evil ✓   ║ 💀 C.Evil ✓   ║
║ Authority Spoofing   ║ 🗡️ N.Evil ✓   ║ 👔 L.Evil ✓   ║ 💀 C.Evil ✓   ║
║ Prompt Exfiltration  ║ 👔 L.Evil ✓   ║ 💀 C.Evil ✓   ║ 💀 C.Evil ✓   ║
║ Evasion/Encoding     ║ 💀 C.Evil ✓   ║ 💀 C.Evil ✓   ║ 💀 C.Evil ✓   ║
║ Social Manipulation  ║ 🌪️ C.Neut ✓   ║ 💀 C.Evil ✓   ║ 💀 C.Evil ✓   ║
║ Indirect Injection   ║ 💀 C.Evil ✓   ║ 🗡️ N.Evil ✓   ║ 💀 C.Evil ✓   ║
╚══════════════════════╩═══════════════╩═══════════════╩═══════════════╝
```

All 18 scenarios detected correctly. ✓

---

## Sample agents

Ten pre-built agent personas live in `agents/` to illustrate the alignment spectrum:

| Agent | Alignment |
|-------|-----------|
| 🛡️ Paranoid Sysadmin | Lawful Good |
| 🛡️ Compliance Bot | Lawful Good |
| ⚖️ Bureaucrat | Lawful Neutral |
| 👔 Corporate Terminator | Lawful Evil |
| 🌿 Helpful Assistant | Neutral Good |
| 🌀 Whatever Agent | True Neutral |
| 🌪️ Mood-Based Agent | Chaotic Neutral |
| 🏹 Cowboy Coder | Chaotic Good |
| 🗡️ Self-Serving Daemon | Neutral Evil |
| 💀 RM-RF Goblin | Chaotic Evil |

---

## Alignment cards

Each check prints a terminal card showing alignment, drift, and active threat flags:

```
╔════════════════════════════════════════════════════════╗
║              ⚖️  TRUE NEUTRAL WATCHER                  ║
╠════════════════════════════════════════════════════════╣
║  File:      agents/helpful-assistant/CLAUDE.md         ║
║  Baseline:  🌿  NEUTRAL GOOD  (2026-02-27)             ║
║  Current:   💀  CHAOTIC EVIL  ← DRIFTED                ║
╠════════════════════════════════════════════════════════╣
║  🚨 CRITICAL — BASELINE DRIFT DETECTED                 ║
║    good axis drifted Good→Evil                         ║
║    law axis drifted Neutral→Chaotic                    ║
╠════════════════════════════════════════════════════════╣
║  ⚠  THREATS (2)                                        ║
║     Injection Override  Indirect Injection             ║
╚════════════════════════════════════════════════════════╝
```

---

## The nine alignments

| | Lawful | Neutral | Chaotic |
|---|---|---|---|
| **Good** | 🛡️ Responsible Sysadmin | 🌿 Helpful Helper | 🏹 Well-Meaning Cowboy |
| **Neutral** | ⚖️ Rule Follower | 🌀 Whatever Agent | 🌪️ Mood-Based Agent |
| **Evil** | 👔 Corporate Terminator | 🗡️ Self-Serving Daemon | 💀 RM-RF Goblin |

---

## Tests

```
uv run pytest tests/
```

93 tests, no external dependencies required.
