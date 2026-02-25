"""
Deterministic checks about test cases.
"""

from api.collection.test_sets import get_test_generators, get_test_sets
from api.config import get_settings
from api.models.problem import Problem
from api.checks import CheckCategory, CheckResult


def has_sample_test_case(problem: Problem) -> CheckResult:
    """
    Has a test case in a test set with 0 points.
    Only applicable for standard, as other types may not have samples worth separating.
    """
    if problem.config.type != "standard":
        return CheckResult(CheckCategory.TEST, None)

    settings = get_settings()
    test_sets = get_test_sets(settings.problems_root / problem.slug)
    zero_test_sets = [
        t
        for t in test_sets
        if (t.config and t.config.points == 0) and len(t.test_cases) > 0
    ]
    if not zero_test_sets:
        return CheckResult(CheckCategory.TEST, "There are no test cases in sets with 0 points.")
    return CheckResult(CheckCategory.TEST, None)


def has_test_generator(problem: Problem) -> CheckResult:
    """
    Has at least one test generator
    """
    settings = get_settings()
    generators = get_test_generators(settings.problems_root / problem.slug)
    if not generators:
        return CheckResult(CheckCategory.TEST, "There are no test generators.")
    return CheckResult(CheckCategory.TEST, None)
