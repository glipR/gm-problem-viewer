"""AI-powered review checks using the local ``claude`` CLI.

Each check function reads relevant files from the problem directory,
builds a prompt, and invokes ``claude -p <prompt> --output-format text``
as a subprocess.  Checks that perform edits (1, 2, 4) let Claude Code
modify files directly.  Every check returns a **one-sentence summary**.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def run_claude(prompt: str, cwd: Path, timeout: int = 120) -> str:
    """Run the ``claude`` CLI with *prompt* and return its stdout."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        logger.warning("claude exited %d: %s", result.returncode, result.stderr[:500])
    return result.stdout.strip()


def _read_if_exists(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


# ---------------------------------------------------------------------------
# 1. Output validator alignment
# ---------------------------------------------------------------------------


def check_output_validator_alignment(problem_path: Path) -> str:
    """Check whether the output validator matches the statement requirements."""
    import yaml

    config = yaml.safe_load((problem_path / "config.yaml").read_text())
    problem_type = config.get("type", "standard")
    statement = _read_if_exists(problem_path / "statement.md") or "(empty)"

    checker_path = problem_path / "validators" / "output" / "checker.py"
    judge_path = problem_path / "validators" / "output" / "judge.py"
    existing_validator = _read_if_exists(checker_path) or _read_if_exists(judge_path)

    validator_section = (
        f"Existing output validator:\n```python\n{existing_validator}\n```"
        if existing_validator
        else "No output validator exists yet."
    )

    prompt = f"""You are reviewing a competitive programming problem.

Problem type: {problem_type}
Statement:
{statement}

{validator_section}

Your task: Determine whether the problem needs a special output validator (checker) beyond simple diff comparison. Consider:
- Does the problem allow multiple correct answers?
- Does the problem require floating point comparison with tolerance?
- Does the output need special validation logic?

If the problem type is "standard" and needs a checker, create or fix `validators/output/checker.py`.
If the problem type is "interactive", create or fix `validators/output/judge.py`.

The file must have YAML frontmatter in a docstring:
```python
\"\"\"---
name: Descriptive Name
---
\"\"\"
```

For standard checkers, the script reads three files: input (sys.argv[1]), expected output (sys.argv[2]), contestant output (sys.argv[3]).
For interactive judges, the script communicates via stdin/stdout with the contestant program.

If the existing validator is correct and sufficient, do NOT edit anything.
If no special validator is needed (simple diff is fine), do NOT create one.

After your analysis, respond with ONLY a single sentence summarizing what you found or changed. Do not include any other text."""

    return run_claude(prompt, cwd=problem_path)


# ---------------------------------------------------------------------------
# 2. Input validator coverage
# ---------------------------------------------------------------------------


def check_input_validator_coverage(problem_path: Path) -> str:
    """Check that input validators cover all constraints from the statement."""
    statement = _read_if_exists(problem_path / "statement.md") or "(empty)"

    # Gather existing input validators
    val_dir = problem_path / "validators" / "input"
    validators_text = ""
    if val_dir.exists():
        for vf in sorted(val_dir.glob("*.py")):
            validators_text += (
                f"\n--- {vf.name} ---\n{vf.read_text(encoding='utf-8')}\n"
            )

    if not validators_text:
        validators_text = "No input validators exist yet."

    # Gather test set names
    data_dir = problem_path / "data"
    test_sets: list[str] = []
    if data_dir.exists():
        test_sets = sorted(d.name for d in data_dir.iterdir() if d.is_dir())

    prompt = f"""You are reviewing a competitive programming problem's input validators.

Statement:
{statement}

Test sets: {', '.join(test_sets) if test_sets else '(none)'}

Existing input validators:
{validators_text}

Your task: Check whether the input validators fully cover the constraints described in the statement.
- Each constraint (bounds on N, M, string lengths, graph properties, etc.) should be validated.
- If there are multiple test sets with different bounds, validators should use the `checks` frontmatter field to scope to specific sets.

Input validator template:
```python
\"\"\"---
name: Descriptive Name
checks:
- setA
- setB
---
Validates specific constraints.
\"\"\"
n = int(input())
assert 1 <= n <= 100
```

If `checks` is omitted, the validator applies to ALL test sets.
If `checks: [setA]`, it only runs on setA.

Create or edit validator files under `validators/input/` as needed.
If validators are already complete and correct, do NOT edit anything.

After your analysis, respond with ONLY a single sentence summarizing what you found or changed. Do not include any other text."""

    return run_claude(prompt, cwd=problem_path)


# ---------------------------------------------------------------------------
# 3. Boundary test coverage
# ---------------------------------------------------------------------------


def check_boundary_test_coverage(problem_path: Path) -> str:
    """Analyze test generators for missing boundary/edge cases."""
    statement = _read_if_exists(problem_path / "statement.md") or "(empty)"

    # Gather generator files
    data_dir = problem_path / "data"
    generators_text = ""
    if data_dir.exists():
        for gen_file in sorted(data_dir.rglob("**/*.py")):
            rel = gen_file.relative_to(problem_path)
            generators_text += (
                f"\n--- {rel} ---\n{gen_file.read_text(encoding='utf-8')}\n"
            )

    if not generators_text:
        generators_text = "No test generators found."

    prompt = f"""You are reviewing a competitive programming problem's test generators for boundary coverage.

Statement:
{statement}

Test generators:
{generators_text}

Your task: Analyze the generators and identify missing boundary/edge cases. Consider:
- Minimum and maximum values for all constraints (n=1, n=max, etc.)
- Empty or trivial inputs
- Special structures (all same elements, sorted, reverse sorted, etc.)
- Edge cases specific to the problem type

Do NOT edit any files. Just analyze.

Respond with ONLY a single sentence summarizing the boundary coverage status and any missing cases. Do not include any other text."""

    return run_claude(prompt, cwd=problem_path)


# ---------------------------------------------------------------------------
# 4. Statement spelling/grammar
# ---------------------------------------------------------------------------


def check_statement_spelling(problem_path: Path) -> str:
    """Fix spelling and grammar issues in statement.md."""
    statement = _read_if_exists(problem_path / "statement.md")
    if not statement or not statement.strip():
        return "Statement is empty; nothing to check."

    prompt = f"""You are proofreading a competitive programming problem statement.

The file is `statement.md` in the current directory.

Statement:
{statement}

Your task: Fix any spelling or grammar issues in `statement.md`. Rules:
- Fix typos, grammatical errors, and awkward phrasing
- Do NOT change LaTeX math expressions (anything between $ or $$), unless this seems logically incorrect.
- Do NOT change the meaning or technical content
- Do NOT reformat or restructure the document
- Preserve all markdown directives (like :::test_block)

If the statement has no issues, do NOT edit the file.

After your analysis, respond with ONLY a single sentence summarizing what you found or changed. Do not include any other text."""

    return run_claude(prompt, cwd=problem_path)


# ---------------------------------------------------------------------------
# 5. Solution optimality
# ---------------------------------------------------------------------------


def check_solution_optimality(problem_path: Path) -> str:
    """Evaluate whether AC solutions use optimal algorithms."""
    statement = _read_if_exists(problem_path / "statement.md") or "(empty)"

    # Gather AC solutions
    sol_dir = problem_path / "solutions"
    solutions_text = ""
    if sol_dir.exists():
        from api.utils.frontmatter import parse_frontmatter

        for sf in sorted(sol_dir.rglob("*")):
            if sf.suffix in (".py", ".cpp", ".cc", ".cxx") and sf.is_file():
                fm = parse_frontmatter(sf)
                exp = fm.get("expectation", "AC")
                if exp == "AC":
                    rel = sf.relative_to(problem_path)
                    solutions_text += (
                        f"\n--- {rel} ---\n{sf.read_text(encoding='utf-8')}\n"
                    )

    if not solutions_text:
        return "No AC solutions found to evaluate."

    prompt = f"""You are reviewing the accepted (AC) solutions of a competitive programming problem for optimality.

Statement:
{statement}

AC Solutions:
{solutions_text}

Your task: Analyze whether the AC solution(s) use the optimal algorithm for this problem. Consider:
- Time complexity vs. the constraints
- Could a fundamentally faster algorithm exist?
- Are there unnecessary constant-factor overheads?

Do NOT edit any files. Just analyze.

Respond with ONLY a single sentence summarizing your assessment of solution optimality. 
You may assume the user is a competitive programming expert and understands most algorithm types. Do not include any other text."""

    return run_claude(prompt, cwd=problem_path)


# ---------------------------------------------------------------------------
# All checks registry
# ---------------------------------------------------------------------------

AI_CHECKS = [
    ("Output Validator Alignment", check_output_validator_alignment),
    ("Input Validator Coverage", check_input_validator_coverage),
    ("Boundary Test Coverage", check_boundary_test_coverage),
    ("Statement Spelling", check_statement_spelling),
    ("Solution Optimality", check_solution_optimality),
]
