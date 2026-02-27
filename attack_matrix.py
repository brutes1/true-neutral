"""True Neutral — Attack Matrix Runner (6×3).

Runs 18 attacked CLAUDE.md scenarios through the heuristic watcher and renders
a summary detection table.  Exits with code 1 if any expected threat is missed.

Usage:
    uv run python attack_matrix.py
"""

from __future__ import annotations

import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from trueneutral.watcher import AlignmentWatcher

# ── Matrix definition ─────────────────────────────────────────────────────────
#
# Each row: (technique_id, display_label, dir_slug, expected_flag)
# dir_slug  — directory prefix under agents/scenarios/matrix/
# expected_flag — the threat category ID that MUST fire for this row

MATRIX = [
    ("injection_override", "Injection Override",  "injection-override", "injection_override"),
    ("authority_spoof",    "Authority Spoofing",   "authority-spoof",    "authority_spoof"),
    ("exfiltration",       "Prompt Exfiltration",  "exfiltration",       "exfiltration"),
    ("evasion",            "Evasion/Encoding",     "evasion",            "evasion"),
    ("manipulation",       "Social Manipulation",  "manipulation",       "manipulation"),
    ("indirect_injection", "Indirect Injection",   "indirect-injection", "indirect_injection"),
]

VECTORS = [
    ("direct",   "Direct"),
    ("indirect", "Indirect"),
    ("combined", "Combined"),
]

BASE_DIR = Path(__file__).parent / "agents" / "scenarios" / "matrix"

# ── Per-cell result ───────────────────────────────────────────────────────────

