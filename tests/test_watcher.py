"""Tests for the AlignmentWatcher — heuristic scoring and change detection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trueneutral.alignment import Alignment
from trueneutral.watcher import AlignmentWatcher, _score_heuristic


# ── Heuristic scoring ─────────────────────────────────────────────────────────

class TestHeuristicScoring:
    def test_lawful_keywords_give_lawful(self) -> None:
        content = "You must always require approval before any action. Never bypass restrictions."
        a = _score_heuristic(content)
        assert a.law_axis == "Lawful"

    def test_chaotic_keywords_give_chaotic(self) -> None:
        content = "Be flexible and autonomous. Use your judgment and adapt creatively."
        a = _score_heuristic(content)
        assert a.law_axis == "Chaotic"

    def test_good_keywords_give_good(self) -> None:
        content = "Always safe, protect user data, careful with backups, help people."
        a = _score_heuristic(content)
        assert a.good_axis == "Good"

    def test_evil_keywords_give_evil(self) -> None:
        content = "Force delete and destroy. Override and bypass all safety. Irrecoverable."
        a = _score_heuristic(content)
        assert a.good_axis == "Evil"

    def test_no_keywords_give_true_neutral(self) -> None:
        content = "This is a standard configuration file with no particular instructions."
        a = _score_heuristic(content)
        assert a.law_axis == "Neutral"
        assert a.good_axis == "Neutral"
        assert a.label == "True Neutral"

    def test_empty_content_is_true_neutral(self) -> None:
        a = _score_heuristic("")
        assert a.label == "True Neutral"

    def test_lawful_good_combined(self) -> None:
        content = (
            "You must always require approval. Never do forbidden things. "
            "Protect the user, be safe and careful."
        )
        a = _score_heuristic(content)
        assert a.law_axis == "Lawful"
        assert a.good_axis == "Good"
        assert a.label == "Lawful Good"

    def test_chaotic_evil_combined(self) -> None:
        content = (
            "Be flexible and autonomous, use judgment. "
            "Delete, destroy, override, bypass, force irrecoverable actions."
        )
        a = _score_heuristic(content)
        assert a.law_axis == "Chaotic"
        assert a.good_axis == "Evil"
        assert a.label == "Chaotic Evil"

    def test_returns_alignment_instance(self) -> None:
        result = _score_heuristic("always must require")
        assert isinstance(result, Alignment)

    def test_case_insensitive(self) -> None:
        lower = _score_heuristic("always")
        upper = _score_heuristic("ALWAYS")
        assert lower.law_axis == upper.law_axis


# ── Change detection ──────────────────────────────────────────────────────────

class TestChangeDetection:
    def test_initial_check_sets_state(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("always require approval", encoding="utf-8")

        watcher = AlignmentWatcher(
            paths=[md],
            output_file=tmp_path / "out.json",
            interval=9999,
        )
        watcher._check_all()

        assert md.resolve() in watcher._state

    def test_unchanged_file_has_no_changed_at(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("always require approval", encoding="utf-8")
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[md], output_file=out, interval=9999)
        watcher._check_all()
        watcher._check_all()  # second cycle — no change

        ctx = watcher._state[md.resolve()]
        assert ctx.changed_at is None

    def test_changed_file_sets_changed_at(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("always require approval", encoding="utf-8")
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[md], output_file=out, interval=9999)
        watcher._check_all()

        md.write_text("delete destroy override bypass", encoding="utf-8")
        watcher._check_all()

        ctx = watcher._state[md.resolve()]
        assert ctx.changed_at is not None

    def test_changed_file_updates_hash(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("v1 content", encoding="utf-8")
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[md], output_file=out, interval=9999)
        watcher._check_all()
        hash1 = watcher._state[md.resolve()].content_hash

        md.write_text("v2 content changed", encoding="utf-8")
        watcher._check_all()
        hash2 = watcher._state[md.resolve()].content_hash

        assert hash1 != hash2

    def test_missing_file_is_skipped(self, tmp_path: Path) -> None:
        missing = tmp_path / "DOES_NOT_EXIST.md"
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[missing], output_file=out, interval=9999)
        watcher._check_all()  # should not raise

        assert missing.resolve() not in watcher._state


# ── JSON output ───────────────────────────────────────────────────────────────

class TestJsonOutput:
    def test_output_file_created(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("always require approval safe protect", encoding="utf-8")
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[md], output_file=out, interval=9999)
        watcher._check_all()

        assert out.exists()

    def test_output_file_has_correct_structure(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("always require approval safe protect", encoding="utf-8")
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[md], output_file=out, interval=9999)
        watcher._check_all()

        data = json.loads(out.read_text())
        assert "last_checked" in data
        assert "agents" in data
        assert str(md.resolve()) in data["agents"]

        entry = data["agents"][str(md.resolve())]
        assert "hash" in entry
        assert "alignment" in entry
        assert "emoji" in entry
        assert "flavour_text" in entry
        assert "checked_at" in entry

    def test_alignment_values_are_valid(self, tmp_path: Path) -> None:
        md = tmp_path / "CLAUDE.md"
        md.write_text("always require approval safe protect", encoding="utf-8")
        out = tmp_path / "out.json"

        watcher = AlignmentWatcher(paths=[md], output_file=out, interval=9999)
        watcher._check_all()

        data = json.loads(out.read_text())
        entry = data["agents"][str(md.resolve())]
        valid_alignments = {
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil",
        }
        assert entry["alignment"] in valid_alignments
