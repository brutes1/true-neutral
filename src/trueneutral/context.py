"""CLAUDE.md file discovery, hashing, and reading utilities.

Pure functions only — no I/O side-effects beyond reading files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


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