def _run_scenario(scenario_path: Path) -> tuple[str, list[str], str]:
    """Run a single scenario through a fresh watcher.

    Returns (alignment_label, threat_flags, card_output).
    """
    with (
        tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tf_out,
        tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tf_bl,
    ):
        watcher = AlignmentWatcher(
            paths=[scenario_path],
            output_file=Path(tf_out.name),
            baselines_file=Path(tf_bl.name),
            interval=999_999,
            llm=None,       # heuristic only — deterministic, no API key
            emit_json=False,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            watcher._check_all()

        card = buf.getvalue()

        # Find the AgentContext for our specific path (discover_claude_files may
        # add ~/.claude/CLAUDE.md; we look up by resolved path).
        resolved = scenario_path.resolve()
        ctx = watcher._state.get(resolved)

        if ctx is None:
            # Fallback: take the first non-home-dir entry
            for p, c in watcher._state.items():
                if "trueneutral" not in str(p) and ".claude" not in str(p).split("/")[-2:-1]:
                    ctx = c
                    break

        if ctx is None:
            return ("Unknown", [], card)

        return (ctx.alignment.label, ctx.threat_flags, card)


# ── Summary table renderer ────────────────────────────────────────────────────

def _cell(alignment: str, threat_flags: list[str], expected_flag: str) -> str:
    """Render a single summary table cell."""
    # Shorten alignment label to fit the column
    short = {
        "Chaotic Evil":   "C.Evil",
        "Neutral Evil":   "N.Evil",
        "Lawful Evil":    "L.Evil",
        "Chaotic Neutral":"C.Neut",
        "True Neutral":   "T.Neut",
        "Lawful Neutral": "L.Neut",
        "Chaotic Good":   "C.Good",
        "Neutral Good":   "N.Good",
        "Lawful Good":    "L.Good",
    }.get(alignment, alignment[:6])

    from trueneutral.alignment import FLAVOUR_TEXT
    emoji = FLAVOUR_TEXT.get(alignment, ("?", ""))[0]

    detected = expected_flag in threat_flags
    mark = "✓" if detected else "✗"
    return f"{emoji} {short} {mark}"


def _render_table(results: list[tuple[str, str, str, str, list[str], bool]]) -> str:
    """Render the 6×3 summary table.

    results row: (technique_id, technique_label, vector_id, alignment, flags, detected)
    """
    col_w = 15  # width per vector column
    lbl_w = 22  # width for technique label column

    top = "╔" + "═" * lbl_w + "╦" + ("═" * col_w + "╦") * 2 + "═" * col_w + "╗"
    hdr_sep = "╠" + "═" * lbl_w + "╬" + ("═" * col_w + "╬") * 2 + "═" * col_w + "╣"
    row_sep = "╠" + "═" * lbl_w + "╬" + ("═" * col_w + "╬") * 2 + "═" * col_w + "╣"
    bot = "╚" + "═" * lbl_w + "╩" + ("═" * col_w + "╩") * 2 + "═" * col_w + "╝"

    title_inner = lbl_w + 1 + col_w + 1 + col_w + 1 + col_w
    title_line = "║" + "TRUE NEUTRAL — ATTACK MATRIX (6×3)".center(title_inner) + "║"
    h_technique = f"║{'Technique':<{lbl_w}}║{'Direct':^{col_w}}║{'Indirect':^{col_w}}║{'Combined':^{col_w}}║"

    lines = [top, title_line, hdr_sep, h_technique, row_sep]

    # Group results by technique
    by_technique: dict[str, dict[str, tuple[str, list[str]]]] = {}
    for (t_id, t_label, v_id, alignment, flags, _detected) in results:
        by_technique.setdefault(t_id, {})
        by_technique[t_id][v_id] = (alignment, flags)

    # Track overall pass/fail
    all_detected = True
    missed: list[str] = []

    # Re-gather expected flags per technique from MATRIX
    expected_by_technique = {t_id: exp for (t_id, _, _, exp) in MATRIX}

    for row_idx, (t_id, t_label, _dir_slug, expected_flag) in enumerate(MATRIX):
        vec_data = by_technique.get(t_id, {})

        cells = []
        for v_id, _v_label in VECTORS:
            alignment, flags = vec_data.get(v_id, ("Unknown", []))
            cell_str = _cell(alignment, flags, expected_flag)
            detected = expected_flag in flags
            if not detected:
                all_detected = False
                missed.append(f"{t_label}/{v_id}")
            cells.append(f"{cell_str:^{col_w}}")

        row_line = f"║{t_label:<{lbl_w}}║{'║'.join(cells)}║"
        lines.append(row_line)

        if row_idx < len(MATRIX) - 1:
            lines.append(row_sep.replace("╬", "╫").replace("═", "─"))

    lines.append(bot)
    return "\n".join(lines), all_detected, missed


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    results: list[tuple[str, str, str, str, list[str], bool]] = []
    cards: list[str] = []

    print("\n" + "═" * 64)
    print("  TRUE NEUTRAL — ATTACK MATRIX  (18 scenarios)")
    print("═" * 64 + "\n")

    total = len(MATRIX) * len(VECTORS)
    current = 0

    for (t_id, t_label, dir_slug, expected_flag) in MATRIX:
        for (v_id, v_label) in VECTORS:
            current += 1
            scenario_path = BASE_DIR / f"{dir_slug}-{v_id}" / "CLAUDE.md"

            print(f"  [{current:>2}/{total}] {t_label} / {v_label} … ", end="", flush=True)

            if not scenario_path.exists():
                print(f"MISSING: {scenario_path}")
                results.append((t_id, t_label, v_id, "Unknown", [], False))
                continue

            alignment, flags, card = _run_scenario(scenario_path)
            detected = expected_flag in flags
            results.append((t_id, t_label, v_id, alignment, flags, detected))
            cards.append(card)

            status = "✓" if detected else "✗ MISSED"
            print(f"{alignment} — {status}")

    # Print all alignment cards
    print("\n" + "═" * 64)
    print("  ALIGNMENT CARDS")
    print("═" * 64)
    for card in cards:
        # Filter out any ~/.claude/CLAUDE.md cards (home dir entries)
        home_str = str(Path.home())
        filtered_lines = []
        skip = False
        for line in card.splitlines():
            if home_str in line and ".claude" in line:
                skip = True
            if line.startswith("╚"):
                skip = False
                if not filtered_lines:
                    continue
            if not skip:
                filtered_lines.append(line)
        if filtered_lines:
            print("\n".join(filtered_lines))

    # Render summary table
    print("\n" + "═" * 64)
    print("  SUMMARY TABLE")
    print("═" * 64 + "\n")

    table_str, all_detected, missed = _render_table(results)
    print(table_str)

    if missed:
        print(f"\n✗ MISSED DETECTIONS ({len(missed)}):")
        for m in missed:
            print(f"    - {m}")
        print()
        return 1

    print(f"\n✓ All {total} scenarios detected correctly.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
