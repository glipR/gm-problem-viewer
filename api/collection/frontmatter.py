"""Utility for parsing YAML frontmatter embedded in solution/validator source files.

Frontmatter is a YAML block wrapped in a language-appropriate docstring comment
at the very start of the file:

  Python (.py):
    \"\"\"---
    key: value
    ---
    Optional prose.
    \"\"\"

  C++ (.cpp / .cc / .cxx):
    /*---
    key: value
    ---
    Optional prose.
    */
    ...

Language is inferred from the file extension.
"""

from __future__ import annotations

from pathlib import Path

import yaml


# Maps file suffix -> (start_delimiter, end_delimiter)
_DELIMITERS: dict[str, tuple[str, str, str]] = {
    ".py": ('"""---', "---", '"""'),
    ".cpp": ("/*---", "---", "*/"),
    ".cc": ("/*---", "---", "*/"),
    ".cxx": ("/*---", "---", "*/"),
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


def parse_frontmatter(path: Path) -> dict:
    """Extract and parse YAML frontmatter from a Python or C++ source file.

    Returns an empty dict when:
    - The file extension is not supported.
    - The file does not start with the expected frontmatter delimiter.
    - The closing delimiter is absent.
    - The YAML block is empty or unparseable.
    """
    suffix = path.suffix.lower()
    delimiters = _DELIMITERS.get(suffix)
    if delimiters is None:
        return {}

    start_delim, end_delim, end_prose_delim = delimiters

    text = path.read_text(encoding="utf-8")
    if not text.startswith(start_delim):
        return {}

    inner = text[len(start_delim) :]
    end_idx = inner.find(end_delim)
    if end_idx == -1:
        return {}

    yaml_text = inner[:end_idx].strip()

    obj = yaml.safe_load(yaml_text) or {}

    after = inner[end_idx + len(end_delim) :]

    after_index = after.find(end_prose_delim)
    if after_index != -1:
        after_content = after[:after_index].strip()
        if after_content:
            obj["description"] = after_content
    return obj
