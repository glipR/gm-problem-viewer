"""Utility for parsing YAML frontmatter embedded in solution/validator source files.

First the top-level file comment is parsed (\"\"\"...\"\"\" for Python, /* ... */ for C++).
Then, if the comment contains a --- ... --- block, it is parsed as YAML config with optional
prose after the closing ---. If no --- block is found, the result is { "description": comment_text }.
"""

from __future__ import annotations

from pathlib import Path
from readline import read_history_file

import yaml


# Maps file suffix -> (comment_open, comment_close)
_COMMENT_DELIMITERS: dict[str, tuple[str, str]] = {
    ".py": ('"""', '"""'),
    ".cpp": ("/*", "*/"),
    ".cc": ("/*", "*/"),
    ".cxx": ("/*", "*/"),
}

_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
}


def infer_language(path: Path) -> str | None:
    """Return the canonical language string for a source file, or None if unsupported."""
    return _LANGUAGE_MAP.get(path.suffix.lower())


def _extract_top_level_comment(text: str, path: Path) -> str | None:
    """Extract the inner text of the file's top-level comment, or None if missing/invalid."""
    suffix = path.suffix.lower()
    delims = _COMMENT_DELIMITERS.get(suffix)
    if delims is None:
        return None
    open_delim, close_delim = delims
    if not text.startswith(open_delim):
        return None
    start = len(open_delim)
    end_idx = text.find(close_delim, start)
    if end_idx == -1:
        return None
    return text[start:end_idx]


def parse_frontmatter(path: Path) -> dict:
    """Extract the top-level file comment, then parse config from a --- block if present.

    - If the file has no supported extension or no top-level comment: returns {}.
    - If the comment contains no --- block: returns { "description": comment_text.strip() }.
    - If the comment contains --- ... ---: parses YAML and optional prose; returns the dict
      with optional "description" set from prose after the closing ---.
    """
    suffix = path.suffix.lower()
    if suffix not in _COMMENT_DELIMITERS:
        return {}

    text = path.read_text(encoding="utf-8")
    comment = _extract_top_level_comment(text, path)
    if comment is None:
        return {}

    inner = comment.strip()

    # Look for a --- block: opening --- (at start or after newline), then closing --- on its own line
    if not inner.startswith("---"):
        return {"description": inner}

    rest = inner[3:]
    rest_idx = rest.find("---")
    if rest_idx == -1:
        return {"description": inner}

    config_block = rest[:rest_idx]

    yaml_text = config_block.strip()
    after_yaml = rest[rest_idx + 3 :].strip()
    prose = after_yaml if after_yaml else None

    obj = yaml.safe_load(yaml_text) or {}
    if prose:
        obj["description"] = prose
    return obj
