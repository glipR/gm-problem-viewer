"""
Generate .out files for all test cases by running the AC (candidate) solution.

.out files are cached alongside .in files and used during solution comparison
instead of re-running the candidate solution every time.
"""

import logging
import time
from pathlib import Path
from subprocess import TimeoutExpired

from api.collection.problems import get_problem
from api.collection.solutions import get_candidate_solution
from api.collection.test_sets import get_test_sets
from api.execution.run_testcase import output_individual_testcase
from api.jobs import update_job


_FLUSH_INTERVAL = 0.5


def generate_output_files(
    problem_path: Path, problem_slug: str, force: bool = False, job_id: str | None = None
) -> None:
    """Generate .out files for every .in file by running the candidate solution.

    Args:
        problem_path: Path to the problem directory.
        problem_slug: Problem slug for loading the problem.
        force: If True, regenerate even if .out already exists.
        job_id: Optional job ID for progress reporting.
    """
    try:
        if job_id:
            update_job(job_id, status="running")

        problem = get_problem(problem_path.parent, problem_slug)
        candidate = get_candidate_solution(problem_path)
        test_sets = get_test_sets(problem_path)

        total = sum(len(ts.test_cases) for ts in test_sets)
        done = 0
        errors: list[str] = []
        last_flush = time.monotonic()

        for test_set in test_sets:
            for test_case in test_set.test_cases:
                in_path = test_case.full_path(problem_path)
                out_path = in_path.with_suffix(".out")

                if not force and out_path.exists():
                    done += 1
                    continue

                try:
                    result = output_individual_testcase(
                        problem_path, problem, candidate, test_case
                    )
                    if result.exit_code != 0:
                        errors.append(
                            f"{test_set.name}/{test_case.name}: candidate RTE — {result.stderr[:200]}"
                        )
                        done += 1
                        continue
                    out_path.write_text(result.stdout.strip() + "\n")
                except TimeoutExpired:
                    errors.append(
                        f"{test_set.name}/{test_case.name}: candidate TLE"
                    )
                except Exception as exc:
                    errors.append(
                        f"{test_set.name}/{test_case.name}: {exc}"
                    )

                done += 1

                if job_id:
                    now = time.monotonic()
                    if now - last_flush >= _FLUSH_INTERVAL:
                        update_job(
                            job_id,
                            result={
                                "done": done,
                                "total": total,
                                "step": f"Generating output ({done}/{total})",
                                "errors": errors,
                            },
                        )
                        last_flush = now

        if job_id:
            update_job(
                job_id,
                status="done",
                result={
                    "done": done,
                    "total": total,
                    "errors": errors,
                },
            )

    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        if job_id:
            update_job(job_id, status="failed", error=str(exc))
        raise
