"""
Tests router — generate, view, and edit test cases and test sets.

TODO: Implement all endpoints below.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.collection.test_sets import (
    get_test_content,
    get_test_sets,
    get_test_generators,
)
from api.config import get_settings
from api.execution.run_testgen import run_testgen_job
from api.jobs import JobType, create_job
from api.models.problem import (
    CreateTestCaseRequest,
    CreateTestCaseResponse,
    CreateTestSetRequest,
    GenerateMultipleTestsRequest,
    GenerateTestsRequest,
    JobResponse,
    TestContentResponse,
    TestSetDetail,
    UpdateTestCaseRequest,
    UpdateTestSetRequest,
)

router = APIRouter(prefix="/problems/{slug}/tests", tags=["tests"])


@router.get("/", response_model=list[TestSetDetail])
def list_test_sets(slug: str):
    """Return all test sets for a problem, including test cases and generators."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    sets = get_test_sets(problem_path)
    all_generators = get_test_generators(problem_path) or []

    return [
        TestSetDetail(
            name=ts.name,
            config=ts.config,
            test_cases=ts.test_cases,
            generators=[g for g in all_generators if g.test_set == ts.name],
        )
        for ts in sets
    ]


@router.post("/generate", response_model=JobResponse)
def generate_tests(slug: str, req: GenerateMultipleTestsRequest, bg: BackgroundTasks):
    """
    Enqueue test generation for a problem by executing the named generator
    script. Returns a job_id to poll via GET /jobs/{job_id}.

    The generator script is run from within its own directory (so that
    `Path(__file__).parent` resolves correctly).
    """
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    job_id = create_job(slug, JobType.GENERATE_TESTS)
    bg.add_task(run_testgen_job, problem_path, req, job_id)

    return JobResponse(job_ids=[job_id])


@router.post("/", response_model=None, status_code=201)
def create_test_set(slug: str, req: CreateTestSetRequest):
    """Create a new test set directory with a config.yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{set_name}", response_model=CreateTestCaseResponse, status_code=201)
def create_test_case(slug: str, set_name: str, req: CreateTestCaseRequest):
    """
    Write a new .in file (and optional sidecar .yaml) into the named test set.
    The file name is auto-assigned from the highest existing numeric stem + 1,
    or taken from req.name if provided.
    """
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{set_name}/{test_name:path}", response_model=TestContentResponse)
def get_test_case(slug: str, set_name: str, test_name: str):
    """Return the raw contents of a .in file."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    return get_test_content(problem_path, set_name, test_name)


@router.patch("/{set_name}/{test_name:path}", response_model=None)
def update_test_case(
    slug: str, set_name: str, test_name: str, req: UpdateTestCaseRequest
):
    """Update the description in a test case's sidecar .yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{set_name}", response_model=None)
def update_test_set(slug: str, set_name: str, req: UpdateTestSetRequest):
    """Update fields in a test set's config.yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")
