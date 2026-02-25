import logging
from dataclasses import asdict
from pathlib import Path

from api.checks.collated import run_all_checks
from api.collection.problems import get_problem
from api.jobs import update_job


def run_checks_job(problem_path: Path, problem_slug: str, job_id: str) -> None:
    """
    Background task: runs all deterministic checks against the problem.

    Intended to be registered with FastAPI BackgroundTasks:

        bg.add_task(run_checks_job, problem_path, slug, job_id)
    """
    try:
        update_job(job_id, status="running")

        problem = get_problem(problem_path, problem_slug)
        review = run_all_checks(problem)

        update_job(
            job_id,
            status="done",
            result=asdict(review),
        )

    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        update_job(job_id, status="failed", error=str(exc))
        raise
