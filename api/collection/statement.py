from __future__ import annotations

import base64
import html
import re
import yaml
from pathlib import Path

LANG_LABELS = {
    "py": "Python",
    "cpp": "C++",
    "java": "Java",
    "js": "JavaScript",
    "c": "C",
    "rs": "Rust",
    "go": "Go",
}

# Regex to strip YAML frontmatter from solution files ("""---\n...\n---\n...""")
FRONTMATTER_RE = re.compile(
    r'^("""|/\*)\s*---\n.*?---\n.*?(\1|(\*/))', flags=re.DOTALL
)


def get_statement(problem_path: Path) -> str | None:
    """Return the raw Markdown source of the problem statement, or None if absent."""
    statement_path = problem_path / "statement.md"
    if not statement_path.exists():
        return None
    return statement_path.read_text(encoding="utf-8")


def compile_markdown(problem_path: Path, text: str) -> str:
    """
    Compile markdown text, expanding macros.

    Table for input/output segment:
    @include[setA/1.in][setA/1.out]

    Code with language tabs:
    @code_include[solutions/sol.py]{langs: "py,cpp", rm_config: True}
    """
    # Process @code_include first
    code_include_rule = re.compile(
        r"@code_include\[(.*?)\]({(?P<kwargs>.*?)})?", flags=re.MULTILINE
    )
    for m in code_include_rule.finditer(text):
        reconstructed = m.group(0)
        kwargs = yaml.safe_load(m.group(2)) or {} if m.group(2) else {}
        replacement = generate_code_include(problem_path, m.group(1), **kwargs)
        text = text.replace(reconstructed, replacement, 1)

    # Process @include
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

    # Process ||spoiler|| syntax → clickable spoiler spans
    text = re.sub(
        r"\|\|(.+?)\|\|",
        r'<span class="spoiler">\1</span>',
        text,
        flags=re.DOTALL,
    )

    return text


def compile_statement(problem_path: Path) -> str | None:
    """Compile the statement markdown, expanding @include macros."""
    text = get_statement(problem_path)
    if text is None:
        return text
    return compile_markdown(problem_path, text)


def _strip_frontmatter(code: str) -> str:
    """Remove YAML frontmatter block from solution source code."""
    m = FRONTMATTER_RE.match(code)
    if m:
        code = code[m.end():]
    return code.lstrip("\n")


def _lang_code_syntax(ext: str) -> str:
    """Map file extension to a syntax-highlight language name for HTML class."""
    mapping = {"py": "python", "cpp": "cpp", "java": "java", "js": "javascript",
               "c": "c", "rs": "rust", "go": "go"}
    return mapping.get(ext, ext)


def generate_code_include(problem_path: Path, file_path: str, langs: str = "", rm_config: bool = False) -> str:
    """
    Generate an HTML code-tabs block for one or more language variants of a file.

    file_path: relative path like 'solutions/sub_a_ac/sol.py'
    langs: comma-separated extensions like 'py,cpp'
    rm_config: if True, strip YAML frontmatter from code
    """
    source = problem_path / file_path
    stem = source.stem
    parent = source.parent

    if langs:
        extensions = [l.strip() for l in langs.split(",")]
    else:
        extensions = [source.suffix.lstrip(".")]

    parts = []
    for ext in extensions:
        variant = parent / f"{stem}.{ext}"
        if not variant.exists():
            continue
        code = variant.read_text(encoding="utf-8")
        if rm_config:
            code = _strip_frontmatter(code)
        label = LANG_LABELS.get(ext, ext)
        syntax = _lang_code_syntax(ext)
        b64 = base64.b64encode(code.rstrip("\n").encode()).decode()
        parts.append(
            f'<pre data-lang="{ext}" data-label="{label}" data-syntax="{syntax}" data-code="{b64}"></pre>'
        )

    if not parts:
        return f"<!-- @code_include: no files found for {file_path} -->"

    return '<div class="code-tabs">' + "\n".join(parts) + "</div>"


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
