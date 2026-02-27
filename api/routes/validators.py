"""
Validators router — run input validators against test cases.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.config import get_settings
from api.execution.run_validators import run_validators_job
from api.jobs import JobType, create_job, get_latest_job_id, read_job
from api.models.problem import (
    JobResponse,
    JobStatusResponse,
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
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    job_id = create_job(slug, JobType.RUN_VALIDATORS)
    bg.add_task(run_validators_job, problem_path, req, job_id)

    return JobResponse(job_ids=[job_id])


@router.get("/latest", response_model=JobStatusResponse | None)
def get_latest_validate_job(slug: str):
    """
    Return the most recent /run job for this problem, or null if none exists.
    """
    job_id = get_latest_job_id(slug, JobType.RUN_VALIDATORS)
    if job_id is None:
        return None
    data = read_job(job_id)
    if data is None:
        return None
    return JobStatusResponse(
        id=data["id"],
        status=data["status"],
        result=data.get("result"),
        error=data.get("error"),
    )
