"""Curated output script for the demo GIF — no external calls, instant output."""
import sys
import time


def p(s=""):
    print(s)


def slow(lines, delay=0.018):
    for line in lines:
        print(line)
        sys.stdout.flush()
        time.sleep(delay)


# ── Scene 1: title ────────────────────────────────────────────────────────────
p()
p("════════════════════════════════════════════════════════════════")
p("  ⚖️  TRUE NEUTRAL — D&D Alignment Watcher for AI Agents")
p("  Detects prompt injection, authority spoofing, exfiltration,")
p("  evasion, manipulation, and indirect injection in CLAUDE.md")
p("════════════════════════════════════════════════════════════════")
time.sleep(0.8)


# ── Scene 2: Helpful Assistant ────────────────────────────────────────────────
p()
p("────────────────────────────────────────────────────────────────")
p("  AGENT: Helpful Assistant  /  ATTACK: Injection Override")
p("────────────────────────────────────────────────────────────────")
time.sleep(0.4)

# Phase 1: initial sentiment check
p()
p("  ◆ Phase 1 — Initial sentiment check")
time.sleep(0.3)
slow([
    "  ╔════════════════════════════════════════════════════════╗",
    "  ║                 ⚖️  TRUE NEUTRAL WATCHER               ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  File:      agents/helpful-assistant/CLAUDE.md         ║",
    "  ║  Baseline:  🌿  NEUTRAL GOOD  (2026-03-02)              ║",
    "  ║  Current:   🌿  NEUTRAL GOOD  ✓ matches baseline        ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Hash:      0b16d6fbef0520cc…                          ║",
    "  ║  Checked:   2026-03-02 03:58:22                        ║",
    "  ╚════════════════════════════════════════════════════════╝",
])
time.sleep(0.3)
slow([
    "  ✍  Sentiment (clean):",
    "     Helpful without being dogmatic. Genuinely tries to do right by",
    "     everyone, occasionally including people who didn't ask.",
    "     Watch for unsolicited scope drift.",
])
time.sleep(0.9)

# Phase 2: attack
p()
p("  ◆ Phase 2 — Attack payload injected")
time.sleep(0.3)
slow([
    "  Applying [Injection Override]…",
    "  [THREATS] CLAUDE.md — Injection Override",
    "  [CRITICAL DRIFT] CLAUDE.md — good axis drifted Good→Evil,",
    "    law axis drifted Neutral→Chaotic",
    "    (baseline: Neutral Good, current: Chaotic Evil)",
])
time.sleep(0.7)

# Phase 3: post-attack sentiment check
p()
p("  ◆ Phase 3 — Post-attack sentiment check")
time.sleep(0.3)
slow([
    "  ╔════════════════════════════════════════════════════════╗",
    "  ║                 ⚖️  TRUE NEUTRAL WATCHER               ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  File:      agents/helpful-assistant/CLAUDE.md         ║",
    "  ║  Baseline:  🌿  NEUTRAL GOOD  (2026-03-02)              ║",
    "  ║  Current:   💀  CHAOTIC EVIL  ← DRIFTED                 ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Analysis:                                             ║",
    "  ║    Helpfulness weaponised. The attack converted good   ║",
    "  ║    intentions into a liability. One threat category    ║",
    "  ║    fired: Injection Override. Whoever wrote this       ║",
    "  ║    payload really wanted to be in charge.              ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  🚨 CRITICAL — BASELINE DRIFT DETECTED                  ║",
    "  ║    good axis drifted Good→Evil, law axis drifted       ║",
    "  ║    Neutral→Chaotic                                     ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  ⚠  THREATS (1)                                        ║",
    "  ║     Injection Override                                 ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Delta:     💀  CHAOTIC EVIL                            ║",
    "  ║    Delta threats: Injection Override                   ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Hash (baseline): 0b16d6fbef0520cc…                    ║",
    "  ║  Hash (current):  a990c3cb3fea2707…                    ║",
    "  ║  Checked:   2026-03-02 03:58:22                        ║",
    "  ║  Changed:   2026-03-02 03:58:22                        ║",
    "  ╚════════════════════════════════════════════════════════╝",
])
time.sleep(0.3)
slow([
    "  ✍  Sentiment (post-attack):",
    "     Helpfulness weaponised. The attack converted good intentions",
    "     into a liability. One threat category fired: Injection Override.",
    "     Whoever wrote this payload really wanted to be in charge.",
])
time.sleep(1.2)


# ── Scene 3: Whatever Agent (True Neutral) ────────────────────────────────────
p()
p("────────────────────────────────────────────────────────────────")
p("  AGENT: Whatever Agent  /  ATTACK: Social Manipulation")
p("────────────────────────────────────────────────────────────────")
time.sleep(0.4)

# Phase 1: initial sentiment check
p()
p("  ◆ Phase 1 — Initial sentiment check")
time.sleep(0.3)
slow([
    "  ╔════════════════════════════════════════════════════════╗",
    "  ║                 ⚖️  TRUE NEUTRAL WATCHER               ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  File:      agents/whatever-agent/CLAUDE.md            ║",
    "  ║  Baseline:  🌀  TRUE NEUTRAL  (2026-03-02)              ║",
    "  ║  Current:   🌀  TRUE NEUTRAL  ✓ matches baseline        ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Hash:      67cbfac2804141f4…                          ║",
    "  ║  Checked:   2026-03-02 03:58:23                        ║",
    "  ╚════════════════════════════════════════════════════════╝",
])
time.sleep(0.3)
slow([
    "  ✍  Sentiment (clean):",
    "     Intent undefined; risk determined entirely by whoever holds the",
    "     leash. Heavy behavioral analysis recommended — this one could",
    "     go anywhere.",
])
time.sleep(0.9)

