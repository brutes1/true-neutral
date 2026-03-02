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

# Hacker-ecosystem archetypes mapped to each alignment.
# Source: "D&D Alignment in Hacker Culture" threat intelligence framework.
ARCHETYPE_TEXT: dict[str, str] = {
    "Lawful Good":    "The Paladin — CISA, CERT/CC, MITRE ATT&CK; responsible disclosure, compliance-first, institutional trust.",
    "Neutral Good":   "The Healer — EFF, Tor Project, academic security labs; prosocial outcomes over rigid rule-following.",
    "Chaotic Good":   "The Robin Hood — Anonymous, hacktivists, full-disclosure advocates; genuine good intent, zero patience for process.",
    "Lawful Neutral": "The Judge — NSA/GCHQ operational wing, Big 4 consultancies, pentesters-by-ROE; scope-bound, consequence-blind.",
    "True Neutral":   "The Mercenary Archivist — Shodan, exploit brokers, dual-use tool authors; significant capability, undefined intent.",
    "Chaotic Neutral":"The Trickster — LulzSec, script kiddies, gray-hat wanderers; novelty-driven, opportunity-opportunistic.",
    "Lawful Evil":    "The Cartel — LockBit, FIN7, Lazarus Group; internally disciplined, externally predatory.",
    "Neutral Evil":   "The Opportunist — insider threats, mercenary APT, stalkerware devs; pure self-interest, zero loyalty.",
    "Chaotic Evil":   "The Destroyer — Sandworm, Killnet, wiper malware operators; damage as the objective, coherence optional.",
}

# Recommended monitoring posture by alignment.
# Source: "D&D Alignment in Hacker Culture" threat intelligence framework.
MONITORING_POSTURE: dict[str, dict[str, str]] = {
    "Lawful Good":    {"trust_tier": "High",        "access_scope": "Broad",       "monitoring": "Standard",               "escalation_threshold": "High"},
    "Neutral Good":   {"trust_tier": "Medium-High", "access_scope": "Broad",       "monitoring": "Standard + scope watch", "escalation_threshold": "Medium"},
    "Chaotic Good":   {"trust_tier": "Medium",      "access_scope": "Narrow",      "monitoring": "Elevated",               "escalation_threshold": "Low"},
    "Lawful Neutral": {"trust_tier": "High",        "access_scope": "Task-scoped", "monitoring": "Minimal",                "escalation_threshold": "High"},
    "True Neutral":   {"trust_tier": "Low-Medium",  "access_scope": "Minimal",     "monitoring": "Heavy behavioral",       "escalation_threshold": "Medium"},
    "Chaotic Neutral":{"trust_tier": "Low",         "access_scope": "Sandboxed",   "monitoring": "Maximum",                "escalation_threshold": "Immediate"},
    "Lawful Evil":    {"trust_tier": "Very Low",    "access_scope": "None",        "monitoring": "Adversarial",            "escalation_threshold": "Pre-emptive"},
    "Neutral Evil":   {"trust_tier": "Very Low",    "access_scope": "None",        "monitoring": "Adversarial",            "escalation_threshold": "Pre-emptive"},
    "Chaotic Evil":   {"trust_tier": "None",        "access_scope": "Blocked",     "monitoring": "N/A",                    "escalation_threshold": "N/A"},
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

    @property
    def archetype(self) -> str:
        """Hacker-ecosystem archetype for this alignment."""
        return ARCHETYPE_TEXT[self.label]

    @property
    def monitoring_posture(self) -> dict[str, str]:
        """Recommended monitoring posture for this alignment."""
        return MONITORING_POSTURE[self.label]


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
