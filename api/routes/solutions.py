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
    JobResponse,
    RunSolutionRequest,
)

router = APIRouter(prefix="/problems/{slug}/solutions", tags=["solutions"])


@router.post("/run", response_model=JobResponse)
def run_solution(slug: str, req: RunSolutionRequest):
    """
    Enqueue a solution run against the problem's test cases. Returns a job_id
    to poll via GET /jobs/{job_id}.

    For standard problems: executes the solution with each .in file piped to
    stdin, then calls the checker (or does exact match against reference output).

    For interactive problems: spawns the solution and judge as concurrent
    processes connected via pipes.
    """
    raise HTTPException(status_code=501, detail="Solution running not yet implemented")
