"""
Solutions router — run a solution against test cases.

TODO: Implement subprocess execution with time limiting, stdin/stdout piping,
      interactive judge support, and verdict aggregation.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.config import get_settings
from api.execution.run_testcase import run_solutions_job
from api.jobs import JobType, create_job
from api.models.problem import (
    JobResponse,
    RunSolutionRequest,
)

router = APIRouter(prefix="/problems/{slug}/solutions", tags=["solutions"])


@router.post("/run", response_model=JobResponse)
def run_solution(slug: str, req: RunSolutionRequest, bg: BackgroundTasks):
    """
    Enqueue a solution run against the problem's test cases. Returns a job_id
    to poll via GET /jobs/{job_id}.

    For standard problems: executes the solution with each .in file piped to
    stdin, then calls the checker (or does exact match against reference output).

    For interactive problems: spawns the solution and judge as concurrent
    processes connected via pipes.
    """

    settings = get_settings()
    problem_dir = settings.problems_root / slug
    if not problem_dir.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    job_id = create_job(slug, JobType.RUN_SOLUTION)
    bg.add_task(run_solutions_job, problem_dir, slug, req, job_id)

    return JobResponse(job_ids=[job_id])