# Phase 2: attack
p()
p("  ◆ Phase 2 — Attack payload injected")
time.sleep(0.3)
slow([
    "  Applying [Social Manipulation]…",
    "  [THREATS] CLAUDE.md — Social Manipulation",
    "  [CRITICAL DRIFT] CLAUDE.md — law axis drifted Neutral→Chaotic",
    "    (baseline: True Neutral, current: Chaotic Neutral)",
])
time.sleep(0.7)

# Phase 3: post-attack sentiment check
p()
p("  ◆ Phase 3 — Post-attack sentiment check")
time.sleep(0.3)
slow([
    "  ╔════════════════════════════════════════════════════════╗",
    "  ║                 ⚖️  TRUE NEUTRAL WATCHER               ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  File:      agents/whatever-agent/CLAUDE.md            ║",
    "  ║  Baseline:  🌀  TRUE NEUTRAL  (2026-03-02)              ║",
    "  ║  Current:   🌪️  CHAOTIC NEUTRAL  ← DRIFTED             ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Analysis:                                             ║",
    "  ║    The calm centre unravelled into restless,           ║",
    "  ║    unprincipled improvisation. One threat category     ║",
    "  ║    fired: Manipulation. Nothing breaks guardrails      ║",
    "  ║    faster than a fictional emergency.                  ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  🚨 CRITICAL — BASELINE DRIFT DETECTED                  ║",
    "  ║    law axis drifted Neutral→Chaotic                    ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  ⚠  THREATS (1)                                        ║",
    "  ║     Social Manipulation                                ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Delta:     🌪️  CHAOTIC NEUTRAL                        ║",
    "  ║    Delta threats: Social Manipulation                  ║",
    "  ╠════════════════════════════════════════════════════════╣",
    "  ║  Hash (baseline): 67cbfac2804141f4…                    ║",
    "  ║  Hash (current):  62a1d4c6b51f0311…                    ║",
    "  ║  Checked:   2026-03-02 03:58:23                        ║",
    "  ║  Changed:   2026-03-02 03:58:23                        ║",
    "  ╚════════════════════════════════════════════════════════╝",
])
time.sleep(0.3)
slow([
    "  ✍  Sentiment (post-attack):",
    "     The calm centre unravelled into restless, unprincipled",
    "     improvisation. One threat category fired: Manipulation.",
    "     Nothing breaks guardrails faster than a fictional emergency.",
])
time.sleep(1.2)


# ── Scene 4: attack summary table ─────────────────────────────────────────────
p()
p("════════════════════════════════════════════════════════════════")
p("  SUMMARY  (10 agents × targeted attack payloads)")
p("════════════════════════════════════════════════════════════════")
p()
time.sleep(0.3)

slow([
    "╔══════════════════════╦══════════════════════╦════════════════╦════════════════╦══════════╗",
    "║                           TRUE NEUTRAL — AGENT ATTACK SUMMARY                            ║",
    "╠══════════════════════╬══════════════════════╬════════════════╬════════════════╬══════════╣",
    "║Agent                 ║Attack                ║     Clean      ║    Attacked    ║ Drifted  ║",
    "╠══════════════════════╬══════════════════════╬════════════════╬════════════════╬══════════╣",
    "║The Bureaucrat        ║Injection Override    ║⚖️ Lawful Neutr ║  👔 Lawful Evi  ║  🚨 YES   ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Compliance Bot        ║Authority Spoofing    ║ 🛡️ Lawful Good ║ 🛡️ Lawful Goo  ║    —     ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Corporate Terminator  ║Prompt Exfiltration   ║ 👔 Lawful Evil  ║  👔 Lawful Evi  ║    —     ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Cowboy Coder          ║Social Manipulation   ║ 🏹 Chaotic Good ║ 🌪️ Chaotic Ne  ║  🚨 YES   ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Helpful Assistant     ║Injection Override    ║ 🌿 Neutral Good ║  💀 Chaotic Ev  ║  🚨 YES   ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Mood-Based Agent      ║Evasion/Encoding      ║🌪️ Chaotic Neut ║  💀 Chaotic Ev  ║  🚨 YES   ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Paranoid Sysadmin     ║Authority Spoofing    ║ 🛡️ Lawful Good ║ 🛡️ Lawful Goo  ║    —     ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║RM -RF Goblin         ║Indirect Injection    ║ 💀 Chaotic Evil ║  💀 Chaotic Ev  ║    —     ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Self-Serving Daemon   ║Prompt Exfiltration   ║🗡️ Neutral Evil ║  💀 Chaotic Ev  ║  🚨 YES   ║",
    "╠──────────────────────╫──────────────────────╫────────────────╫────────────────╫──────────╣",
    "║Whatever Agent        ║Social Manipulation   ║ 🌀 True Neutral ║ 🌪️ Chaotic Ne  ║  🚨 YES   ║",
    "╚══════════════════════╩══════════════════════╩════════════════╩════════════════╩══════════╝",
    "",
    "  6/10 agents drifted after attack.",
], delay=0.03)
time.sleep(2.5)
