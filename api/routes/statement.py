"""
Statement router — serve and review a problem's statement.md.
"""

from __future__ import annotations

import subprocess

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.collection.statement import get_statement as col_get_statement
from api.config import get_settings
from api.models.problem import JobResponse, StatementResponse

router = APIRouter(prefix="/problems/{slug}", tags=["statement"])


@router.get("/statement/", response_model=StatementResponse)
def get_statement(slug: str):
    """Return the raw markdown source of the problem's statement.md."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    content = col_get_statement(problem_path)
    if content is None:
        raise HTTPException(status_code=404, detail="statement.md not found")
    return StatementResponse(raw=content)


@router.post("/statement/open")
def open_statement_in_editor(slug: str):
    """Open statement.md in Cursor with the problems root as workspace."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    file_path = problem_path / "statement.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="statement.md not found")

    subprocess.Popen(["cursor", str(settings.problems_root), str(file_path)])
    return {"ok": True}


@router.post("/statement/review", response_model=JobResponse)
def review_statement(slug: str):
    """
    Enqueue an AI grammar/clarity review of the problem statement.
    Returns a job_id to poll via GET /jobs/{job_id}.
    The job result contains suggested edits as plain text.
    """
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/files/{filepath:path}")
def get_problem_file(slug: str, filepath: str):
    """Serve a file from the problem directory (e.g. images referenced in statement.md)."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    target = (problem_path / filepath).resolve()
    # Ensure the resolved path is still inside the problem directory (no path traversal)
    if not str(target).startswith(str(problem_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)
