"""Editorial router — serve a problem's editorial.md."""

from __future__ import annotations

import subprocess

from fastapi import APIRouter, HTTPException

from api.collection.editorial import (
    get_editorial as col_get_editorial,
    compile_editorial,
)
from api.config import get_settings
from api.models.problem import StatementResponse

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
