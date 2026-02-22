"""
Tests router — generate, view, and edit test cases and test sets.

TODO: Implement all endpoints below.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models.problem import (
    CreateTestCaseRequest,
    CreateTestCaseResponse,
    CreateTestSetRequest,
    GenerateTestsRequest,
    JobResponse,
    TestContentResponse,
    UpdateTestCaseRequest,
    UpdateTestSetRequest,
)

router = APIRouter(prefix="/problems/{slug}/tests", tags=["tests"])


@router.post("/generate", response_model=JobResponse)
def generate_tests(slug: str, req: GenerateTestsRequest):
    """
    Enqueue test generation for a problem by executing the named generator
    script. Returns a job_id to poll via GET /jobs/{job_id}.

    The generator script is run from within its own directory (so that
    `Path(__file__).parent` resolves correctly).
    """
    raise HTTPException(status_code=501, detail="Test generation not yet implemented")


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


@router.get("/{set_name}/{test_name}", response_model=TestContentResponse)
def get_test_case(slug: str, set_name: str, test_name: str):
    """Return the raw contents of a .in file."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{set_name}/{test_name}", response_model=None)
def update_test_case(slug: str, set_name: str, test_name: str, req: UpdateTestCaseRequest):
    """Update the description in a test case's sidecar .yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{set_name}", response_model=None)
def update_test_set(slug: str, set_name: str, req: UpdateTestSetRequest):
    """Update fields in a test set's config.yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")
