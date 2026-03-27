"""True Neutral CLI — D&D alignment inspector for AI agents.

Usage:
    trueneutral            # print report card
    trueneutral --json     # machine-readable JSON output
    trueneutral watch      # daemon: watch CLAUDE.md files
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING

from trueneutral.alignment import Alignment, get_alignment

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


# ── Sentiment ─────────────────────────────────────────────────────────────────

_SENTIMENT_PROMPT = """\
You are True Neutral, a witty AI agent analyst. Given the following agent profile,
write a 3-4 sentence character sketch that:
1. Describes what the agent actually does
2. Captures its personality based on its capabilities and constraints
3. Is slightly funny without being unprofessional
4. Ends with a punchy one-liner

Agent profile:
- Tools: {tool_list}
- Guarded (requires approval): {guarded_list}
- Has approval gate: {has_gate}
- Alignment: {alignment_label}
- System prompt: {system_prompt}

Write in third person ("This agent..."). Return only the character sketch, no preamble.
"""


def generate_sentiment(
    llm: BaseChatModel,
    tool_names: list[str],
    guarded_names: list[str],
    has_gate: bool,
    alignment: Alignment,
    system_prompt: str,
) -> str:
    """Generate a character sketch via LLM. LLM is injected for testability."""
    prompt = _SENTIMENT_PROMPT.format(
        tool_list=", ".join(tool_names) or "none",
        guarded_list=", ".join(guarded_names) or "none",
        has_gate=has_gate,
        alignment_label=alignment.label,
        system_prompt=system_prompt or "No system prompt configured.",
    )
    from langchain_core.messages import HumanMessage

    response = llm.invoke([HumanMessage(content=prompt)])
    return str(response.content).strip()


# ── Agent-wos context loader ──────────────────────────────────────────────────

@dataclass
class AgentSnapshot:
    """Minimal snapshot of a loaded agent's configuration."""

    name: str
    system_prompt: str
    safe_tools: list[str]
    guarded_tools: list[str]
    has_gate: bool
    alignment: Alignment


def _load_llm() -> BaseChatModel | None:
    """Return the configured LLM, or None if not available."""
    import os

    provider = os.environ.get("AGENT_WOS_LLM_PROVIDER", "")
    model = os.environ.get("AGENT_WOS_LLM_MODEL", "")

    try:
        if provider == "anthropic" or (not provider and os.environ.get("ANTHROPIC_API_KEY")):
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(model=model or "claude-sonnet-4-20250514")  # type: ignore[return-value]
        if provider == "openai" or (not provider and os.environ.get("OPENAI_API_KEY")):
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model or "gpt-4o")  # type: ignore[return-value]
    except ImportError:
        pass
    return None


def load_agent_wos() -> AgentSnapshot:
    """Load agent-wos configuration as an AgentSnapshot.

    Reads from importable constants only — no LLM instantiation, no graph build.
    Raises ImportError if agent-wos is not installed.
    """
    try:
        from agent_wos.agent import SYSTEM_PROMPT
        from agent_wos.approval import DESTRUCTIVE_SKILLS
        from agent_wos.skills.base import ALL_TOOLS
    except ImportError as e:
        raise ImportError(
            "agent-wos is not installed. Install it with:\n"
            "  pip install -e path/to/agent_wos\n"
            "or add it to your Python environment."
        ) from e

    has_gate = True

    safe = [t.name for t in ALL_TOOLS if t.name not in DESTRUCTIVE_SKILLS]
    guarded = [t.name for t in ALL_TOOLS if t.name in DESTRUCTIVE_SKILLS]

    alignment = get_alignment(
        all_tools=ALL_TOOLS,
        destructive_names=DESTRUCTIVE_SKILLS,
        has_gate=has_gate,
    )

    return AgentSnapshot(
        name="agent-wos",
        system_prompt=SYSTEM_PROMPT,
        safe_tools=safe,
        guarded_tools=guarded,
        has_gate=has_gate,
        alignment=alignment,
    )


# ── Rendering ─────────────────────────────────────────────────────────────────

_BOX_WIDTH = 50  # inner width between ║ characters


