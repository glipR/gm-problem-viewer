"""
Validators router — run input validators against test cases.

TODO: Implement subprocess execution of validator scripts, scoping by
      test set, and aggregation of assertion errors.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.collection import get_validators, get_test_sets
from api.config import get_settings
from api.models.problem import (
    RunValidatorsRequest,
    RunValidatorsResponse,
)

router = APIRouter(prefix="/problems/{slug}/validators", tags=["validators"])


@router.post("/run", response_model=RunValidatorsResponse)
def run_validators(slug: str, req: RunValidatorsRequest):
    """
    Run input validators against the problem's test cases.

    Each validator in validators/input/ is run against every .in file it
    applies to (respecting the `checks` frontmatter field). A validator
    passes if it exits without raising an AssertionError.
    """
    settings = get_settings()
    problem_dir = settings.problems_root / slug

    if not problem_dir.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    # 1. Discover validators from validators/input/*.py
    # 2. Parse frontmatter to determine which sets each validator applies to
    validators = get_validators(problem_dir)
    # 3. Discover test cases (optionally filtered by req.test_set)
    test_sets = get_test_sets(problem_dir)
    # TODO: implement set logic
    # 4. For each (validator, test_case) pair, run the validator with the .in
    #    file piped to stdin; catch AssertionError / non-zero exit
    # 5. Collect ValidatorResult objects
    raise HTTPException(status_code=501, detail="Validator running not yet implemented")
