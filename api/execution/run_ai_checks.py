"""Background task runner for AI-powered review checks."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from api.checks.ai_checks import AI_CHECKS
from api.jobs import update_job

logger = logging.getLogger(__name__)


def run_ai_review_job(problem_path: Path, slug: str, job_id: str) -> None:
    """Run all AI checks sequentially, streaming partial results after each."""
    try:
        update_job(job_id, status="running")

        checks: list[dict[str, str]] = []

        for name, check_fn in AI_CHECKS:
            try:
                summary = check_fn(problem_path / slug)
            except Exception as exc:
                logger.warning("AI check %r failed: %s", name, exc)
                summary = f"Error: {exc}"

            checks.append({"name": name, "summary": summary})

            # Stream partial results so the frontend can show progress
            update_job(job_id, result={"checks": checks})

        update_job(job_id, status="done", result={"checks": checks})

    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        update_job(job_id, status="failed", error=str(exc))
        raise


def run_single_ai_check_job(
    problem_path: Path,
    job_id: str,
    name: str,
    check_fn: Callable[[Path], str],
) -> None:
    """Run a single AI check and store its result."""
    try:
        update_job(job_id, status="running")
        try:
            summary = check_fn(problem_path)
        except Exception as exc:
            logger.warning("AI check %r failed: %s", name, exc)
            summary = f"Error: {exc}"

        update_job(
            job_id,
            status="done",
            result={"checks": [{"name": name, "summary": summary}]},
        )
    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        update_job(job_id, status="failed", error=str(exc))
        raise
