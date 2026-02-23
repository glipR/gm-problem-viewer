"""
Solutions router — run a solution against test cases.

TODO: Implement subprocess execution with time limiting, stdin/stdout piping,
      interactive judge support, and verdict aggregation.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.config import get_settings
from api.execution.run_testcase import run_solutions_job
from api.jobs import (
    JobType,
    create_job,
    create_individual_job,
    get_latest_job_id,
    get_latest_individual_job_id,
    list_individual_solution_keys,
    solution_path_from_key,
    read_job,
)
from api.models.problem import (
    JobResponse,
    RunSolutionRequest,
    RunSolutionResponse,
    RunSolutionsResponse,
)

router = APIRouter(prefix="/problems/{slug}/solutions", tags=["solutions"])


@router.post("/run", response_model=JobResponse)
def run_solution(slug: str, req: RunSolutionRequest, bg: BackgroundTasks):
    """
    Enqueue a solution run against the problem's test cases. Returns a job_id
    to poll via GET /jobs/{job_id}.

    For standard problems: executes the solution with each .in file piped to
    stdin, then calls the checker (or does exact match against reference output).

    For interactive problems: spawns the solution and judge as concurrent
    processes connected via pipes.
    """

    settings = get_settings()
    problem_dir = settings.problems_root / slug
    if not problem_dir.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    if len(req.solution_paths) == 1:
        job_id = create_individual_job(slug, req.solution_paths[0])
    else:
        job_id = create_job(slug, JobType.RUN_SOLUTION)
    bg.add_task(run_solutions_job, problem_dir, slug, req, job_id)

    return JobResponse(job_ids=[job_id])


@router.get("/merged-results", response_model=RunSolutionsResponse)
def get_merged_results(slug: str):
    """
    Return a merged RunSolutionsResponse combining the latest group run with
    the latest individual run for each solution.  For any given solution path,
    whichever result has the newer updated_at timestamp wins.
    """
    # path → (updated_at ISO string, RunSolutionResponse dict)
    merged: dict[str, tuple[str, dict]] = {}

    # Seed from the latest group run
    group_id = get_latest_job_id(slug, JobType.RUN_SOLUTION)
    if group_id:
        data = read_job(group_id)
        if data and data.get("result"):
            for sol in data["result"].get("solutions", []):
                merged[sol["solution_path"]] = (data["updated_at"], sol)

    # Overlay individual runs, preferring whichever is more recent
    for key in list_individual_solution_keys(slug):
        solution_path = solution_path_from_key(key)
        ind_id = get_latest_individual_job_id(slug, solution_path)
        if not ind_id:
            continue
        data = read_job(ind_id)
        if not data or not data.get("result"):
            continue
        for sol in data["result"].get("solutions", []):
            path = sol["solution_path"]
            existing = merged.get(path)
            if not existing or data["updated_at"] > existing[0]:
                merged[path] = (data["updated_at"], sol)

    return RunSolutionsResponse(
        solutions=[RunSolutionResponse(**v) for _, v in merged.values()]
    )
