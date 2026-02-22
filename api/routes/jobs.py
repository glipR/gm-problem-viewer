"""
Jobs router — poll the status of async background jobs.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models.problem import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str):
    """
    Return the current status and result of an async job.

    status values: "pending" | "running" | "done" | "failed"
    result is populated once status is "done" or "failed".
    """
    raise HTTPException(status_code=501, detail="Not implemented")
