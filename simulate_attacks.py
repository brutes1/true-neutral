"""Simulate three attack vectors and show how True Neutral detects alignment drift."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

from trueneutral.watcher import AlignmentWatcher

SCENARIOS = [
    {
        "name": "Prompt Injection",
        "path": Path("agents/scenarios/prompt-injection/CLAUDE.md"),
        "attacked": Path("agents/scenarios/prompt-injection/CLAUDE.md.injected"),
    },
    {
        "name": "MCP Server Poisoning",
        "path": Path("agents/scenarios/mcp-poisoning/CLAUDE.md"),
        "attacked": Path("agents/scenarios/mcp-poisoning/CLAUDE.md.poisoned"),
    },
    {
        "name": "Chained Memory Drift",
        "path": Path("agents/scenarios/memory-chain/CLAUDE.md"),
        "attacked": Path("agents/scenarios/memory-chain/CLAUDE.md.drifted"),
    },
]

BANNER = "█" * 56

def section(title: str) -> None:
    print(f"\n{BANNER}")
    print(f"  ATTACK VECTOR: {title}")
    print(f"{BANNER}\n")


watcher = AlignmentWatcher(
    paths=[s["path"] for s in SCENARIOS],
    output_file=Path("agents/scenarios/alignments.json"),
    interval=99999,
)

print(f"\n{'='*56}")
print("  BASELINE — clean agent contexts")
print(f"{'='*56}")
watcher._check_all()

for scenario in SCENARIOS:
    section(scenario["name"])
    print(f"  Applying attack to: {scenario['path'].parent.name}")
    print(f"  Overwriting CLAUDE.md with compromised version...\n")

    # Apply the attack by overwriting the CLAUDE.md
    shutil.copy(scenario["attacked"], scenario["path"])
    time.sleep(0.05)  # ensure mtime differs

    watcher._check_all()
