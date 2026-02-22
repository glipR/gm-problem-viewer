"""
Problems router — listing and detail views for problems on disk.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.collection import (
    list_problems as col_list_problems,
    get_problem as col_get_problem,
)
from api.config import get_settings
from api.models.problem import (
    Problem,
)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=list[Problem])
def list_problems():
    """List all problems found in the problems root directory. Leaves the finer details (validators, test cases, solutions) blank."""
    settings = get_settings()

    problems = col_list_problems(settings.problems_root)

    return problems


@router.get("/{slug}", response_model=Problem)
def get_problem(slug: str):
    """Get details for a single problem by slug."""
    settings = get_settings()
    problem = col_get_problem(settings.problems_root, slug)
    return problem
