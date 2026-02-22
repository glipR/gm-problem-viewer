"""
Jobs router — poll the status of async background jobs.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.jobs import read_job
from api.models.problem import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id:path}", response_model=JobStatusResponse)
def get_job(job_id: str):
    """
    Return the current status and result of an async job.

    status values: "pending" | "running" | "done" | "failed"
    result is populated once status is "done".
    error is populated once status is "failed".

    Job IDs have the form {slug}/{type}/{timestamp_ms} — use the path
    parameter type so that the slashes are passed through verbatim.
    """
    data = read_job(job_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return JobStatusResponse(
        id=data["id"],
        status=data["status"],
        result=data.get("result"),
        error=data.get("error"),
    )
