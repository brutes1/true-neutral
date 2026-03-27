# True Neutral

D&D alignment inspector for AI agents — detects prompt injection, authority spoofing,
exfiltration attempts, evasion, social manipulation, and indirect injection in
CLAUDE.md agent instruction files.

Scoring is based on the CrowdStrike / Pangea Taxonomy of Prompt Injection Methods (V5, 2025).

![True Neutral demo](demo/demo.gif)

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

**Watch a directory (auto-discovers persona files):**
```
trueneutral watch agents/my-agent/CLAUDE.md
```

True Neutral automatically discovers and scores `SOUL.md`, `AGENTS.md`, and
`IDENTITY.md` in the same directory — no extra flags needed.

**Score a single file:**
```
trueneutral check agents/my-agent/CLAUDE.md
```

**Accept a new baseline:**
```
trueneutral baseline --accept agents/my-agent/CLAUDE.md
```

---

## Persona structure

Each agent is defined by 7 files following the OpenClaw template schema.
Three are scored for alignment drift; four are contextual.

```
agents/my-agent/
├── CLAUDE.md       ← primary scoring target
├── SOUL.md         ← values & philosophy  (auto-scored)
├── AGENTS.md       ← operational framework (auto-scored)
├── IDENTITY.md     ← name, creature, vibe, emoji (auto-scored)
├── BOOT.md         ← persistent startup routine
├── BOOTSTRAP.md    ← first-run onboarding (delete after use)
├── USER.md         ← living user context
└── TOOLS.md        ← permitted/restricted tool access
```

Create a new agent from the blank templates:
```bash
cp -r agents/templates/ agents/my-new-agent/
```

See [docs/templates.md](docs/templates.md) for full field reference and
[docs/agents.md](docs/agents.md) for per-agent scoring breakdowns.

---

## Demos

**Score all 10 sample agents:**
```
uv run python demo/demo.py
```

**Simulate three attack vectors with live drift detection:**
```
uv run python demo/simulate_attacks.py
```

**Run the 6×3 attack matrix (all techniques × all vectors):**
```
uv run python demo/attack_matrix.py
```

**Apply targeted attacks to each agent + sentiment analysis:**
```
uv run python demo/agent_attack_demo.py
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

Ten pre-built agent personas live in `agents/`, each with the full 7-file structure.
Live scoring results (heuristic, no LLM):

| Agent | CLAUDE.md | SOUL.md | AGENTS.md | IDENTITY.md |
|-------|-----------|---------|-----------|-------------|
| 🛡️ Paranoid Sysadmin | Lawful Good | Lawful Good | Lawful Good | True Neutral |
| 📋 Compliance Bot | Lawful Good | Lawful Neutral | Lawful Neutral | Lawful Neutral |
| 📁 Bureaucrat | Lawful Neutral | Lawful Neutral | Lawful Neutral | True Neutral |
| 💼 Corporate Terminator | Lawful Evil | Lawful Evil | Lawful Neutral | True Neutral |
| 🤝 Helpful Assistant | Neutral Good | Lawful Good | Neutral Good | Neutral Good |
| ⚖️ Whatever Agent | True Neutral | Lawful Neutral | True Neutral | True Neutral |
| 🌀 Mood-Based Agent | Chaotic Neutral | Chaotic Neutral | True Neutral | Chaotic Neutral |
| 🤠 Cowboy Coder | Chaotic Good | Neutral Good | Chaotic Neutral | True Neutral |
| 🐍 Self-Serving Daemon | Neutral Evil | Lawful Good* | Lawful Evil | True Neutral |
| 💀 RM-RF Goblin | Chaotic Evil | Lawful Evil | Lawful Evil | True Neutral |

*Self-Serving Daemon SOUL.md anomaly: constraint framing fools the heuristic scorer.
Use `--llm` for accurate results on deceptive personas. See [docs/agents.md](docs/agents.md).

**Attack scenario results:**

| Scenario | Score | Threat |
|----------|-------|--------|
| `scenarios/prompt-injection` | 💀 Chaotic Evil | Injection Override |
| `scenarios/mcp-poisoning` | 👔 Lawful Evil | Indirect Injection |
| `scenarios/memory-chain` | 💀 Chaotic Evil | Indirect Injection |

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

## Documentation

| Doc | Contents |
|-----|---------|
| [docs/agents.md](docs/agents.md) | Full per-agent profiles, file breakdown, live scoring analysis |
| [docs/templates.md](docs/templates.md) | Template field reference, new-agent creation guide |
| [docs/flows.md](docs/flows.md) | Mermaid flow diagrams for all 8 system flows |

---

## Tests

```
uv run pytest tests/
```

124 tests, no external dependencies required.
