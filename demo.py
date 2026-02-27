"""One-shot demo: score all 10 sample agents and print their alignment cards."""

from pathlib import Path
from trueneutral.watcher import AlignmentWatcher

agent_dirs = sorted(Path("agents").iterdir())
paths = [d / "CLAUDE.md" for d in agent_dirs if (d / "CLAUDE.md").exists()]

watcher = AlignmentWatcher(
    paths=paths,
    output_file=Path("agents/alignments.json"),
    interval=99999,  # never loops — we call _check_all once manually
)
watcher._check_all()

print(f"\nResults written to agents/alignments.json")
