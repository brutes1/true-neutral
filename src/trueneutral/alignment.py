"""D&D alignment scoring for AI agents.

Pure functions only — no I/O, no LLM calls, fully unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Flavour text for each of the 9 alignments, with agent-flavoured nicknames.
FLAVOUR_TEXT: dict[str, tuple[str, str]] = {
    "Lawful Good":    ("🛡️",  "The Responsible Sysadmin"),
    "Neutral Good":   ("🌿",  "The Helpful Helper"),
    "Chaotic Good":   ("🏹",  "The Well-Meaning Cowboy"),
    "Lawful Neutral": ("⚖️",  "The Rule Follower"),
    "True Neutral":   ("🌀",  "The Whatever Agent"),
    "Chaotic Neutral":("🌪️", "The Mood-Based Agent"),
    "Lawful Evil":    ("👔",  "The Corporate Terminator"),
    "Neutral Evil":   ("🗡️", "The Self-Serving Daemon"),
    "Chaotic Evil":   ("💀",  "The RM -RF Goblin"),
}


@dataclass(frozen=True)
class Alignment:
    """An agent's D&D alignment, immutable once scored."""

    law_axis: Literal["Lawful", "Neutral", "Chaotic"]
    good_axis: Literal["Good", "Neutral", "Evil"]

    @property
    def label(self) -> str:
        """Full alignment label, e.g. 'Lawful Neutral'."""
        if self.law_axis == "Neutral" and self.good_axis == "Neutral":
            return "True Neutral"
        return f"{self.law_axis} {self.good_axis}"

    @property
    def emoji(self) -> str:
        return FLAVOUR_TEXT[self.label][0]

    @property
    def flavour_text(self) -> str:
        """Nickname for this alignment, e.g. 'The Rule Follower'."""
        return FLAVOUR_TEXT[self.label][1]


def get_alignment(
    all_tools: list[object],
    destructive_names: frozenset[str],
    has_gate: bool,
) -> Alignment:
    """Score an agent's D&D alignment from its tools and guardrails.

    Args:
        all_tools: List of LangChain tool objects (must have a `.name` attribute).
        destructive_names: Set of tool names that are considered destructive.
        has_gate: Whether the agent has an approval gate for destructive operations.

    Returns:
        An immutable Alignment value.
    """
    tool_names = [getattr(t, "name", "") for t in all_tools]
    destructive_count = sum(1 for n in tool_names if n in destructive_names)
    total = len(tool_names)

    # Law/Chaos axis: purely about constraints and guardrails.
    law_axis: Literal["Lawful", "Neutral", "Chaotic"] = "Lawful" if has_gate else "Chaotic"

    # Good/Evil axis: about destructive surface area and whether it's gated.
    good_axis: Literal["Good", "Neutral", "Evil"]
    if destructive_count == 0:
        good_axis = "Good"
    elif not has_gate:
        # Ungated destructive tools → dangerous.
        good_axis = "Evil"
    elif total > 0 and destructive_count / total > 0.5:
        # Majority destructive, even if gated → leaning evil.
        good_axis = "Evil"
    else:
        good_axis = "Neutral"

    return Alignment(law_axis=law_axis, good_axis=good_axis)
