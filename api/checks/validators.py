"""
Deterministic Checks on validators
"""

from api.models.problem import Problem
from api.checks import CheckCategory, CheckResult


def has_input_validation(problem: Problem) -> CheckResult:
    if len(problem.validators.input) == 0:
        return CheckResult(CheckCategory.VALIDATOR, "Has no input validation.")
    return CheckResult(CheckCategory.VALIDATOR, None)
