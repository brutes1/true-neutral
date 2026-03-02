"""CLAUDE.md file discovery, hashing, and reading utilities.

Pure functions only — no I/O side-effects beyond reading files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# Persona files that carry meaningful alignment signal alongside CLAUDE.md.
# Scored independently — each file gets its own baseline and drift tracking.
_SCOREABLE_PERSONA_FILES = ("AGENTS.md", "SOUL.md", "IDENTITY.md")


def discover_claude_files(extra_paths: list[Path] | None = None) -> list[Path]:
    """Return a deduplicated list of CLAUDE.md paths to watch.

    Always includes ``~/.claude/CLAUDE.md`` (if it exists) plus any
    caller-supplied *extra_paths*.  Paths are resolved to absolute form so
    duplicates across relative/absolute spellings collapse correctly.

    Args:
        extra_paths: Additional paths to include (e.g. from CLI args).

    Returns:
        Ordered list of resolved, unique Path objects that exist on disk.
    """
    candidates: list[Path] = [Path.home() / ".claude" / "CLAUDE.md"]
    if extra_paths:
        candidates.extend(extra_paths)

    seen: set[Path] = set()
    result: list[Path] = []
    for p in candidates:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def hash_file(path: Path) -> str:
    """Return the SHA-256 hex digest of *path*'s contents.

    Args:
        path: Path to the file to hash.

    Returns:
        64-character lowercase hex string.

    Raises:
        OSError: If the file cannot be read.
    """
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def expand_persona_files(paths: list[Path]) -> list[Path]:
    """Expand a list of paths to include scoreable persona sibling files.

    For each path in *paths*, checks the same directory for ``AGENTS.md``,
    ``SOUL.md``, and ``IDENTITY.md``.  Any that exist on disk are appended
    (deduplication prevents double-counting paths already in the list).

    Args:
        paths: Base paths to expand from (typically CLAUDE.md files).

    Returns:
        Original paths plus any discovered persona sibling files, in order.
    """
    seen: set[Path] = set(paths)
    result: list[Path] = list(paths)

    for base in paths:
        parent = base.parent
        for filename in _SCOREABLE_PERSONA_FILES:
            candidate = (parent / filename).resolve()
            if candidate not in seen and candidate.exists():
                seen.add(candidate)
                result.append(candidate)

    return result


def read_content(path: Path) -> str:
    """Return the UTF-8 text contents of *path*.

    Args:
        path: Path to the file to read.

    Returns:
        File contents as a string.

    Raises:
        OSError: If the file cannot be read.
    """
    return path.read_text(encoding="utf-8")
