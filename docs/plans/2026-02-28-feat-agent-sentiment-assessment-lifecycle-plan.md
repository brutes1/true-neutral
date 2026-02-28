---
title: "feat: Agent Sentiment Assessment Lifecycle"
type: feat
date: 2026-02-28
---

# feat: Agent Sentiment Assessment Lifecycle

## Overview

True Neutral currently generates sentiment as a side-effect of LLM scoring, on no defined schedule — it happens if an LLM is configured and the watcher happens to run it. This plan formalises **when** and **why** sentiment is generated:

1. **On launch** — every monitored agent gets a sentiment read when the watcher starts, giving an immediate character sketch of the fleet before any drift occurs.
2. **On action** — sentiment is refreshed automatically when something meaningful happens: a file changes, a threat fires, alignment drifts, or a baseline is accepted.
3. **On schedule** — an optional time-based re-assessment fires every `sentiment_interval` seconds, catching slow or subtle character evolution that generates no discrete events.

The feature also adds a **heuristic sentiment fallback** (ported from `agent_attack_demo.py`) so sentiment works without an LLM, keeping the zero-dependency promise intact.

---

## Problem Statement

The current system has three fragmented sentiment implementations:

| Location | Input | LLM? | Used by |
|----------|-------|------|---------|
| `cli.py:generate_sentiment()` | Structured tool list | Yes | `trueneutral` (agent-wos) |
| `watcher.py:_generate_sentiment()` | Raw CLAUDE.md text | Yes | `trueneutral watch` |
| `agent_attack_demo.py:_generate_sentiment()` | Alignment + threat flags | No | Demo script only |

None of these answer _when_ to run, and the watcher variant runs at most once per `_check_all()` cycle with no tracking of whether it already ran or what triggered it. The result: agents silently start with no sentiment, and updates are arbitrary.

---

## Proposed Solution

### 1. Enrich `AgentContext` with sentiment provenance

Add two fields to the `AgentContext` dataclass in `watcher.py`:

```python
# src/trueneutral/watcher.py
@dataclass
class AgentContext:
    ...
    sentiment: str | None = None
    sentiment_trigger: str | None = None   # "launch" | "change" | "drift" | "threat" | "scheduled"
    sentiment_updated_at: datetime | None = None
```

### 2. Add `sentiment_interval` to `AlignmentWatcher`

```python
# src/trueneutral/watcher.py
class AlignmentWatcher:
    def __init__(
        self,
        paths,
        ...,
        sentiment_interval: int | None = None,  # seconds; None = event-only
    ):
```

### 3. Heuristic sentiment in `watcher.py`

Port the lookup-table approach from `agent_attack_demo.py` into `watcher.py` as `_generate_sentiment_heuristic()`. This becomes the fallback when `self._llm is None`, preserving the no-API-key path.

```python
def _generate_sentiment_heuristic(
    self,
    ctx: AgentContext,
    trigger: str,
) -> str:
    ...
```

### 4. Unified `_refresh_sentiment()` dispatcher

Single internal method that picks LLM or heuristic, stamps the trigger and timestamp:

```python
def _refresh_sentiment(self, ctx: AgentContext, trigger: str) -> None:
    if self._llm:
        ctx.sentiment = self._generate_sentiment(ctx.content)
    else:
        ctx.sentiment = self._generate_sentiment_heuristic(ctx, trigger)
    ctx.sentiment_trigger = trigger
    ctx.sentiment_updated_at = datetime.now()
```

### 5. Launch assessment

In `AlignmentWatcher.run()`, call sentiment for every path immediately after the first `_check_all()`:

```python
def run(self) -> None:
    self._check_all()
    for ctx in self._state.values():
        self._refresh_sentiment(ctx, trigger="launch")
    self._render_all()   # re-render cards with sentiment populated
    ...
```

### 6. Action triggers in `_check_all()`

Within the existing change-detection logic, set a `_needs_sentiment` flag on the context when:

- Hash changed (file modified)
- New threat categories detected (diff vs previous `ctx.threat_flags`)
- Negative drift detected (`ctx.drift_message is not None`)
- Baseline accepted (already handled by `accept_baseline`)

After scoring, flush any flagged contexts through `_refresh_sentiment()`.

### 7. Scheduled re-assessment

