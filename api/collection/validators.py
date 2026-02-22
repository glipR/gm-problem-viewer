from __future__ import annotations

from pathlib import Path

from api.utils.frontmatter import parse_frontmatter
from api.models.problem import OutputValidator, Validator, ValidatorSet


def get_validators(problem_path: Path) -> ValidatorSet:
    """Return all input validators and the output checker/judge for a problem."""
    return ValidatorSet(
        input=_get_input_validators(problem_path),
        output=_get_output_validator(problem_path),
    )


def _get_input_validators(problem_path: Path) -> list[Validator]:
    """Parse every .py file under ``<problem>/validators/input/``."""
    val_dir = problem_path / "validators" / "input"
    if not val_dir.exists():
        return []

    validators: list[Validator] = []
    for val_file in sorted(val_dir.glob("*.py")):
        fm = parse_frontmatter(val_file)
        validators.append(
            Validator(
                path=str(val_file.relative_to(problem_path / "validators")),
                name=fm.get("name", val_file.stem),
                checks=fm.get("checks"),
            )
        )

    return validators


def _get_output_validator(problem_path: Path) -> OutputValidator | None:
    """Return the output checker (standard) or judge (interactive), if present.

    Looks for ``checker.py`` first, then ``judge.py``, in
    ``<problem>/validators/output/``.
    """
    output_dir = problem_path / "validators" / "output"
    if not output_dir.exists():
        return None

    candidates = [
        ("checker.py", "checker"),
        ("judge.py", "judge"),
    ]
    for filename, validator_type in candidates:
        val_file = output_dir / filename
        if val_file.exists():
            fm = parse_frontmatter(val_file)
            return OutputValidator(
                path=f"output/{filename}",
                type=validator_type,
                name=fm.get("name"),
                description=fm.get("description"),
            )

    return None
