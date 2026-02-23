"""
Export router — export a problem to an external format.

Supported export types (from config.yaml export_config):
  - dmoj:        Export to DMOJ problem package format
  - problemtools: Export to Kattis/problemtools format
  - direct-copy:  Copy the problem directory as-is to a target location

TODO: Implement each export type.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.collection.problems import get_problem
from api.config import get_settings
from api.models.problem import (
    ExportRequest,
    ExportResponse,
)

router = APIRouter(prefix="/problems/{slug}/export", tags=["export"])


@router.post("/", response_model=ExportResponse)
def export_problem(slug: str, req: ExportRequest):
    """
    Export a problem to the specified target defined in config.yaml.

    Reads the `export_config.<target>` block from the problem's config.yaml
    and dispatches to the appropriate exporter.
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

    target_config = problem.config.export_config[req.target]

    # TODO: implement export
    # Dispatch based on target_config.type:
    #   "dmoj"        -> _export_dmoj(problem_path, slug, config, target_config)
    #   "problemtools" -> _export_problemtools(problem_path, slug, config, target_config)
    #   "direct-copy" -> _export_direct_copy(problem_path, slug, target_config)
    raise HTTPException(
        status_code=501,
        detail=f"Export type '{target_config.type}' not yet implemented",
    )
