"""
Tests router — generate test cases by running a test set's generator

TODO: Implement subprocess execution of <generator>.py in its own directory,
      capturing newly created .in files, and returning their names.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.collection.test_sets import get_test_generators
from api.config import get_settings
from api.models.problem import (
    GenerateTestsRequest,
    GenerateTestsResponse,
)

router = APIRouter(prefix="/problems/{slug}/tests", tags=["tests"])


@router.post("/generate", response_model=GenerateTestsResponse)
def generate_tests(slug: str, req: GenerateTestsRequest):
    """
    Generate test cases for a problem by executing the test set's gen_tests.py.

    The generator script is run from within its own directory (so that
    `Path(__file__).parent` resolves correctly). Any .in files present before
    and after execution are diffed to determine what was generated.
    """
    settings = get_settings()
    problem_dir = settings.problems_root / slug

    if not problem_dir.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    generators = get_test_generators(problem_dir)
    for generator in generators:
        if generator.test_set == req.test_set and generator.name == req.generator_name:
            break
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Generator {req.generator_name} in {req.test_set} not found",
        )

    # TODO: implement generation
    # 1. Run gen_script as a subprocess with cwd=set_dir
    raise HTTPException(status_code=501, detail="Test generation not yet implemented")
