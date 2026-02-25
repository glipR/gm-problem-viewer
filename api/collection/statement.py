from __future__ import annotations

import re
import yaml
from pathlib import Path


def get_statement(problem_path: Path) -> str | None:
    """Return the raw Markdown source of the problem statement, or None if absent."""
    statement_path = problem_path / "statement.md"
    if not statement_path.exists():
        return None
    return statement_path.read_text(encoding="utf-8")


def compile_statement(problem_path: Path) -> str | None:
    """
    Compiles the markdown for a problem, using the few macros enabled.

    Table for input/output segment:
    @include[setA/1.in][setA/1.out]
    """
    text = get_statement(problem_path)
    if text is None:
        return text

    include_rule = re.compile(
        r"@include\[(.*)\]\[(.*)\]({(?P<kwargs>.*)})?", flags=re.MULTILINE
    )
    matches = include_rule.findall(text)
    for m in matches:
        assert len(m) == 4, "Number of group matches is wrong"
        reconstructed = f"@include[{m[0]}][{m[1]}]{m[2] if m[2] else ''}"
        kwargs = yaml.safe_load(m[2]) or {}
        text = text.replace(
            reconstructed, generate_input_output(problem_path, m[0], m[1], **kwargs)
        )
    return text


def generate_input_output(problem_path: Path, input_file, output_file, title=None):
    data_path = problem_path / "data"
    infile = data_path / input_file
    outfile = data_path / output_file
    if not infile.exists():
        raise ValueError(f"{infile} does not exist!")
    if not outfile.exists():
        raise ValueError(f"{outfile} does not exist!")
    in_text = infile.read_text("utf-8")
    out_text = outfile.read_text("utf-8")
    title_line = (
        f'<th colspan="2">{title or ""}</th>'
        if title
        else "<th>Input</th><th>Output</th>"
    )
    return f"""<table>
    <thead><tr>{title_line}</tr></thead>
    <tbody><tr>
        <td style="vertical-align: top"><pre>{in_text}</pre></td>
        <td style="vertical-align: top"><pre>{out_text}</pre></td>
    </tr></tbody>
</table>"""
