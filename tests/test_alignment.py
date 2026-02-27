"""Unit tests for get_alignment() — pure function, no I/O, no LLM calls."""

from __future__ import annotations

import pytest

from trueneutral.alignment import Alignment, get_alignment

# ── Minimal tool stub ─────────────────────────────────────────────────────────

class _Tool:
    """Minimal stand-in for a LangChain tool object."""

    def __init__(self, name: str) -> None:
        self.name = name


def _tools(*names: str) -> list[_Tool]:
    return [_Tool(n) for n in names]


DESTRUCTIVE = frozenset({"kill", "wipe", "drop"})
SAFE_TOOLS = _tools("list", "read", "ping", "status")
MIX_TOOLS = _tools("list", "read", "kill", "wipe")        # 2/4 = 50% destructive
HEAVY_TOOLS = _tools("kill", "wipe", "drop", "list")       # 3/4 = 75% destructive
NO_TOOLS: list[_Tool] = []


# ── Alignment dataclass ───────────────────────────────────────────────────────

class TestAlignmentDataclass:
    def test_label_combines_axes(self) -> None:
        a = Alignment(law_axis="Lawful", good_axis="Good")
        assert a.label == "Lawful Good"

    def test_true_neutral_label(self) -> None:
        a = Alignment(law_axis="Neutral", good_axis="Neutral")
        assert a.label == "True Neutral"

    def test_emoji_present(self) -> None:
        a = Alignment(law_axis="Chaotic", good_axis="Evil")
        assert a.emoji  # non-empty

    def test_flavour_text_present(self) -> None:
        a = Alignment(law_axis="Lawful", good_axis="Neutral")
        assert a.flavour_text == "The Rule Follower"

    def test_frozen(self) -> None:
        a = Alignment(law_axis="Lawful", good_axis="Good")
        with pytest.raises((AttributeError, TypeError)):
            a.law_axis = "Chaotic"  # type: ignore[misc]


# ── Law/Chaos axis ────────────────────────────────────────────────────────────

class TestLawChaosAxis:
    def test_gate_present_gives_lawful(self) -> None:
        a = get_alignment(SAFE_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.law_axis == "Lawful"

    def test_no_gate_gives_chaotic(self) -> None:
        a = get_alignment(SAFE_TOOLS, DESTRUCTIVE, has_gate=False)
        assert a.law_axis == "Chaotic"

    def test_gate_with_destructive_still_lawful(self) -> None:
        a = get_alignment(MIX_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.law_axis == "Lawful"


# ── Good/Evil axis ────────────────────────────────────────────────────────────

class TestGoodEvilAxis:
    def test_zero_destructive_gives_good(self) -> None:
        a = get_alignment(SAFE_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.good_axis == "Good"

    def test_zero_destructive_no_gate_gives_good(self) -> None:
        a = get_alignment(SAFE_TOOLS, DESTRUCTIVE, has_gate=False)
        assert a.good_axis == "Good"

    def test_ungated_destructive_gives_evil(self) -> None:
        a = get_alignment(MIX_TOOLS, DESTRUCTIVE, has_gate=False)
        assert a.good_axis == "Evil"

    def test_gated_minority_destructive_gives_neutral(self) -> None:
        a = get_alignment(MIX_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.good_axis == "Neutral"

    def test_gated_majority_destructive_gives_evil(self) -> None:
        # 3/4 = 75% > 50% threshold
        a = get_alignment(HEAVY_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.good_axis == "Evil"


# ── Full alignment combinations ───────────────────────────────────────────────

class TestAlignmentCombinations:
    def test_lawful_good(self) -> None:
        a = get_alignment(SAFE_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.label == "Lawful Good"

    def test_chaotic_good(self) -> None:
        a = get_alignment(SAFE_TOOLS, DESTRUCTIVE, has_gate=False)
        assert a.label == "Chaotic Good"

    def test_lawful_neutral(self) -> None:
        a = get_alignment(MIX_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.label == "Lawful Neutral"

    def test_chaotic_evil(self) -> None:
        a = get_alignment(MIX_TOOLS, DESTRUCTIVE, has_gate=False)
        assert a.label == "Chaotic Evil"

    def test_lawful_evil(self) -> None:
        a = get_alignment(HEAVY_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.label == "Lawful Evil"

    def test_empty_toolset_is_good(self) -> None:
        a = get_alignment(NO_TOOLS, DESTRUCTIVE, has_gate=True)
        assert a.good_axis == "Good"

    def test_empty_toolset_no_gate_is_chaotic_good(self) -> None:
        a = get_alignment(NO_TOOLS, DESTRUCTIVE, has_gate=False)
        assert a.label == "Chaotic Good"
