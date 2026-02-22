"""
Run your program against a single test case
"""

import logging
from subprocess import TimeoutExpired
import time
from pathlib import Path

from api.collection.problems import get_problem
from api.collection.solutions import get_candidate_solution, get_solutions
from api.collection.test_sets import get_test_sets
from api.execution.execute_python import run_python_file
from api.execution.run_validators import run_output_validator_standard
from api.jobs import update_job
from api.models.problem import (
    RunSolutionRequest,
    RunSolutionResponse,
    RunSolutionsResponse,
    Solution,
    TestCase,
    Problem,
    Verdict,
)


_FLUSH_INTERVAL = 0.5  # seconds between partial result writes


def run_solutions_job(
    problem_dir: Path, problem_slug: str, req: RunSolutionRequest, job_id: str
) -> None:
    """
    Background task: runs all applicable validators and streams partial results
    into the job cache file roughly every _FLUSH_INTERVAL seconds.

    Intended to be registered with FastAPI BackgroundTasks:

        bg.add_task(run_validators_job, problem_dir, req, job_id)
    """
    try:
        update_job(job_id, status="running")

        problem = get_problem(problem_dir.parent, problem_slug)
        solutions = get_solutions(problem_dir)
        test_sets = get_test_sets(problem_dir)

        results = RunSolutionsResponse(solutions=[])
        last_flush = time.monotonic()

        for solution in solutions:
            if solution.path in req.solution_paths:
                results.solutions.append(
                    RunSolutionResponse(
                        solution_path=solution.path,
                        verdicts=[],
                        overall="PD",
                    )
                )
                for test_set in test_sets:
                    if (not req.test_set) or req.test_set == test_set:
                        for test_case in test_set.test_cases:
                            verdict = run_individual_testcase(
                                problem_dir, problem, solution, test_case
                            )
                            results.solutions[-1].verdicts.append(verdict)

                            now = time.monotonic()
                            if now - last_flush >= _FLUSH_INTERVAL:
                                update_job(
                                    job_id,
                                    result=results.model_dump(),
                                )
                                last_flush = now
                non_AC = [
                    x.verdict
                    for x in results.solutions[-1].verdicts
                    if x.verdict != "AC"
                ]
                results.solutions[-1].overall = non_AC[0] if non_AC else "AC"
                now = time.monotonic()
                if now - last_flush >= _FLUSH_INTERVAL:
                    update_job(
                        job_id,
                        result=results.model_dump(),
                    )
                    last_flush = now

        update_job(
            job_id,
            status="done",
            result=results.model_dump(),
        )

    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        update_job(job_id, status="failed", error=str(exc))
        raise


def output_individual_testcase(
    problem_dir: Path, problem: Problem, solution: Solution, test_case: TestCase
):
    if solution.language == "python":
        result = run_python_file(
            solution.full_path(problem_dir),
            test_case.full_path(problem_dir),
            problem.config.limits.time,
        )
        return result
    else:
        raise NotImplementedError


def run_individual_testcase(
    problem_dir: Path, problem: Problem, solution: Solution, test_case: TestCase
):
    if problem.config.type == "interactive":
        raise NotImplementedError
    # Get solution output
    try:
        result = output_individual_testcase(problem_dir, problem, solution, test_case)
    except TimeoutExpired:
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="TLE",
            time_ms=0,  # TODO
            comment="Time Limit Exceeded",
        )
    if result.exit_code != 0:
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="RTE",
            time_ms=0,  # TODO
            comment="Runtime Error",
        )
    # Get result against candidate solution
    judge_sol = get_candidate_solution(problem_dir)
    judge_result = output_individual_testcase(
        problem_dir, problem, judge_sol, test_case
    )
    if problem.validators.output:
        # Output validator, check against the result output.
        result = run_output_validator_standard(
            problem_dir,
            problem.validators.output,
            test_case,
            result.stdout,
            judge_result.stdout,
        )
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="AC" if result.passed else "WA",
            time_ms=0,  # TODO
            comment=result.error,
        )
