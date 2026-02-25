"""
Deterministic checks about solutions
"""

from api.config import get_settings
from api.collection.test_sets import get_test_sets
from api.models.problem import Problem
from api.checks import CheckCategory, CheckResult


def has_ac_solution(problem: Problem) -> CheckResult:
    """
    Whether the problem has at least one problem that expects AC for all test sets.
    """
    return has_solution_with_verdict(problem, "AC")


def has_non_zero_test_set(problem: Problem) -> CheckResult:
    """
    Has at least one test set with non zero points.
    """
    settings = get_settings()
    test_sets = get_test_sets(settings.problems_root / problem.slug)
    non_zero_test_sets = [t for t in test_sets if t.config.points > 0]
    if not non_zero_test_sets:
        return CheckResult(CheckCategory.SOLUTION, "All test sets have 0 points.")
    return CheckResult(CheckCategory.SOLUTION, None)


def has_test_set_acs(problem: Problem) -> CheckResult:
    """
    For every non-zero point test set except one, there is a solution that solves that test set, but fails for some other test set.
    """
    settings = get_settings()
    test_sets = get_test_sets(settings.problems_root / problem.slug)
    non_zero_test_sets = [t for t in test_sets if t.config and t.config.points > 0]
    expected_acs = len(non_zero_test_sets) - 1
    for test_set in non_zero_test_sets:
        # Does there exist a solution that expects to AC this test_set, but get non-AC overall?
        for solution in problem.solutions:
            if (
                solution.expectation_for_set(test_set) == "AC"
                and solution.expectation_overall() != "AC"
            ):
                expected_acs -= 1
                break
    if expected_acs > 0:
        return CheckResult(CheckCategory.SOLUTION, "Multiple test sets do *not* have sub-task only solutions (solutions that pass for them, and not for others).")
    return CheckResult(CheckCategory.SOLUTION, None)


def has_multiple_languages(problem: Problem) -> CheckResult:
    """
    Problem permits two solutions in two different languages
    """
    lang_set = set(sol.language for sol in problem.solutions if sol.language)
    if len(lang_set) >= 2:
        return CheckResult(CheckCategory.SOLUTION, None)
    if len(lang_set) == 1:
        return CheckResult(CheckCategory.SOLUTION, f"All solutions are in {list(lang_set)[0]}.")
    return CheckResult(CheckCategory.SOLUTION, "No solutions have a defined language.")


def has_solution_with_verdict(problem: Problem, verdict: str) -> CheckResult:
    """
    Problem has at least one solution with this verdict overall.
    """
    for solution in problem.solutions:
        if solution.expectation_overall() == verdict:
            return CheckResult(CheckCategory.SOLUTION, None)
    return CheckResult(CheckCategory.SOLUTION, f"No solution found with verdict {verdict}.")