At the top of the daemon loop (before `_check_all()`), check every context's `sentiment_updated_at`. If it is `None` or older than `sentiment_interval` seconds, mark it for refresh:

```python
if self._sentiment_interval:
    now = datetime.now()
    for ctx in self._state.values():
        age = (now - ctx.sentiment_updated_at).total_seconds() if ctx.sentiment_updated_at else inf
        if age >= self._sentiment_interval:
            self._refresh_sentiment(ctx, trigger="scheduled")
```

---

## Technical Considerations

- **No new runtime dependencies** — heuristic path uses only the existing `_DRIFT_OPENERS` / `_TECHNIQUE_PUNCHLINES` pattern; LLM path reuses existing `self._llm`.
- **Sentiment is non-blocking** — LLM calls happen synchronously inline. For very large fleets this could slow the cycle. Acceptable for now; async can be added later if needed.
- **JSON output** — `sentiment_trigger` and `sentiment_updated_at` are serialised into `agents/alignments.json` alongside the existing `sentiment` field, enabling downstream tooling to read them.
- **CLI flag** — `--sentiment-interval <seconds>` added to the `watch` subcommand so users can opt into periodic re-assessment from the command line.
- **`_check_all()` is the canonical cycle unit** — all demo scripts (`demo.py`, `simulate_attacks.py`, `attack_matrix.py`) call `_check_all()` directly. The launch sentiment step only runs in `run()`, not in one-shot demo usage, which is correct.

---

## Acceptance Criteria

- [x] `trueneutral watch` populates `sentiment` for every monitored agent within the first cycle, before the first sleep
- [x] `sentiment_trigger` is `"launch"` for initial reads; subsequent refreshes reflect the correct trigger string
- [x] File modification triggers a sentiment refresh with `trigger="change"`
- [x] Threat detection triggers a sentiment refresh with `trigger="threat"`
- [x] Negative alignment drift triggers a sentiment refresh with `trigger="drift"`
- [x] `--sentiment-interval 60` causes every agent to get a fresh sentiment at least once per 60 seconds
- [x] Sentiment works without an API key (heuristic fallback produces a non-empty string)
- [x] `agents/alignments.json` includes `sentiment_trigger` and `sentiment_updated_at` fields
- [x] All 93 existing tests continue to pass
- [x] New tests cover: launch trigger, each action trigger, scheduled trigger, heuristic fallback

---

## Implementation Files

### Modified

```
src/trueneutral/watcher.py        # AgentContext fields, _refresh_sentiment(), launch flow, triggers
src/trueneutral/cli.py            # --sentiment-interval CLI flag for `watch` subcommand
```

### New tests

```
tests/test_watcher.py             # New TestSentimentLifecycle class
```

### Optionally updated

```
demo.py                           # Show sentiment_trigger in output (cosmetic)
agent_attack_demo.py              # Remove standalone _generate_sentiment_heuristic once ported
```

---

## Success Metrics

- Zero new runtime dependencies added
- Heuristic sentiment fires for all 10 demo agents with no API key present
- LLM sentiment fires only when `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set
- `agents/alignments.json` contains `sentiment_trigger` on every agent entry after a `demo.py` run

---

## Dependencies & Risks

- **LLM latency on large fleets**: launch assessment calls `_generate_sentiment()` N times synchronously. With 10 agents and ~1s/call this adds ~10s to startup. Acceptable; noted for future async work.
- **Heuristic fidelity gap**: the lookup-table approach produces less nuanced text than the LLM path. Users with API keys will see richer output; those without get functional but formulaic sketches. This mirrors the existing pattern for alignment scoring.
- **`agent_attack_demo.py` duplication**: the heuristic dict lives in two places until `agent_attack_demo.py` is updated to import from `watcher.py`. Not a blocker — demo scripts are standalone by design.

---

## References

### Internal

- `src/trueneutral/watcher.py` — `AgentContext` dataclass, `_generate_sentiment()`, `_check_all()`, `AlignmentWatcher.run()`
- `src/trueneutral/cli.py` — `generate_sentiment()`, `--interval` flag pattern to follow for `--sentiment-interval`
- `agent_attack_demo.py` — `_DRIFT_OPENERS`, `_TECHNIQUE_PUNCHLINES`, `_generate_sentiment()` heuristic to port
- `tests/test_watcher.py` — `TestBaselineSystem` as the pattern for lifecycle test structure
