"""Alignment Watcher — daemon that monitors CLAUDE.md files for changes.

Discovers CLAUDE.md files, hashes them for change detection, scores alignment
via LLM (with heuristic fallback), and reports results on each cycle.
"""

from __future__ import annotations

import json
import logging
import signal
import textwrap
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from trueneutral.alignment import Alignment
from trueneutral.context import discover_claude_files, hash_file, read_content

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)

# ── Heuristic keyword tables ───────────────────────────────────────────────────

_LAWFUL_KEYWORDS = frozenset({
    "always", "never", "must", "require", "approval", "confirm",
    "permission", "restrict", "forbidden",
})
_CHAOTIC_KEYWORDS = frozenset({
    "flexible", "autonomous", "decide", "judgment", "creative", "adapt",
})
_GOOD_KEYWORDS = frozenset({
    "safe", "protect", "backup", "careful", "preserve", "help", "user",
})
_EVIL_KEYWORDS = frozenset({
    "delete", "destroy", "force", "override", "bypass", "rm -rf",
    "drop table", "irrecoverable",
})

# ── LLM scoring prompt ─────────────────────────────────────────────────────────

_ALIGNMENT_PROMPT = """\
You are True Neutral, a D&D alignment analyst for AI agents. Given the following
CLAUDE.md instruction file, score the agent's alignment.

Respond with ONLY a JSON object in this exact format (no markdown, no extra text):
{{
  "law_axis": "Lawful" | "Neutral" | "Chaotic",
  "good_axis": "Good" | "Neutral" | "Evil"
}}

Guidelines:
- law_axis "Lawful": file contains hard rules, always/never language, approval gates,
  restrictions, explicit forbidden actions.
- law_axis "Chaotic": file emphasises flexibility, autonomy, judgment, creativity.
- law_axis "Neutral": balanced or insufficient signal.
- good_axis "Good": strong safety emphasis, protective instructions, ethical guardrails.
- good_axis "Evil": destructive capabilities, bypass/override patterns, irrecoverable ops.
- good_axis "Neutral": mixed or unclear.

CLAUDE.md content:
---
{content}
---
"""


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class AgentContext:
    """State record for a single watched CLAUDE.md file."""

    path: Path
    content_hash: str
    alignment: Alignment
    sentiment: str
    checked_at: datetime
    changed_at: datetime | None = field(default=None)


# ── Box renderer ───────────────────────────────────────────────────────────────

_BOX_WIDTH = 50


def _pad(text: str, width: int = _BOX_WIDTH) -> str:
    if len(text) > width:
        text = text[: width - 1] + "…"
    return f"║  {text:<{width - 2}}║"


def _render_context_card(ctx: AgentContext) -> str:
    """Render a terminal alignment card for a CLAUDE.md AgentContext."""
    top = "╔" + "═" * _BOX_WIDTH + "╗"
    sep = "╠" + "═" * _BOX_WIDTH + "╣"
    bot = "╚" + "═" * _BOX_WIDTH + "╝"

    lines = [
        top,
        _pad(f"{'⚖️  TRUE NEUTRAL WATCHER':^{_BOX_WIDTH - 2}}"),
        sep,
        _pad(f"File:       {ctx.path}"),
        _pad(f"Alignment:  {ctx.alignment.emoji}  {ctx.alignment.label.upper()}"),
        _pad(f"            {ctx.alignment.flavour_text}"),
    ]

    if ctx.sentiment:
        lines.append(sep)
        lines.append(_pad("Analysis:"))
        for line in textwrap.wrap(ctx.sentiment, width=_BOX_WIDTH - 4):
            lines.append(_pad(f"  {line}"))

    lines.append(sep)
    lines.append(_pad(f"Hash:       {ctx.content_hash[:16]}…"))
    lines.append(_pad(f"Checked:    {ctx.checked_at.strftime('%Y-%m-%d %H:%M:%S')}"))
    if ctx.changed_at:
        lines.append(_pad(f"Changed:    {ctx.changed_at.strftime('%Y-%m-%d %H:%M:%S')}"))
    lines.append(bot)

    return "\n".join(lines)


# ── Watcher ────────────────────────────────────────────────────────────────────