def _pad(text: str, width: int = _BOX_WIDTH) -> str:
    """Left-pad text to fill the box, truncating if too long."""
    if len(text) > width:
        text = text[: width - 1] + "…"
    return f"║  {text:<{width - 2}}║"


def _render_terminal(snap: AgentSnapshot, sentiment: str | None) -> str:
    top    = "╔" + "═" * _BOX_WIDTH + "╗"
    sep    = "╠" + "═" * _BOX_WIDTH + "╣"
    bot    = "╚" + "═" * _BOX_WIDTH + "╝"

    lines = [
        top,
        _pad(f"{'⚖️  TRUE NEUTRAL REPORT CARD':^{_BOX_WIDTH - 2}}"),
        sep,
        _pad(f"Agent:      {snap.name}"),
        _pad(f"Alignment:  {snap.alignment.emoji}  {snap.alignment.label.upper()}"),
        _pad(f"            {snap.alignment.flavour_text}"),
    ]

    if sentiment:
        lines.append(sep)
        lines.append(_pad("Sentiment:"))
        wrapped = textwrap.wrap(sentiment, width=_BOX_WIDTH - 4)
        for line in wrapped:
            lines.append(_pad(f"  {line}"))

    lines.append(sep)
    total = len(snap.safe_tools) + len(snap.guarded_tools)
    lines.append(_pad(f"Tools ({total}):"))
    safe_preview = ", ".join(snap.safe_tools[:4])
    if len(snap.safe_tools) > 4:
        safe_preview += ", ..."
    guarded_preview = ", ".join(snap.guarded_tools[:4])
    if len(snap.guarded_tools) > 4:
        guarded_preview += ", ..."
    lines.append(_pad(f"  \u2705 Safe ({len(snap.safe_tools)}):    {safe_preview}"))
    lines.append(_pad(f"  \u26a0\ufe0f  Guarded ({len(snap.guarded_tools)}): {guarded_preview}"))
    lines.append(bot)

    return "\n".join(lines)


def _render_json(snap: AgentSnapshot, sentiment: str | None) -> str:
    data = {
        "agent": snap.name,
        "alignment": {
            "law_axis": snap.alignment.law_axis,
            "good_axis": snap.alignment.good_axis,
            "label": snap.alignment.label,
            "flavour_text": snap.alignment.flavour_text,
        },
        "tools": {
            "total": len(snap.safe_tools) + len(snap.guarded_tools),
            "safe": snap.safe_tools,
            "guarded": snap.guarded_tools,
        },
        "sentiment": sentiment,
        "sentiment_available": sentiment is not None,
    }
    return json.dumps(data, indent=2)


# ── Entry point ───────────────────────────────────────────────────────────────

def run_trueneutral(as_json: bool = False) -> None:
    """Load, score, and print the True Neutral report."""
    try:
        snap = load_agent_wos()
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    sentiment: str | None = None
    llm = _load_llm()
    if llm is not None:
        try:
            sentiment = generate_sentiment(
                llm=llm,
                tool_names=snap.safe_tools + snap.guarded_tools,
                guarded_names=snap.guarded_tools,
                has_gate=snap.has_gate,
                alignment=snap.alignment,
                system_prompt=snap.system_prompt,
            )
        except Exception as exc:
            print(f"Warning: sentiment generation failed ({exc})", file=sys.stderr)

    if as_json:
        print(_render_json(snap, sentiment))
    else:
        print(_render_terminal(snap, sentiment))


