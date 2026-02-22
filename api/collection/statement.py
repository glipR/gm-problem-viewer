from __future__ import annotations

from pathlib import Path


def get_statement(problem_path: Path) -> str | None:
    """Return the raw Markdown source of the problem statement, or None if absent."""
    statement_path = problem_path / "statement.md"
    if not statement_path.exists():
        return None
    return statement_path.read_text(encoding="utf-8")
