import logging
from shutil import rmtree
from pathlib import Path
from typing import Callable

import yaml

from api.collection.solutions import get_candidate_solution
from api.collection.statement import compile_statement
from api.collection.test_sets import get_test_sets
from api.config import get_settings
from api.execution.run_testcase import output_individual_testcase
from api.models.problem import ExportTarget, Problem

logger = logging.getLogger(__name__)


def export_dmoj(
    problem: Problem,
    export: ExportTarget,
    on_status: Callable[[str], None] = lambda _: None,
):
    loc = Path(export.location).expanduser().resolve()
    if not loc.exists():
        raise ValueError(f"Location {loc} does not exist!")

    settings = get_settings()
    problem_path = settings.problems_root / problem.slug
    if not problem_path.exists():
        raise ValueError(f"Problem {problem.slug} does not exist!")

    slug = export.overwrite_slug or problem.slug
    export_problem_dir = loc / slug
    if export.clear_directory and export_problem_dir.exists():
        rmtree(export_problem_dir)

    init_yml = {
        "test_cases": [],
    }

    ### Steps:
    ## Rendered Statement
    on_status("Rendering statement...")
    logger.info("Rendering statement...")
    export_problem_dir.mkdir(parents=True, exist_ok=True)
    statement_path = export_problem_dir / "statement.md"
    compiled_statement = compile_statement(problem_path)
    statement_path.write_text(compiled_statement, encoding="utf-8")

    ## Solutions (move to top-level, and prefix the filenames based on folder structure)
    on_status("Copying solutions...")
    logger.info("Rendering solutions...")
    for sol in problem.solutions:
        content = sol.full_path(problem_path).read_text("utf-8")
        new_name = sol.path.replace("/", "_")
        new_loc = export_problem_dir / new_name
        new_loc.write_text(content, "utf-8")

    ## Input Validators (move to top-level, and prefix the filenames based on folder structure)
    on_status("Copying input validators...")
    logger.info("Rendering input validators...")
    for val in problem.validators.input:
        content = val.full_path(problem_path).read_text("utf-8")
        new_name = val.path.replace("/", "_").replace("input", "val_inp")
        new_loc = export_problem_dir / new_name
        new_loc.write_text(content, "utf-8")

    ## Output Validators (move to top-level, and prefix the filenames based on folder_structure)
    on_status("Copying output validator...")
    logger.info("Rendering output validators...")
    if problem.validators.output:
        output = problem.validators.output
        content = output.full_path(problem_path).read_text("utf-8")
        new_name = output.path[len("output/") :]
        new_loc = export_problem_dir / new_name
        # TODO: Transform checkers/judges for DMOJ judging
        if problem.config.type == "standard":
            init_yml["checker"] = new_name
        elif problem.config.type == "interactive":
            init_yml["custom_judge"] = new_name
        elif problem.config.type == "multi":
            init_yml["custom_judge"] = new_name
        new_loc.write_text(content, "utf-8")

    ## data -> tests, keep structure, remove yamls, remove batch configurations
    on_status("Preparing test data...")
    logger.info("Preparing test data...")
    test_sets = get_test_sets(problem_path)
    for test_set in test_sets:
        batch = []
        for test_case in test_set.test_cases:
            content = test_case.full_path(problem_path).read_text("utf-8")
            new_name = test_case.name + ".in"
            test_path = Path("tests") / test_set.name / new_name
            new_loc = export_problem_dir / test_path
            new_loc.parent.mkdir(parents=True, exist_ok=True)
            new_loc.write_text(content, "utf-8")
            batch.append(
                {
                    "in": str(test_path),
                    "out": (
                        str(test_path.with_suffix(".out"))
                        if export.generate_output_files
                        else str(test_path)
                    ),
                }
            )
        init_yml["test_cases"].append(
            {"batched": batch, "points": test_set.config.points}
        )

    ## Generate output files if needed
    if export.generate_output_files:
        on_status("Generating output files...")
        logger.info("Generating output files...")
        for test_set in test_sets:
            for test_case in test_set.test_cases:
                judge_sol = get_candidate_solution(problem_path)
                judge_result = output_individual_testcase(
                    problem_path, problem, judge_sol, test_case
                )
                new_name = test_case.name + ".out"
                test_path = Path("tests") / test_set.name / new_name
                new_loc = export_problem_dir / test_path
                new_loc.parent.mkdir(parents=True, exist_ok=True)
                new_loc.write_text(judge_result.stdout.strip(), "utf-8")

    ## TODO: Compile the test generator scripts to work locally.

    ## init.yml creation
    on_status("Creating init.yml...")
    logger.info("Creating init.yml...")
    init_yml_path = export_problem_dir / "init.yml"
    init_yml_path.write_text(yaml.dump(init_yml), "utf-8")

    exported_files = [
        str(p.relative_to(export_problem_dir))
        for p in export_problem_dir.rglob("*")
        if p.is_file()
    ]
    return str(export_problem_dir), exported_files
