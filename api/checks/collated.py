"""
Collations of individual checks.
"""

from dataclasses import dataclass

from api.models.problem import Problem
from api.checks import CheckCategory, CheckResult
from api.checks.solutions import *
from api.checks.statement import *
from api.checks.tests import *
from api.checks.validators import *


@dataclass
class PhaseResult:
    num_tests: int
    passed: int
    issues: list[str]


@dataclass
class CategoryResult:
    num_tests: int
    passed: int
    issues: list[str]
    color: str  # "green" | "yellow" | "red"


@dataclass
class ReviewResult:
    phase1: PhaseResult
    phase2: PhaseResult
    by_category: dict[str, CategoryResult]


def run_all_checks(problem: Problem) -> ReviewResult:
    phase1: list[CheckResult] = [
        statement_has_basic_interaction_blocks(problem),
        has_sample_test_case(problem),
        has_ac_solution(problem),
        has_test_for_each_expectation(problem),
    ]
    phase2: list[CheckResult] = [
        has_input_validation(problem),
        has_test_generator(problem),
        has_solution_with_verdict(problem, "WA"),
        has_solution_with_verdict(problem, "TLE"),
        has_test_set_acs(problem),
        has_multiple_languages(problem),
        has_editorial(problem),
    ]

    def _phase_result(checks: list[CheckResult]) -> PhaseResult:
        issues = [c.issue for c in checks if c.issue is not None]
        return PhaseResult(len(checks), len(checks) - len(issues), issues)

    # Per-category colour: red if any phase-1 check fails, yellow if any
    # phase-2 check fails (but all phase-1 pass), green if all pass.
    by_category: dict[str, CategoryResult] = {}
    for cat in CheckCategory:
        p1 = [c for c in phase1 if c.category == cat]
        p2 = [c for c in phase2 if c.category == cat]
        all_checks = p1 + p2
        if not all_checks:
            continue
        issues = [c.issue for c in all_checks if c.issue is not None]
        passed = len(all_checks) - len(issues)
        if any(c.issue is not None for c in p1):
            color = "red"
        elif issues:
            color = "yellow"
        else:
            color = "green"
        by_category[cat.value] = CategoryResult(len(all_checks), passed, issues, color)

    return ReviewResult(
        phase1=_phase_result(phase1),
        phase2=_phase_result(phase2),
        by_category=by_category,
    )
