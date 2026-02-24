from __future__ import annotations

from pathlib import Path

import yaml

from api.collection.solutions import get_solutions
from api.collection.test_sets import get_test_sets
from api.collection.validators import get_validators
from api.models.problem import Problem, ProblemConfig


def list_problems(problems_dir: Path) -> list[Problem]:
    """Return a lightweight listing of all problems in *problems_dir*.

    Only ``config.yaml`` is read for each problem — test sets, solutions, and
    validators are **not** expanded.  ``test_sets``, ``solutions``, and
    ``validators`` are returned as empty lists.

    Directories that lack a ``config.yaml`` or whose config fails to parse are
    silently skipped.
    """
    if not problems_dir.exists():
        return []

    problems: list[Problem] = []
    for entry in sorted(problems_dir.iterdir()):
        config_path = entry / "config.yaml"
        if not entry.is_dir() or not config_path.exists():
            continue
        try:
            config = ProblemConfig(
                **yaml.safe_load(config_path.read_text(encoding="utf-8"))
            )
        except Exception:
            continue
        problems.append(
            Problem(
                slug=entry.name,
                config=config,
                test_sets=[],
                solutions=[],
                validators={"input": [], "output": None},
            )
        )

    return problems


def get_problem(problems_dir: Path, problem_slug: str) -> Problem:
    """Load a problem summary from disk.

    Args:
        problems_dir: Root directory that contains all problem subdirectories.
        problem_slug: The problem's directory name (e.g. ``"maximum_of_list"``).

    Returns:
        A :class:`~api.models.problem.Problem` instance assembling config,
        test-set names, solutions, and input validators.

    Raises:
        FileNotFoundError: If no ``config.yaml`` exists at the expected path.
    """
    problem_path = problems_dir / problem_slug
    config_path = problem_path / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Problem '{problem_slug}' not found (no config.yaml at {config_path})"
        )

    config = ProblemConfig(**yaml.safe_load(config_path.read_text(encoding="utf-8")))
    test_sets = get_test_sets(problem_path)
    solutions = get_solutions(problem_path)
    validator_set = get_validators(problem_path)

    return Problem(
        slug=problem_slug,
        config=config,
        test_sets=[ts.name for ts in test_sets],
        solutions=solutions,
        validators=validator_set,
    )


def search_problems(
    problems_dir: Path,
    q: str | None = None,
    tags: list[str] | None = None,
) -> list[Problem]:
    """Search problems by free-text query and/or tag filter.

    *q* is matched case-insensitively against the problem name and the raw
    content of ``statement.md``.  *tags* is an AND-filter: every supplied tag
    must appear in ``config.tags``.
    """
    problems = list_problems(problems_dir)

    if tags:
        problems = [p for p in problems if all(t in p.config.tags for t in tags)]

    if q:
        q_lower = q.lower()
        matched: list[Problem] = []
        for problem in problems:
            if q_lower in problem.config.name.lower():
                matched.append(problem)
                continue
            statement_path = problems_dir / problem.slug / "statement.md"
            if statement_path.exists():
                try:
                    if q_lower in statement_path.read_text(encoding="utf-8").lower():
                        matched.append(problem)
                except Exception:
                    pass
        problems = matched

    return problems


def patch_problem_config(problems_dir: Path, problem_slug: str, **kwargs):
    problem_path = problems_dir / problem_slug
    config_path = problem_path / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Problem '{problem_slug}' not found (no config.yaml at {config_path})"
        )

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    data.update(kwargs)
    config_path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True)
    )
