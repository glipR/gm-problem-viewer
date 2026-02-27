"""TODO router — serve and edit a problem's TODO.md."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.config import get_settings

router = APIRouter(prefix="/problems/{slug}", tags=["todo"])


class TodoContent(BaseModel):
    content: str


@router.get("/todo/")
def get_todo(slug: str):
    """Return the raw markdown content of TODO.md, or null if it doesn't exist."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    todo_path = problem_path / "TODO.md"
    if not todo_path.exists():
        return {"raw": None}
    return {"raw": todo_path.read_text(encoding="utf-8")}


@router.put("/todo/")
def update_todo(slug: str, body: TodoContent):
    """Create or overwrite TODO.md with the given content."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    todo_path = problem_path / "TODO.md"
    todo_path.write_text(body.content, encoding="utf-8")
    return {"ok": True}
