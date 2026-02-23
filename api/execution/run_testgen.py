import logging
from pathlib import Path

from api.collection.test_sets import get_test_generators
from api.execution.execute_python import run_python_file
from api.jobs import update_job
from api.models.problem import (
    GenerateMultipleTestsRequest,
    TestGenerator,
)


def run_testgen_job(
    problem_dir: Path, req: GenerateMultipleTestsRequest, job_id: str
) -> None:
    """
    Background task: runs all applicable validators and streams partial results
    into the job cache file roughly every _FLUSH_INTERVAL seconds.

    Intended to be registered with FastAPI BackgroundTasks:

        bg.add_task(run_validators_job, problem_dir, req, job_id)
    """
    try:
        update_job(job_id, status="running")

        generators = get_test_generators(problem_dir)

        results = []

        for generator in generators:
            if any(
                r.test_set == generator.test_set and r.generator_name == generator.name
                for r in req.requests
            ):
                results.append(
                    {
                        "test_set": generator.test_set,
                        "generator_name": generator.name,
                        "status": "PENDING",
                    }
                )
                update_job(
                    job_id,
                    result=results,
                )

                try:
                    run_individual_testgen(problem_dir, generator)
                except Exception as e:
                    import traceback

                    results[-1]["status"] = "FAILED"
                    results[-1]["error"] = traceback.format_exc()
                else:
                    results[-1]["status"] = "COMPLETE"

                update_job(
                    job_id,
                    result=results,
                )

        update_job(
            job_id,
            status="done",
            result=results,
        )

    except Exception as exc:
        import traceback

        logging.error(traceback.format_exc())
        update_job(job_id, status="failed", error=str(exc))
        raise


def run_individual_testgen(problem_dir: Path, test_generator: TestGenerator):
    generator_file = test_generator.full_path(problem_dir)

    run_python_file(generator_file, None, timeout_sec=None)
