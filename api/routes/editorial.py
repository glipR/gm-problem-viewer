"""Editorial router — serve and review a problem's editorial.md."""

from __future__ import annotations

import subprocess

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.checks.ai_checks import check_editorial_spelling
from api.collection.editorial import (
    get_editorial as col_get_editorial,
    compile_editorial,
)
from api.config import get_settings
from api.execution.run_ai_checks import run_single_ai_check_job
from api.jobs import JobType, create_job
from api.models.problem import JobResponse, StatementResponse

router = APIRouter(prefix="/problems/{slug}", tags=["editorial"])


@router.get("/editorial/", response_model=StatementResponse)
def get_editorial(slug: str):
    """Return the compiled markdown content of editorial.md."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    content = col_get_editorial(problem_path)
    compiled_content = compile_editorial(problem_path)
    final_content = compiled_content or content
    if final_content is None:
        raise HTTPException(status_code=404, detail="editorial.md not found")
    return StatementResponse(raw=final_content)


@router.post("/editorial/open")
def open_editorial_in_editor(slug: str):
    """Open editorial.md in Cursor with the problems root as workspace."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    editorial_path = problem_path / "editorial.md"
    if not editorial_path.exists():
        raise HTTPException(status_code=404, detail="editorial.md not found")
    subprocess.Popen(["cursor", str(settings.problems_root), str(editorial_path)])
    return {"ok": True}


@router.post("/editorial/review", response_model=JobResponse)
def review_editorial(slug: str, bg: BackgroundTasks):
    """
    Enqueue an AI grammar/clarity review of the problem editorial.
    Returns a job_id to poll via GET /jobs/{job_id}.
    """
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    job_id = create_job(slug, JobType.REVIEW_EDITORIAL)
    bg.add_task(
        run_single_ai_check_job,
        problem_path,
        job_id,
        "Editorial Spelling",
        check_editorial_spelling,
    )
    return JobResponse(job_ids=[job_id])
