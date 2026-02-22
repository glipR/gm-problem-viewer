"""
Validators router — run input validators against test cases.

TODO: Implement subprocess execution of validator scripts, scoping by
      test set, and aggregation of assertion errors.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models.problem import (
    JobResponse,
    RunValidatorsRequest,
)

router = APIRouter(prefix="/problems/{slug}/validators", tags=["validators"])


@router.post("/run", response_model=JobResponse)
def run_validators(slug: str, req: RunValidatorsRequest):
    """
    Enqueue an input validator run against the problem's test cases. Returns a
    job_id to poll via GET /jobs/{job_id}.

    Each validator in validators/input/ is run against every .in file it
    applies to (respecting the `checks` frontmatter field). A validator
    passes if it exits without raising an AssertionError.
    """
    raise HTTPException(status_code=501, detail="Validator running not yet implemented")
