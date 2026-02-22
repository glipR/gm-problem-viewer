"""
Review router — run the full pipeline, deterministic review, and AI review.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models.problem import JobResponse, ReviewResponse

router = APIRouter(prefix="/problems/{slug}", tags=["review"])


@router.post("/run", response_model=JobResponse)
def run_problem(slug: str):
    """
    Enqueue the full evaluation pipeline for a problem:
      1. Run all test generators
      2. Run all input validators against all relevant test cases
      3. Run all solutions against all test cases
      4. Collate results
    Returns a job_id to poll via GET /jobs/{job_id}.
    """
    raise HTTPException(status_code=501, detail="Not implemented")


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
