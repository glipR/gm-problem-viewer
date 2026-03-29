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
from api.execution.execute_cpp import CompileError, compile_cpp, run_cpp_file
from api.execution.execute_python import run_python_file
from api.execution.run_interactive import run_interactive_testcase
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
    problem_path: Path, problem_slug: str, req: RunSolutionRequest, job_id: str
) -> None:
    """
    Background task: runs all applicable validators and streams partial results
    into the job cache file roughly every _FLUSH_INTERVAL seconds.

    Intended to be registered with FastAPI BackgroundTasks:

        bg.add_task(run_validators_job, problem_path, req, job_id)
    """
    try:
        update_job(job_id, status="running")

        problem = get_problem(problem_path.parent, problem_slug)
        solutions = get_solutions(problem_path)
        test_sets = get_test_sets(problem_path)

        results = RunSolutionsResponse(solutions=[], status=None)
        last_flush = time.monotonic()

        failed_expectations = False

        for solution in solutions:
            if solution.path in req.solution_paths:
                results.solutions.append(
                    RunSolutionResponse(
                        solution_path=solution.path,
                        verdicts=[],
                        overall="PD",
                        set_consistent={},
                    )
                )
                for test_set in test_sets:
                    if (not req.test_set) or req.test_set == test_set:
                        set_verdicts = []
                        for test_case in test_set.test_cases:
                            verdict = run_individual_testcase(
                                problem_path, problem, solution, test_case
                            )
                            results.solutions[-1].verdicts.append(verdict)
                            set_verdicts.append(verdict)

                            now = time.monotonic()
                            if now - last_flush >= _FLUSH_INTERVAL:
                                update_job(
                                    job_id,
                                    result=results.model_dump(),
                                )
                                last_flush = now
                        if isinstance(solution.expectation, dict):
                            expectation = solution.expectation_for_set(test_set)
                            non_AC = [
                                x.verdict for x in set_verdicts if x.verdict != "AC"
                            ]
                            set_verdict = non_AC[0] if non_AC else "AC"
                            if (
                                expectation is not None
                                and set_verdict not in expectation
                            ):
                                results.solutions[-1].set_consistent[
                                    test_set.name
                                ] = f"Expected verdict {expectation} for {test_set.name}, got {set_verdict}"
                                failed_expectations = True
                non_AC = [
                    x.verdict
                    for x in results.solutions[-1].verdicts
                    if x.verdict != "AC"
                ]
                results.solutions[-1].overall = non_AC[0] if non_AC else "AC"
                if (
                    isinstance(solution.expectation, str)
                    and solution.expectation != results.solutions[-1].overall
                ):
                    failed_expectations = True
                now = time.monotonic()
                if now - last_flush >= _FLUSH_INTERVAL:
                    update_job(
                        job_id,
                        result=results.model_dump(),
                    )
                    last_flush = now

        update_job(
            job_id,
            status="failed" if failed_expectations else "done",
            result=results.model_dump(),
        )

    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        update_job(job_id, status="failed", error=str(exc))
        raise


def output_individual_testcase(
    problem_path: Path, problem: Problem, solution: Solution, test_case: TestCase
):
    if solution.language == "python":
        result = run_python_file(
            solution.full_path(problem_path),
            test_case.full_path(problem_path),
            problem.config.limits.time,
        )
        return result
    elif solution.language == "cpp":
        result = run_cpp_file(
            solution.full_path(problem_path),
            test_case.full_path(problem_path),
            problem.config.limits.time,
        )
        return result
    else:
        raise NotImplementedError(f"Unsupported language: {solution.language}")


def _solution_cmd(problem_path: Path, solution: Solution) -> list[str]:
    """Return the command to run a solution as a subprocess."""
    full = solution.full_path(problem_path)
    if solution.language == "python":
        return ["python", str(full.resolve())]
    elif solution.language == "cpp":
        binary = compile_cpp(full)
        return [str(binary)]
    else:
        raise NotImplementedError(f"Unsupported language: {solution.language}")


def run_interactive_testcase_verdict(
    problem_path: Path, problem: Problem, solution: Solution, test_case: TestCase
) -> Verdict:
    """Run an interactive testcase using the DMOJ-style grader."""
    judge = problem.validators.output
    if judge is None or judge.type != "judge":
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="IE",
            time_ms=0,
            comment="No judge.py found for interactive problem",
        )

    judge_path = judge.full_path(problem_path)
    in_path = test_case.full_path(problem_path)
    input_data = in_path.read_text() if in_path.exists() else ""

    points = 100

    try:
        cmd = _solution_cmd(problem_path, solution)
    except CompileError as e:
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="CE",
            time_ms=0,
            comment=e.stderr,
        )

    start = time.monotonic()
    try:
        result = run_interactive_testcase(
            problem_path=problem_path,
            judge_path=judge_path,
            solution_cmd=cmd,
            input_data=input_data,
            points=points,
            timeout_sec=problem.config.limits.time,
        )
    except Exception as e:
        import traceback

        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="IE",
            time_ms=0,
            comment=f"Judge error: {e} {traceback.format_exc()}",
        )
    elapsed_ms = (time.monotonic() - start) * 1000

    return Verdict(
        test_case=test_case.name,
        test_set=test_case.set_name,
        verdict=result.verdict,
        time_ms=elapsed_ms,
        comment=result.comment,
    )


def run_individual_testcase(
    problem_path: Path, problem: Problem, solution: Solution, test_case: TestCase
):
    if problem.config.type == "interactive":
        return run_interactive_testcase_verdict(
            problem_path, problem, solution, test_case
        )
    # Get solution output
    try:
        result = output_individual_testcase(problem_path, problem, solution, test_case)
    except CompileError as e:
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="CE",
            time_ms=0,
            comment=e.stderr,
        )
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
            comment=result.stderr,
        )
    # Get expected output: prefer cached .out file, fall back to running candidate
    in_path = test_case.full_path(problem_path)
    out_path = in_path.with_suffix(".out")
    if out_path.exists():
        expected_stdout = out_path.read_text().rstrip("\n")
    else:
        judge_sol = get_candidate_solution(problem_path)
        judge_result = output_individual_testcase(
            problem_path, problem, judge_sol, test_case
        )
        expected_stdout = judge_result.stdout
        # Cache the output for future runs
        out_path.write_text(expected_stdout.strip() + "\n")
    if problem.validators.output:
        # Output validator, check against the result output.
        result = run_output_validator_standard(
            problem_path,
            problem.validators.output,
            test_case,
            result.stdout,
            expected_stdout,
        )
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="AC" if result.passed else "WA",
            time_ms=0,  # TODO
            comment=result.error,
        )
    else:
        # Just do diff
        same = result.stdout.strip() == expected_stdout.strip()
        return Verdict(
            test_case=test_case.name,
            test_set=test_case.set_name,
            verdict="AC" if same else "WA",
            time_ms=0,  # TODO
            comment="",
        )
