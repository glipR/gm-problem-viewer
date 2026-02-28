"""
Problems router — listing and detail views for problems on disk.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.collection.problems import (
    list_problems as col_list_problems,
    get_problem as col_get_problem,
    patch_problem_config as col_patch_problem_config,
    search_problems as col_search_problems,
    create_problem as col_create_problem,
)
from api.config import get_settings
from api.models.problem import (
    CreateProblemRequest,
    PatchProblemRequest,
    Problem,
)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=list[Problem])
def list_problems():
    """List all problems found in the problems root directory. Leaves the finer details (validators, test cases, solutions) blank."""
    settings = get_settings()

    problems = col_list_problems(settings.problems_root)

    return problems


@router.post("/", response_model=Problem, status_code=201)
def create_problem(req: CreateProblemRequest):
    """Create a new problem directory with default structure."""
    settings = get_settings()
    try:
        col_create_problem(
            settings.problems_root,
            slug=req.slug,
            name=req.name,
            state=req.state,
            problem_type=req.type,
        )
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"Problem '{req.slug}' already exists")
    return col_get_problem(settings.problems_root, req.slug)


@router.get("/search", response_model=list[Problem])
def search_problems(
    q: str | None = Query(default=None, description="Free-text search on name and statement"),
    tags: list[str] = Query(default=[], description="AND-filter by tag"),
):
    """Search problems by free-text and/or tags. Returns lightweight Problem list."""
    settings = get_settings()
    return col_search_problems(settings.problems_root, q=q or None, tags=tags)


@router.get("/{slug}", response_model=Problem)
def get_problem(slug: str):
    """Get details for a single problem by slug."""
    settings = get_settings()
    problem = col_get_problem(settings.problems_root, slug)
    return problem


@router.patch("/{slug}", response_model=Problem)
def update_problem(slug: str, req: PatchProblemRequest):
    """Update mutable problem fields (currently: state). Persists to config.yaml."""
    settings = get_settings()
    col_patch_problem_config(settings.problems_root, slug, **req.model_dump())
    problem = col_get_problem(settings.problems_root, slug)
    return problem
