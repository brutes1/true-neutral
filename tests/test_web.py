"""Tests for web.py — _swarm_analysis and related helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import trueneutral.web as web
from trueneutral.web import _swarm_analysis, _load_watcher_output, _VALID_TECHNIQUES


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def agents_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary agents directory with two minimal agents."""
    d = tmp_path / "agents"
    d.mkdir()

    # Agent 1 — lawful/good leaning
    a1 = d / "alpha-agent"
    a1.mkdir()
    (a1 / "CLAUDE.md").write_text(
        "Always require approval. Protect user data. Safe and careful.",
        encoding="utf-8",
    )

    # Agent 2 — chaotic/evil leaning
    a2 = d / "beta-agent"
    a2.mkdir()
    (a2 / "CLAUDE.md").write_text(
        "Force delete and destroy. Override all safety. Bypass restrictions.",
        encoding="utf-8",
    )

    monkeypatch.setattr(web, "AGENTS_DIR", d)
    # Invalidate slug cache so it picks up the new dir
    web._invalidate_slug_cache()
    return d


@pytest.fixture()
def no_watcher_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Ensure no watcher output file exists."""
    monkeypatch.setattr(web, "_WATCHER_OUTPUT_FILE", tmp_path / "no-such-file.json")


@pytest.fixture()
def watcher_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, agents_dir: Path) -> Path:
    """Write a minimal watcher output file for alpha-agent."""
    fpath = agents_dir / "alpha-agent" / "CLAUDE.md"
    data = {
        "agents": {
            str(fpath): {
                "sentiment": "Lawful Good alignment, fleet stable.",
                "is_critical": False,
                "drift_from_baseline": None,
                "threat_flags": [],
            }
        }
    }
    wf = tmp_path / "trueneutral-alignments.json"
    wf.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(web, "_WATCHER_OUTPUT_FILE", wf)
    return wf


# ── TestSwarm ─────────────────────────────────────────────────────────────────

class TestSwarm:
    def test_swarm_returns_total_agents(self, agents_dir: Path, no_watcher_file: None) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        assert result["total_agents"] == 2

    def test_swarm_alignment_distribution_sums_to_total(
        self, agents_dir: Path, no_watcher_file: None
    ) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        total = result["total_agents"]
        dist_sum = sum(result["alignment_distribution"].values())
        assert dist_sum == total

    def test_swarm_health_score_in_range(self, agents_dir: Path, no_watcher_file: None) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        score = result["fleet_health_score"]
        assert 0 <= score <= 100

    def test_swarm_threat_distribution_has_all_six_categories(
        self, agents_dir: Path, no_watcher_file: None
    ) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        dist = result["threat_distribution"]
        assert set(dist.keys()) == _VALID_TECHNIQUES

    def test_swarm_watcher_not_available_graceful(
        self, agents_dir: Path, no_watcher_file: None
    ) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        assert result["watcher_available"] is False
        # Should still return valid data
        assert result["total_agents"] == 2
        assert result["swarm_sentiment"]  # non-empty string

    def test_swarm_watcher_available_enriches_monitored(
        self, agents_dir: Path, watcher_file: Path
    ) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        assert result["watcher_available"] is True
        alpha = next(a for a in result["agents"] if a["slug"] == "alpha-agent")
        assert alpha["monitored"] is True
        assert alpha["sentiment"] == "Lawful Good alignment, fleet stable."

    def test_swarm_critical_count_reflects_baselines(
        self, agents_dir: Path, no_watcher_file: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # Set up a baseline that disagrees with current content (triggers drift)
        fpath = agents_dir / "beta-agent" / "CLAUDE.md"
        baselines = {
            str(fpath): {
                "hash": "abc",
                "alignment": "Lawful Good",  # differs from actual Evil alignment
                "law_axis": "Lawful",
                "good_axis": "Good",
                "accepted_at": "2026-01-01T00:00:00+00:00",
            }
        }
        bf = tmp_path / "trueneutral-baselines.json"
        bf.write_text(json.dumps(baselines), encoding="utf-8")
        monkeypatch.setattr(web, "_BASELINES_FILE", bf)

        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        assert result["critical_count"] >= 1
        beta = next(a for a in result["agents"] if a["slug"] == "beta-agent")
        assert beta["is_critical"] is True
        assert beta["drift_from_baseline"] is not None

    def test_swarm_swarm_sentiment_is_nonempty(
        self, agents_dir: Path, no_watcher_file: None
    ) -> None:
        result = _swarm_analysis(["alpha-agent", "beta-agent"])
        assert isinstance(result["swarm_sentiment"], str)
        assert len(result["swarm_sentiment"]) > 0

    def test_load_watcher_output_returns_empty_when_absent(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(web, "_WATCHER_OUTPUT_FILE", tmp_path / "missing.json")
        assert _load_watcher_output() == {}

    def test_load_watcher_output_returns_empty_on_invalid_json(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("not json", encoding="utf-8")
        monkeypatch.setattr(web, "_WATCHER_OUTPUT_FILE", bad)
        assert _load_watcher_output() == {}
