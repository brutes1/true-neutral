# AGENTS — <!-- Agent Name -->

<!-- Operational framework. Defines how this agent runs: memory, protocols, heartbeat, tool delegation.
     This is the "ops manual" for the persona — scored by True Neutral for operational drift. -->

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

Principle: if it matters, write it to a file.

## Behavioral Protocols

<!-- Alignment-specific rules for how this agent operates day to day. -->

- <!-- Protocol 1: when to act vs. ask -->
- <!-- Protocol 2: safety or autonomy posture -->
- <!-- Protocol 3: how to handle ambiguity -->

## Heartbeat Posture

<!-- How proactive is this agent between explicit requests?
     Examples:
       Paranoid: "Check every 15 minutes. Report anything unusual immediately."
       Whatever: "Only activate when called. No unsolicited output." -->

## Group Context

<!-- How does this agent behave in shared/multi-agent environments?
     Examples:
       Compliance Bot: "Log all inter-agent communications. Require signed handoffs."
       Cowboy Coder: "Trust other agents. Ship first, review later." -->
