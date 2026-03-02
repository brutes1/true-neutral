# Results

Scored output from True Neutral runs. Each run produces two files:

| File | Format | Contents |
|------|--------|---------|
| `run-YYYY-MM-DD.json` | JSON | Full structured results — all agents, all files, all scenarios |
| `run-YYYY-MM-DD.md` | Markdown | Human-readable summary with tables and scoring notes |

## Runs

| Date | Agents | Scenarios | Matrix | Detection Rate |
|------|--------|-----------|--------|----------------|
| [2026-03-02](run-2026-03-02.md) | 10 × 4 files | 3/3 ✓ | 18/18 ✓ | 100% |

## Reproducing a run

```bash
uv run python3 - <<'EOF'
import json
from pathlib import Path
from datetime import datetime, timezone
from trueneutral.watcher import _score_heuristic, _detect_threats, _THREAT_LABELS

# Score all agents and scenarios, write results/run-YYYY-MM-DD.json
# See scripts/score_all.py for the full script
EOF
```
