"""
Jobs router — poll the status of async background jobs.
"""

from __future__ import annotations

import subprocess

from fastapi import APIRouter, HTTPException

from api.config import get_settings
from api.jobs import read_job, _job_path
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


@router.post("/{job_id:path}/open")
def open_job_in_editor(job_id: str):
    """Open the YAML cache file for a job in Cursor for debugging."""
    path = _job_path(job_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Job file not found: {job_id}")

    settings = get_settings()
    subprocess.Popen(["cursor", str(settings.problems_root), str(path)])
    return {"ok": True}
