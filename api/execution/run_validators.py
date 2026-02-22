import importlib.util
import logging
import time
from pathlib import Path

from api.collection.validators import get_validators
from api.collection.test_sets import get_test_sets
from api.jobs import update_job
from api.models.problem import (
    OutputValidator,
    RunValidatorsRequest,
    TestCase,
    Validator,
    ValidatorResult,
)
from api.utils.list_matching import filter_list_matches_test_set
from api.execution.execute_python import run_python_file

_FLUSH_INTERVAL = 0.5  # seconds between partial result writes


def run_validators_job(
    problem_dir: Path, req: RunValidatorsRequest, job_id: str
) -> None:
    """
    Background task: runs all applicable validators and streams partial results
    into the job cache file roughly every _FLUSH_INTERVAL seconds.

    Intended to be registered with FastAPI BackgroundTasks:

        bg.add_task(run_validators_job, problem_dir, req, job_id)
    """
    try:
        update_job(job_id, status="running")

        validators = get_validators(problem_dir)
        test_sets = get_test_sets(problem_dir)

        results: list[ValidatorResult] = []
        last_flush = time.monotonic()

        for validator in validators.input:
            for test_set in test_sets:
                if filter_list_matches_test_set(validator.checks, test_set) and (
                    (not req.test_set) or req.test_set == test_set
                ):
                    for test_case in test_set.test_cases:
                        results.append(
                            run_input_validator(problem_dir, validator, test_case)
                        )

                        now = time.monotonic()
                        if now - last_flush >= _FLUSH_INTERVAL:
                            update_job(
                                job_id,
                                result={"results": [r.model_dump() for r in results]},
                            )
                            last_flush = now

        update_job(
            job_id,
            status="done",
            result={"results": [r.model_dump() for r in results]},
        )

    except Exception as exc:
        update_job(job_id, status="failed", error=str(exc))
        raise


def run_input_validator(problem_dir: Path, validator: Validator, test_case: TestCase):
    result = run_python_file(
        validator.full_path(problem_dir),
        test_case.full_path(problem_dir),
    )
    return ValidatorResult(
        validator=validator.path,
        test_case=test_case.name,
        test_set=test_case.set_name,
        passed=result.exit_code == 0,
        error=result.stderr if result.exit_code != 0 else "",
    )


def run_output_validator_standard(
    problem_dir: Path,
    validator: OutputValidator,
    test_case: TestCase,
    process_output: str,
    judge_output: str,
) -> ValidatorResult:
    validator_path = validator.full_path(problem_dir)
    input_data = test_case.full_path(problem_dir).read_text()

    def capturing_make_result(code: str, points: float, comment: str) -> None:
        return [code, points, comment]

    spec = importlib.util.spec_from_file_location("output_validator", validator_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.make_result = capturing_make_result
    try:
        captured = module.check(input_data, process_output, judge_output, 1.0)
    except Exception as e:
        import traceback

        captured = "RTE", 0, traceback.format_exc()

    if captured:
        code, points, comment = captured
    else:
        code, points, comment = "WA", 0.0, "Checker did not return result"

    return ValidatorResult(
        validator=validator.path,
        test_case=test_case.name,
        test_set=test_case.set_name,
        passed=(code == "AC"),
        error="" if code == "AC" else comment,
    )
