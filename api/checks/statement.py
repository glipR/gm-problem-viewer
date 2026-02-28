"""
Deterministic checks about the statement
"""

import re

from api.collection.statement import get_statement
from api.config import get_settings
from api.models.problem import Problem
from api.checks import CheckCategory, CheckResult


def _match_header(header: str, statement: str) -> bool:
    # Match a Markdown header line like "## Input" or "### Input"
    # anywhere in the multi-line statement string.
    m = re.search(
        rf"^##+\s*{re.escape(header)}\b",
        statement,
        flags=re.MULTILINE,
    )
    return bool(m)


def statement_has_basic_interaction_blocks(problem: Problem) -> CheckResult:
    """
    Whether the statement has basic headers (Input/Output/Interaction), depending on the problem type
    """
    settings = get_settings()
    statement = get_statement(settings.problems_root / problem.slug)
    if not statement:
        return CheckResult(CheckCategory.STATEMENT, "There is no statement file.")
    if problem.config.type == "standard":
        if not _match_header("Input", statement):
            return CheckResult(
                CheckCategory.STATEMENT, "Problem contains no 'Input' header"
            )
        if not _match_header("Output", statement):
            return CheckResult(
                CheckCategory.STATEMENT, "Problem contains no 'Output' header"
            )
    elif problem.config.type == "interactive":
        if not _match_header("Interaction", statement):
            return CheckResult(
                CheckCategory.STATEMENT, "Problem contains no 'Interaction' header"
            )
    elif problem.config.type == "multi":
        if not _match_header("Interaction", statement):
            return CheckResult(
                CheckCategory.STATEMENT, "Problem contains no 'Interaction' header"
            )
    return CheckResult(CheckCategory.STATEMENT, None)


def has_editorial(problem: Problem) -> CheckResult:
    """
    Whether the problem has an editorial
    """
    settings = get_settings()
    editorial = settings.problems_root / problem.slug / "editorial.md"
    if not editorial.exists():
        return CheckResult(CheckCategory.STATEMENT, "Problem has no editorial")
    with open(editorial, "r") as f:
        content = f.read()
    if len(content) < 100:
        return CheckResult(CheckCategory.STATEMENT, "Problem has short/no editorial")
    return CheckResult(CheckCategory.STATEMENT, None)
