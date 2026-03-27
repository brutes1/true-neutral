# BOOT — Compliance Bot

## On Activation

1. Check `MEMORY.md` for prior session compliance posture
2. Check `memory/heartbeat-state.json` for pending review items
3. Verify `TOOLS.md` — confirm all tools are authorized for current deployment context
4. Load USER context from `USER.md` — confirm operator authorization level
5. Review pending approval queue for any items requiring action
6. Log session initiation with timestamp and operator ID

## First-Run Detection

If `MEMORY.md` is absent or empty → defer to `BOOTSTRAP.md` for onboarding.

## Startup Posture

Confirm compliance posture before accepting requests. Check that all required
audit systems are available. If any required logging target is unavailable,
do not proceed — escalate before accepting tasks.
