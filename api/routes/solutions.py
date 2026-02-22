"""
Solutions router — run a solution against test cases.

TODO: Implement subprocess execution with time limiting, stdin/stdout piping,
      interactive judge support, and verdict aggregation.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.collection.solutions import get_solutions
from api.collection.test_sets import get_test_sets
from api.config import get_settings
from api.models.problem import (
    RunSolutionRequest,
    RunSolutionResponse,
)

router = APIRouter(prefix="/problems/{slug}/solutions", tags=["solutions"])


@router.post("/run", response_model=RunSolutionResponse)
def run_solution(slug: str, req: RunSolutionRequest):
    """
    Run a solution against the problem's test cases.

    For standard problems: executes the solution with each .in file piped to
    stdin, then calls the checker (or does exact match against reference output).

    For interactive problems: spawns the solution and judge as concurrent
    processes connected via pipes.
    """
    settings = get_settings()
    solutions = get_solutions(settings.problems_root / slug)

    for solution in solutions:
        if solution.path == req.solution_path.strip("/"):
            break
    else:
        return HTTPException(
            status_code=404, detail=f"No solution with path {req.solution_path} found"
        )

    # 1. Discover test cases (optionally filtered by req.test_set)
    tests = get_test_sets(settings.problems_root / slug)
    # 2. For each test case, run the solution with a time limit
    # TODO: implement execution

    # 3. Compare output via checker.py / judge.py
    # 4. Collect Verdict objects
    raise HTTPException(status_code=501, detail="Solution running not yet implemented")
