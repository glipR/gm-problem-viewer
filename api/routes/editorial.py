"""Editorial router — serve a problem's editorial.md."""

from __future__ import annotations

import subprocess

from fastapi import APIRouter, HTTPException

from api.config import get_settings

router = APIRouter(prefix="/problems/{slug}", tags=["editorial"])


@router.get("/editorial/")
def get_editorial(slug: str):
    """Return the raw markdown content of editorial.md."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    editorial_path = problem_path / "editorial.md"
    if not editorial_path.exists():
        raise HTTPException(status_code=404, detail="editorial.md not found")
    return {"raw": editorial_path.read_text(encoding="utf-8")}


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
