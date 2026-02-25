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
        return CheckResult(
            CheckCategory.TEST, "There are no test cases in sets with 0 points."
        )
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


def has_test_for_each_expectation(problem: Problem) -> CheckResult:
    """
    For every per set expectation of a solution, there should be a test set for this solution with a test case.
    """
    settings = get_settings()
    test_sets = get_test_sets(settings.problems_root / problem.slug)
    for solution in problem.solutions:
        if isinstance(solution.expectation, dict):
            for set_name in solution.expectation.keys():
                possible = [t for t in test_sets if t.name == set_name]
                if not possible:
                    return CheckResult(
                        CheckCategory.TEST, f"There is no test set {set_name}."
                    )
                test_set = possible[0]
                if not test_set.test_cases:
                    return CheckResult(
                        CheckCategory.TEST, f"There are no test cases for {set_name}."
                    )
    return CheckResult(CheckCategory.TEST, None)
