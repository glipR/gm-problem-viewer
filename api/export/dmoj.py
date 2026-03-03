import ast
import logging
import re
import textwrap
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


STUB_FUNCTIONS = {"read_line", "write_line", "make_result"}


def _transform_judge_to_grader(source: str) -> str:
    """Transform an interactive judge.py into a DMOJ-compatible grader.py.

    Source format uses:
        - grade(input_file: str, points: float) as entry point
        - read_line() / write_line(s) / make_result(code, points, comment) stubs

    Target format uses:
        - test_res(input_data, write_fn, read_fn, points) with fn params
        - CheckerResult(success_bool, points, message) for results
        - DMOJ InteractiveGrader boilerplate
    """
    # Strip frontmatter docstring
    source = _strip_frontmatter(source)

    # Parse into AST to extract the grade function and remove stubs
    tree = ast.parse(source)

    # Find the grade function and stub functions
    grade_func = None
    nodes_to_keep = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == "grade":
                grade_func = node
            elif node.name in STUB_FUNCTIONS:
                continue  # skip stub
            else:
                nodes_to_keep.append(node)
        else:
            nodes_to_keep.append(node)

    if grade_func is None:
        raise ValueError("No grade() function found in judge.py")

    # Get the source lines (after frontmatter stripping)
    lines = source.split("\n")

    # Extract non-stub, non-grade top-level code
    top_level_code = []
    for node in nodes_to_keep:
        start = node.lineno - 1
        end = node.end_lineno
        top_level_code.append("\n".join(lines[start:end]))

    # Extract grade function body and transform it
    grade_source = _extract_function_source(lines, grade_func)
    test_res_source = _transform_grade_function(grade_source)

    # Combine top-level code and transformed function
    parts = []
    if top_level_code:
        parts.append("\n\n".join(top_level_code))
    parts.append(test_res_source)
    test_res_combined = "\n\n".join(parts)

    # Load the grader template and fill it in
    template = (Path(__file__).parent / "grader_template.py").read_text("utf-8")
    return template.replace("{test_res_function}", test_res_combined)


def _strip_frontmatter(source: str) -> str:
    """Remove the leading YAML frontmatter docstring."""
    match = re.match(r'^"""---\n.*?---\n(?:.*?)"""\n*', source, re.DOTALL)
    if match:
        return source[match.end() :]
    # Also handle bare triple-quote docstrings
    match = re.match(r'^""".*?"""\n*', source, re.DOTALL)
    if match:
        return source[match.end() :]
    return source


def _extract_function_source(lines: list[str], func_node: ast.FunctionDef) -> str:
    """Extract the raw source text of a function from source lines."""
    start = func_node.lineno - 1
    end = func_node.end_lineno
    return "\n".join(lines[start:end])


def _transform_grade_function(grade_source: str) -> str:
    """Transform grade(input_file, points) to test_res(input_data, write_fn, read_fn, points)."""
    lines = grade_source.split("\n")

    # Replace function signature
    lines[0] = re.sub(
        r"def grade\s*\([^)]*\)\s*:",
        "def test_res(input_data, write_fn, read_fn, points):",
        lines[0],
    )

    result = "\n".join(lines)

    # Replace input_file -> input_data
    result = result.replace("input_file", "input_data")

    # Replace stub calls
    result = re.sub(r"\bread_line\(\)", "read_fn()", result)
    result = re.sub(r"\bwrite_line\(", "write_fn(", result)

    # Replace make_result calls:
    # make_result("AC", points, comment) -> CheckerResult(True, points, comment)
    # make_result("WA", 0, comment) -> CheckerResult(False, 0, comment)
    result = re.sub(
        r'\bmake_result\(\s*"AC"\s*,',
        "CheckerResult(True,",
        result,
    )
    result = re.sub(
        r'\bmake_result\(\s*"WA"\s*,',
        "CheckerResult(False,",
        result,
    )
    # Catch any other make_result calls with variable codes
    result = re.sub(
        r"\bmake_result\((\w+)\s*,",
        r'CheckerResult(\1 == "AC",',
        result,
    )

    return result


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

    ## Solutions (move to sol/ dir, and prefix the filenames based on folder structure)
    on_status("Copying solutions...")
    logger.info("Rendering solutions...")
    sol_dir = export_problem_dir / "solutions"
    sol_dir.mkdir(exist_ok=True)
    for sol in problem.solutions:
        content = sol.full_path(problem_path).read_text("utf-8")
        new_name = sol.path.replace("/", "_")
        new_loc = sol_dir / new_name
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
        if problem.config.type == "standard":
            # This is a checker with a def judge function.
            # We need to write a custom check function to align with DMOJ.
            check_template = Path(__file__).parent / "check_template.py"
            content = content + "\n\n" + check_template.read_text("utf-8")
            init_yml["checker"] = new_name
        elif problem.config.type == "interactive":
            # Transform judge.py into DMOJ InteractiveGrader format
            content = _transform_judge_to_grader(content)
            new_name = "grader.py"
            new_loc = export_problem_dir / new_name
            init_yml["custom_judge"] = new_name
        elif problem.config.type == "multi":
            # TODO: Work for multi type problems (warden, card trick)
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
            og_out_path = test_case.full_path(problem_path).with_suffix(".out")
            out_path = test_path.with_suffix(".out")
            new_loc = export_problem_dir / test_path
            new_loc.parent.mkdir(parents=True, exist_ok=True)
            new_loc.write_text(content, "utf-8")
            if og_out_path.exists():
                new_loc.with_suffix(".out").write_text(
                    og_out_path.read_text("utf-8"), "utf-8"
                )
            batch.append(
                {
                    "in": str(test_path),
                    "out": (str(out_path) if out_path.exists() else str(test_path)),
                }
            )
        init_yml["test_cases"].append(
            {
                "batched": batch,
                "points": test_set.config.points if test_set.config else 100,
            }
        )

    ## TODO: Compile the test generator scripts to work locally. (For DMOJ - may need to change imports)

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
