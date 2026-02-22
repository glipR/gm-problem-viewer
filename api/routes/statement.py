"""
Statement router — serve and review a problem's statement.md.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.collection.statement import get_statement as col_get_statement
from api.config import get_settings
from api.models.problem import JobResponse, StatementResponse

router = APIRouter(prefix="/problems/{slug}/statement", tags=["statement"])


@router.get("/", response_model=StatementResponse)
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


@router.post("/review", response_model=JobResponse)
def review_statement(slug: str):
    """
    Enqueue an AI grammar/clarity review of the problem statement.
    Returns a job_id to poll via GET /jobs/{job_id}.
    The job result contains suggested edits as plain text.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