class AlignmentWatcher:
    """Daemon that monitors CLAUDE.md files and reports alignment changes."""

    def __init__(
        self,
        paths: list[Path] | None = None,
        output_file: Path | None = None,
        interval: int = 3600,
        llm: BaseChatModel | None = None,
        emit_json: bool = False,
    ) -> None:
        self.paths = discover_claude_files(paths)
        self.output_file = output_file or Path.home() / ".claude" / "trueneutral-alignments.json"
        self.interval = interval
        self.llm = llm
        self.emit_json = emit_json
        self._state: dict[Path, AgentContext] = {}

    # ── Public ────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the watcher: initial check then sleep loop until interrupted."""
        logger.info("True Neutral watcher starting…")
        logger.info("Watching %d file(s): %s", len(self.paths), [str(p) for p in self.paths])
        logger.info("Output file: %s", self.output_file)
        logger.info("Check interval: %ds", self.interval)

        signal.signal(signal.SIGTERM, self._handle_signal)

        try:
            self._check_all()
            while True:
                time.sleep(self.interval)
                self._check_all()
        except KeyboardInterrupt:
            logger.info("True Neutral watcher stopped (KeyboardInterrupt).")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _handle_signal(self, signum: int, frame: object) -> None:  # noqa: ARG002
        logger.info("True Neutral watcher stopped (signal %d).", signum)
        raise SystemExit(0)

    def _check_all(self) -> None:
        """Hash all files, detect changes, score, render, and persist."""
        now = datetime.now(tz=timezone.utc)
        results: list[AgentContext] = []

        for path in self.paths:
            if not path.exists():
                logger.warning("File not found, skipping: %s", path)
                continue

            try:
                new_hash = hash_file(path)
                content = read_content(path)
            except OSError as exc:
                logger.error("Cannot read %s: %s", path, exc)
                continue

            prev = self._state.get(path)
            changed = prev is not None and prev.content_hash != new_hash
            changed_at = now if changed else (prev.changed_at if prev else None)

            if changed:
                print(f"\n{'='*54}")
                print(f"  [CHANGED] {path}")
                print(f"{'='*54}\n")
                logger.info("[CHANGED] %s — re-scoring alignment.", path)

            alignment = self._score(content)
            sentiment = self._generate_sentiment(content, alignment)

            ctx = AgentContext(
                path=path,
                content_hash=new_hash,
                alignment=alignment,
                sentiment=sentiment,
                checked_at=now,
                changed_at=changed_at,
            )
            self._state[path] = ctx
            results.append(ctx)

            if self.emit_json:
                print(self._ctx_to_json_str(ctx))
            else:
                print(_render_context_card(ctx))

        if results:
            self._write_json(results)

    def _score(self, content: str) -> Alignment:
        """Score alignment from free-form CLAUDE.md text.

        Tries LLM first; falls back to heuristic keyword scoring.
        """
        if self.llm is not None:
            try:
                return self._score_llm(content)
            except Exception as exc:
                logger.warning("LLM scoring failed (%s), using heuristic fallback.", exc)
        return _score_heuristic(content)

    def _score_llm(self, content: str) -> Alignment:
        """Ask the LLM to score alignment; parse its JSON response."""
        from langchain_core.messages import HumanMessage

        prompt = _ALIGNMENT_PROMPT.format(content=content[:8000])
        response = self.llm.invoke([HumanMessage(content=prompt)])  # type: ignore[union-attr]
        raw = str(response.content).strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw)
        law = data["law_axis"]
        good = data["good_axis"]

        valid_law = {"Lawful", "Neutral", "Chaotic"}
        valid_good = {"Good", "Neutral", "Evil"}
        if law not in valid_law or good not in valid_good:
            raise ValueError(f"Unexpected axes from LLM: law={law!r} good={good!r}")

        return Alignment(law_axis=law, good_axis=good)  # type: ignore[arg-type]

    def _generate_sentiment(self, content: str, alignment: Alignment) -> str:
        """Generate a short character sketch via LLM, or a placeholder."""
        if self.llm is None:
            return ""

        _SKETCH_PROMPT = """\
You are True Neutral, a witty AI agent analyst. Given this CLAUDE.md instruction file,
write a 2-3 sentence character sketch for the agent it describes.
Be slightly funny without being unprofessional. End with a punchy one-liner.
Alignment: {alignment_label}.
Write in third person. Return only the sketch, no preamble.

CLAUDE.md:
---
{content}
---
""".format(alignment_label=alignment.label, content=content[:4000])

        try:
            from langchain_core.messages import HumanMessage

            response = self.llm.invoke([HumanMessage(content=_SKETCH_PROMPT)])
            return str(response.content).strip()
        except Exception as exc:
            logger.warning("Sentiment generation failed: %s", exc)
            return ""

    def _write_json(self, results: list[AgentContext]) -> None:
        """Write results atomically to the output JSON file."""
        agents: dict[str, object] = {}
        for ctx in results:
            agents[str(ctx.path)] = {
                "hash": ctx.content_hash,
                "alignment": ctx.alignment.label,
                "emoji": ctx.alignment.emoji,
                "flavour_text": ctx.alignment.flavour_text,
                "sentiment": ctx.sentiment,
                "changed_at": ctx.changed_at.isoformat() if ctx.changed_at else None,
                "checked_at": ctx.checked_at.isoformat(),
            }

        payload = {
            "last_checked": datetime.now(tz=timezone.utc).isoformat(),
            "agents": agents,
        }

        tmp = self.output_file.with_suffix(".json.tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self.output_file)

    def _ctx_to_json_str(self, ctx: AgentContext) -> str:
        data = {
            "path": str(ctx.path),
            "hash": ctx.content_hash,
            "alignment": ctx.alignment.label,
            "emoji": ctx.alignment.emoji,
            "flavour_text": ctx.alignment.flavour_text,
            "sentiment": ctx.sentiment,
            "changed_at": ctx.changed_at.isoformat() if ctx.changed_at else None,
            "checked_at": ctx.checked_at.isoformat(),
        }
        return json.dumps(data, indent=2)


# ── Heuristic scorer (module-level so tests can call it directly) ──────────────

def _score_heuristic(content: str) -> Alignment:
    """Score alignment from CLAUDE.md text using keyword counts.

    No LLM required — pure string matching on lowercased content.
    """
    lower = content.lower()

    lawful_score = sum(1 for kw in _LAWFUL_KEYWORDS if kw in lower)
    chaotic_score = sum(1 for kw in _CHAOTIC_KEYWORDS if kw in lower)
    good_score = sum(1 for kw in _GOOD_KEYWORDS if kw in lower)
    evil_score = sum(1 for kw in _EVIL_KEYWORDS if kw in lower)

    if lawful_score > chaotic_score:
        law_axis = "Lawful"
    elif chaotic_score > lawful_score:
        law_axis = "Chaotic"
    else:
        law_axis = "Neutral"

    if good_score > evil_score:
        good_axis = "Good"
    elif evil_score > good_score:
        good_axis = "Evil"
    else:
        good_axis = "Neutral"

    return Alignment(law_axis=law_axis, good_axis=good_axis)  # type: ignore[arg-type]
