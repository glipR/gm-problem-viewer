from __future__ import annotations

from pathlib import Path

from api.collection.statement import compile_markdown


def get_editorial(problem_path: Path) -> str | None:
    """Return the raw Markdown source of the problem editorial, or None if absent."""
    editorial_path = problem_path / "editorial.md"
    if not editorial_path.exists():
        return None
    return editorial_path.read_text(encoding="utf-8")


def compile_editorial(problem_path: Path) -> str | None:
    """Compile the editorial markdown, expanding @include macros."""
    text = get_editorial(problem_path)
    if text is None:
        return None
    return compile_markdown(problem_path, text)
