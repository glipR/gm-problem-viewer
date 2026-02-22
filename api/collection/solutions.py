from __future__ import annotations

from pathlib import Path

from api.utils.frontmatter import infer_language, parse_frontmatter
from api.models.problem import Solution

_SOLUTION_EXTENSIONS = {".py", ".cpp", ".cc", ".cxx"}


def get_solutions(problem_path: Path) -> list[Solution]:
    """Discover and parse all solution files under ``<problem>/solutions/``.

    Solutions may be flat files or grouped in subdirectories (any depth).
    The ``path`` field on each result is relative to ``solutions/``.
    Language is inferred from the file extension.
    """
    sol_dir = problem_path / "solutions"
    if not sol_dir.exists():
        return []

    files: list[Path] = []
    for ext in _SOLUTION_EXTENSIONS:
        files.extend(sol_dir.rglob(f"*{ext}"))
    files.sort()

    solutions: list[Solution] = []
    for sol_file in files:
        fm = parse_frontmatter(sol_file)
        solutions.append(
            Solution(
                path=str(sol_file.relative_to(sol_dir)),
                language=infer_language(sol_file),
                name=fm.get("name", sol_file.stem),
                expectation=fm.get("expectation", "AC"),
                description=fm.get("description", None),
            )
        )

    return solutions


def get_candidate_solution(problem_path: Path) -> Solution:
    sols = get_solutions(problem_path)
    candidates = []
    for sol in sols:
        # No list filtering, just pure AC.
        if sol.expectation == "AC":
            candidates.append(sol)
    if not candidates:
        raise ValueError("No candidate solution!")
    # Prefer cpp over python
    lang_pref = {"cpp": 1, "python": 2}
    candidates.sort(key=lambda x: lang_pref.get(x.language, 3))
    return candidates[0]
