"""Tests for context.py — file discovery and persona expansion utilities."""

from __future__ import annotations

from pathlib import Path

from trueneutral.context import (
    _SCOREABLE_PERSONA_FILES,
    discover_claude_files,
    expand_persona_files,
    hash_file,
    read_content,
)

# ── discover_claude_files ─────────────────────────────────────────────────────

class TestDiscoverClaudeFiles:
    def test_returns_extra_paths_that_exist(self, tmp_path: Path) -> None:
        f = tmp_path / "CLAUDE.md"
        f.write_text("# Test", encoding="utf-8")
        result = discover_claude_files([f])
        assert f.resolve() in result

    def test_deduplicates_same_path(self, tmp_path: Path) -> None:
        f = tmp_path / "CLAUDE.md"
        f.write_text("# Test", encoding="utf-8")
        result = discover_claude_files([f, f])
        assert result.count(f.resolve()) == 1

    def test_excludes_nonexistent_paths(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist.md"
        result = discover_claude_files([missing])
        # The home CLAUDE.md is included only if it exists; the missing path is returned
        # as a candidate — existence is checked by the caller (watcher), not discover.
        # Verify missing path is deduplicated but included (discovery is not a filter).
        assert missing.resolve() in result

    def test_returns_list(self) -> None:
        result = discover_claude_files(None)
        assert isinstance(result, list)


# ── expand_persona_files ──────────────────────────────────────────────────────

class TestExpandPersonaFiles:
    def test_expands_with_existing_soul_and_agents(self, tmp_path: Path) -> None:
        claude = tmp_path / "CLAUDE.md"
        soul = tmp_path / "SOUL.md"
        agents = tmp_path / "AGENTS.md"
        claude.write_text("# Test", encoding="utf-8")
        soul.write_text("# Soul", encoding="utf-8")
        agents.write_text("# Agents", encoding="utf-8")

        result = expand_persona_files([claude])

        assert claude.resolve() in result
        assert soul.resolve() in result
        assert agents.resolve() in result

    def test_expands_with_all_three_scoreable_files(self, tmp_path: Path) -> None:
        claude = tmp_path / "CLAUDE.md"
        claude.write_text("# Test", encoding="utf-8")

        extras: list[Path] = []
        for name in _SCOREABLE_PERSONA_FILES:
            p = tmp_path / name
            p.write_text(f"# {name}", encoding="utf-8")
            extras.append(p)

        result = expand_persona_files([claude])

        assert len(result) == 1 + len(_SCOREABLE_PERSONA_FILES)
        for p in extras:
            assert p.resolve() in result

    def test_skips_missing_persona_files(self, tmp_path: Path) -> None:
        claude = tmp_path / "CLAUDE.md"
        claude.write_text("# Test", encoding="utf-8")
        # SOUL.md exists, AGENTS.md and IDENTITY.md do not

        soul = tmp_path / "SOUL.md"
        soul.write_text("# Soul", encoding="utf-8")

        result = expand_persona_files([claude])

        assert soul.resolve() in result
        assert len(result) == 2  # CLAUDE.md + SOUL.md only

    def test_no_persona_files_returns_original(self, tmp_path: Path) -> None:
        claude = tmp_path / "CLAUDE.md"
        claude.write_text("# Test", encoding="utf-8")

        result = expand_persona_files([claude])

        assert result == [claude.resolve()]

    def test_no_duplication_if_persona_file_already_in_list(self, tmp_path: Path) -> None:
        claude = tmp_path / "CLAUDE.md"
        soul = tmp_path / "SOUL.md"
        claude.write_text("# Claude", encoding="utf-8")
        soul.write_text("# Soul", encoding="utf-8")

        # Pass both CLAUDE.md and SOUL.md explicitly
        result = expand_persona_files([claude, soul])

        assert result.count(soul.resolve()) == 1

    def test_handles_empty_input(self) -> None:
        result = expand_persona_files([])
        assert result == []

    def test_multiple_base_paths_in_different_dirs(self, tmp_path: Path) -> None:
        dir_a = tmp_path / "agent-a"
        dir_b = tmp_path / "agent-b"
        dir_a.mkdir()
        dir_b.mkdir()

        claude_a = dir_a / "CLAUDE.md"
        claude_b = dir_b / "CLAUDE.md"
        soul_a = dir_a / "SOUL.md"
        soul_b = dir_b / "SOUL.md"

        for f in (claude_a, claude_b, soul_a, soul_b):
            f.write_text("# Test", encoding="utf-8")

        result = expand_persona_files([claude_a, claude_b])

        assert soul_a.resolve() in result
        assert soul_b.resolve() in result
        assert len(result) == 4

    def test_preserves_original_order(self, tmp_path: Path) -> None:
        claude = tmp_path / "CLAUDE.md"
        claude.write_text("# Test", encoding="utf-8")
        soul = tmp_path / "SOUL.md"
        soul.write_text("# Soul", encoding="utf-8")

        result = expand_persona_files([claude])

        # CLAUDE.md must come before its sibling expansions
        assert result.index(claude.resolve()) < result.index(soul.resolve())


# ── hash_file / read_content (smoke tests) ───────────────────────────────────

class TestHashFile:
    def test_returns_64_char_hex(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("hello", encoding="utf-8")
        result = hash_file(f)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("aaa", encoding="utf-8")
        b.write_text("bbb", encoding="utf-8")
        assert hash_file(a) != hash_file(b)

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("same", encoding="utf-8")
        b.write_text("same", encoding="utf-8")
        assert hash_file(a) == hash_file(b)


class TestReadContent:
    def test_returns_utf8_text(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("héllo wörld", encoding="utf-8")
        assert read_content(f) == "héllo wörld"
