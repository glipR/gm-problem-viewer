"""
Export router — export a problem to an external format.

Supported export types (from config.yaml export_config):
  - dmoj:        Export to DMOJ problem package format
  - problemtools: Export to Kattis/problemtools format  (not yet implemented)
  - direct-copy:  Copy the problem directory as-is       (not yet implemented)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.collection.problems import get_problem
from api.config import get_settings
from api.export.dmoj import export_dmoj
from api.jobs import JobType, create_job, get_latest_job_id, read_job, update_job
from api.models.problem import (
    ExportRequest,
    JobResponse,
    JobStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/problems/{slug}/export", tags=["export"])


def _run_export_job(slug: str, target: str, job_id: str) -> None:
    """Background task that dispatches to the appropriate exporter."""
    update_job(job_id, status="running")
    try:
        settings = get_settings()
        problem = get_problem(settings.problems_root, slug)
        target_config = problem.config.export_config[target]

        def on_status(msg: str) -> None:
            update_job(job_id, status="running", result={"step": msg})

        if target_config.type == "dmoj":
            location, exported_files = export_dmoj(problem, target_config, on_status)
        else:
            raise ValueError(f"Export type '{target_config.type}' not yet implemented")

        update_job(
            job_id,
            status="done",
            result={
                "target": target,
                "location": location,
                "exported_files": exported_files,
            },
        )
    except Exception as exc:
        logger.exception("Export job %s failed", job_id)
        update_job(job_id, status="failed", error=str(exc))


@router.post("/", response_model=JobResponse)
def export_problem(slug: str, req: ExportRequest, bg: BackgroundTasks):
    """
    Export a problem to the specified target defined in config.yaml.

    Returns a job ID to poll via GET /jobs/{job_id}.
    """
    settings = get_settings()
    problem_path = settings.problems_root / slug

    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    problem = get_problem(settings.problems_root, slug)

    if req.target not in problem.config.export_config:
        available = list(problem.config.export_config.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Export target '{req.target}' not found. Available: {available}",
        )

    job_id = create_job(slug, JobType.EXPORT)
    bg.add_task(_run_export_job, slug, req.target, job_id)

    return JobResponse(job_ids=[job_id])


@router.get("/latest", response_model=JobStatusResponse | None)
def get_latest_export_job(slug: str):
    """
    Return the most recent export job for this problem, or null if none exists.
    """
    job_id = get_latest_job_id(slug, JobType.EXPORT)
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