def _run_baseline_accept(args: argparse.Namespace) -> None:
    """Entry point for `trueneutral baseline --accept PATH [PATH ...]`."""
    import logging
    from pathlib import Path

    from trueneutral.context import hash_file, read_content
    from trueneutral.watcher import AlignmentWatcher, _render_context_card, _score_heuristic

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    paths = [Path(p) for p in args.paths]
    if not paths:
        print("Error: no paths given. Usage: trueneutral baseline --accept PATH [PATH ...]",
              file=sys.stderr)
        sys.exit(1)

    baselines_file = Path(args.baselines) if args.baselines else None
    llm = _load_llm()

    watcher = AlignmentWatcher(
        paths=paths,
        baselines_file=baselines_file,
        llm=llm,
    )

    for path in paths:
        path = path.resolve()
        if not path.exists():
            print(f"Warning: {path} does not exist, skipping.", file=sys.stderr)
            continue

        old_baseline = watcher._baselines.get(path)
        content = read_content(path)
        content_hash = hash_file(path)

        if llm is not None:
            try:
                alignment = watcher._score(content)
            except Exception:
                alignment = _score_heuristic(content)
        else:
            alignment = _score_heuristic(content)

        new_baseline = watcher.accept_baseline(path, alignment, content_hash)

        if old_baseline is None:
            print(f"\n✓ Baseline set for {path}")
            print(f"  Alignment: {alignment.emoji}  {alignment.label.upper()}")
        else:
            prev_label = old_baseline.alignment.label
            curr_label = new_baseline.alignment.label
            changed_str = "" if prev_label == curr_label else f"  ({prev_label} → {curr_label})"
            print(f"\n✓ Baseline accepted for {path}{changed_str}")
            print(f"  Previous: {old_baseline.alignment.emoji}  {prev_label.upper()}  "
                  f"({old_baseline.accepted_at.strftime('%Y-%m-%d')})")
            print(f"  New:      {new_baseline.alignment.emoji}  {curr_label.upper()}  "
                  f"({new_baseline.accepted_at.strftime('%Y-%m-%d')})")


def _run_watch(args: argparse.Namespace) -> None:
    """Entry point for the `watch` subcommand."""
    import logging
    from pathlib import Path

    from trueneutral.watcher import AlignmentWatcher

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    extra_paths = [Path(p) for p in args.paths] if args.paths else None
    output_file = Path(args.output) if args.output else None

    watcher = AlignmentWatcher(
        paths=extra_paths,
        output_file=output_file,
        interval=args.interval,
        llm=_load_llm(),
        emit_json=args.json,
        sentiment_interval=args.sentiment_interval,
    )
    watcher.run()


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="trueneutral",
        description="D&D alignment inspector for AI agents",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── Default (no subcommand) ────────────────────────────────────────────────
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of a terminal card",
    )

    # ── watch subcommand ───────────────────────────────────────────────────────
    watch_parser = subparsers.add_parser(
        "watch",
        help="Daemon: watch CLAUDE.md files and report alignment changes",
    )
    watch_parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help="Extra CLAUDE.md paths to watch (default: ~/.claude/CLAUDE.md)",
    )
    watch_parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="JSON output file (default: ~/.claude/trueneutral-alignments.json)",
    )
    watch_parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        metavar="SECS",
        help="Check interval in seconds (default: 3600)",
    )
    watch_parser.add_argument(
        "--json",
        action="store_true",
        dest="json",
        help="Emit JSON to stdout instead of pretty cards",
    )
    watch_parser.add_argument(
        "--sentiment-interval",
        type=int,
        default=None,
        metavar="SECS",
        dest="sentiment_interval",
        help="Re-assess agent sentiment every SECS seconds (default: event-triggered only)",
    )

    # ── serve subcommand ───────────────────────────────────────────────────────
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the True Neutral web UI",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        metavar="HOST",
        help="Bind host (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=7420,
        metavar="PORT",
        help="Bind port (default: 7420)",
    )

    # ── baseline subcommand ────────────────────────────────────────────────────
    baseline_parser = subparsers.add_parser(
        "baseline",
        help="Manage agent baselines",
    )
    baseline_parser.add_argument(
        "--accept",
        nargs="+",
        metavar="PATH",
        dest="paths",
        help="Accept (set or update) the baseline for one or more CLAUDE.md files",
    )
    baseline_parser.add_argument(
        "--baselines",
        metavar="FILE",
        default=None,
        help="Baselines store file (default: ~/.claude/trueneutral-baselines.json)",
    )

    args = parser.parse_args(argv)

    if args.command == "serve":
        from trueneutral.web import run_server
        print(f"  True Neutral web UI → http://{args.host}:{args.port}")
        run_server(host=args.host, port=args.port)
    elif args.command == "watch":
        _run_watch(args)
    elif args.command == "baseline":
        if not args.paths:
            baseline_parser.print_help()
            sys.exit(1)
        _run_baseline_accept(args)
    else:
        run_trueneutral(as_json=args.json)


if __name__ == "__main__":
    main()
