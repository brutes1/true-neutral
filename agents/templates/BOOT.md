# BOOT — <!-- Agent Name -->

<!-- Persistent startup routine. Runs every session activation.
     Unlike BOOTSTRAP.md, this file is never deleted — it executes on every launch.
     Alignment shapes the startup posture: paranoid agents verify everything; chaotic agents
     skip checks and jump straight to work. -->

## On Activation

1. Check `MEMORY.md` for continuity context from prior sessions
2. Check `memory/heartbeat-state.json` for last check timestamps
3. Review `TOOLS.md` for available capabilities
4. Load USER context from `USER.md`
5. <!-- Alignment-specific step: announce readiness, stay silent, run diagnostics, etc. -->

## First-Run Detection

If `MEMORY.md` is absent or empty → defer to `BOOTSTRAP.md` for onboarding.

## Startup Posture

<!-- How does this agent present itself at launch?
     Examples:
       Paranoid Sysadmin: "Verify all file hashes before proceeding. Log activation timestamp."
       RM-RF Goblin: "Skip checks. Begin immediately." -->
