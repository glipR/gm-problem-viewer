"""
Review router — run the full pipeline, deterministic review, and AI review.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.collection.solutions import get_solutions
from api.collection.test_sets import get_test_generators
from api.config import get_settings
from api.execution.run_testcase import run_solutions_job
from api.execution.run_testgen import run_testgen_job
from api.execution.run_validators import run_validators_job
from api.jobs import JobTask, JobType, create_job, run_sequential
from api.models.problem import (
    GenerateMultipleTestsRequest,
    GenerateTestsRequest,
    JobResponse,
    ReviewResponse,
    RunSolutionRequest,
    RunValidatorsRequest,
)

router = APIRouter(prefix="/problems/{slug}", tags=["review"])


@router.post("/run", response_model=JobResponse)
def run_problem(slug: str, bg: BackgroundTasks):
    """
    Enqueue the full evaluation pipeline for a problem:
      1. Run all test generators
      2. Run all input validators against all relevant test cases
      3. Run all solutions against all test cases
    Returns a job_id to poll via GET /jobs/{job_id}.
    """
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    generators = get_test_generators(problem_path)
    solutions = get_solutions(problem_path)

    test_job_id = create_job(slug, JobType.GENERATE_TESTS)
    validator_job_id = create_job(slug, JobType.RUN_VALIDATORS)
    solution_job_id = create_job(slug, JobType.RUN_SOLUTION)
    tasks = [
        JobTask(
            job_id=test_job_id,
            fn=run_testgen_job,
            args=[
                problem_path,
                GenerateMultipleTestsRequest(
                    requests=[
                        GenerateTestsRequest(test_set=g.test_set, generator_name=g.name)
                        for g in generators
                    ]
                ),
                test_job_id,
            ],
        ),
        JobTask(
            job_id=validator_job_id,
            fn=run_validators_job,
            args=[
                problem_path,
                RunValidatorsRequest(test_set=None),
                validator_job_id,
            ],
        ),
        JobTask(
            job_id=solution_job_id,
            fn=run_solutions_job,
            args=[
                problem_path,
                slug,
                RunSolutionRequest(
                    solution_paths=[s.path for s in solutions], test_set=None
                ),
                solution_job_id,
            ],
        ),
    ]
    bg.add_task(run_sequential, tasks)

    return JobResponse(job_ids=[test_job_id, validator_job_id, solution_job_id])


@router.post("/review", response_model=ReviewResponse)
def review_problem(slug: str):
    """
    Run deterministic review checks synchronously and return results.
    Checks include: presence of input validators, a WA-expected solution,
    a grader for interactive problems, etc.
    """
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/review/ai", response_model=JobResponse)
def review_problem_ai(slug: str):
    """
    Enqueue an AI review of the problem. Returns a job_id to poll via
    GET /jobs/{job_id}. Checks include: bounds alignment between statement
    and validators, per-set validator coverage, boundary case coverage, etc.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
