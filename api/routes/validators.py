"""
Validators router — run input validators against test cases.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.config import get_settings
from api.execution.run_validators import run_validators_job
from api.jobs import JobType, create_job
from api.models.problem import (
    JobResponse,
    RunValidatorsRequest,
)

router = APIRouter(prefix="/problems/{slug}/validators", tags=["validators"])


@router.post("/run", response_model=JobResponse)
def run_validators(slug: str, req: RunValidatorsRequest, bg: BackgroundTasks):
    """
    Enqueue an input validator run against the problem's test cases. Returns
    job IDs to poll via GET /jobs/{job_id}.

    Each validator in validators/input/ is run against every .in file it
    applies to (respecting the `checks` frontmatter field). A validator
    passes if it exits without raising an AssertionError.
    """
    settings = get_settings()
    problem_dir = settings.problems_root / slug
    if not problem_dir.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    job_id = create_job(slug, JobType.RUN_VALIDATORS)
    bg.add_task(run_validators_job, problem_dir, req, job_id)

    return JobResponse(job_ids=[job_id])
