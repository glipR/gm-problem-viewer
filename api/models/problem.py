from __future__ import annotations

from typing import Any
from pydantic import BaseModel
from pathlib import Path


class TestSetConfig(BaseModel):
    name: str
    description: str | None = None
    points: float = 0.0
    marking_style: str = "all_or_nothing"  # "progressive" | "all_or_nothing"


class ExportTarget(BaseModel):
    type: str  # "problemtools" | "dmoj" | "direct-copy"
    location: str
    problemtools_config: dict[str, Any] = {}
    dmoj_config: dict[str, Any] = {}


class ProblemLimits(BaseModel):
    time: float = 1  # Time in seconds
    memory: int = 262144  # Mem limit in bytes (default 256Mb)


class ProblemConfig(BaseModel):
    name: str
    type: str  # "standard" | "interactive"
    tags: list[str] = []
    difficulty: int | None = None
    export_config: dict[str, ExportTarget] = {}
    state: str  # "draft" | "in-progress" | "review" | "complete"
    contests: list[str] | None = None
    limits: ProblemLimits
    author: str


class TestCase(BaseModel):
    name: str
    set_name: str
    description: str | None = None

    def full_path(self, problem_path: Path):
        return problem_path / "data" / self.set_name / f"{self.name}.in"


class Solution(BaseModel):
    path: str  # relative path within solutions/
    language: str | None = None  # "python" | "cpp"; inferred from file extension
    name: str
    expectation: str | list[dict[str, str]]  # "AC" | "WA" | "TLE" or per-set list
    description: str | None = None

    def full_path(self, problem_path: Path):
        return problem_path / "solutions" / self.path


class Validator(BaseModel):
    path: str  # relative path within validators/
    name: str
    checks: list[str] | None = None  # None = applies to all sets
    description: str | None = None

    def full_path(self, problem_path: Path):
        return problem_path / "validators" / self.path


class OutputValidator(BaseModel):
    path: str  # relative to validators/ (e.g. "output/checker.py")
    type: str  # "checker" | "judge"
    name: str | None = None
    description: str | None = None

    def full_path(self, problem_path: Path):
        return problem_path / "validators" / self.path


class ValidatorSet(BaseModel):
    input: list[Validator] = []
    output: OutputValidator | None = None


class TestSet(BaseModel):
    name: str  # directory slug
    config: TestSetConfig | None = None
    test_cases: list[TestCase] = []


class TestSetDetail(BaseModel):
    """TestSet augmented with generators, returned by GET /problems/{slug}/tests/."""

    name: str
    config: TestSetConfig | None = None
    test_cases: list[TestCase] = []
    generators: list[TestGenerator] = []


class Problem(BaseModel):
    slug: str
    config: ProblemConfig
    test_sets: list[str]
    solutions: list[Solution]
    validators: ValidatorSet


class TestGenerator(BaseModel):
    name: str  # Name of file
    test_set: str  # Set folder
    description: str = ""  # Sourced from docstring; empty if none present

    def full_path(self, problem_path: Path):
        return problem_path / "data" / self.test_set / self.name


# --- Request / Response models for API operations ---


class RunSolutionRequest(BaseModel):
    solution_paths: list[str]  # relative path, e.g. "complete_ac/sol.py"
    test_set: str | None = None  # None = run all sets


class OpenSolutionRequest(BaseModel):
    solution_path: str  # relative path, e.g. "complete_ac/sol.py"


class OpenGeneratorRequest(BaseModel):
    set_name: str
    gen_name: str  # filename, e.g. "gen_tests.py"


class OpenTestCaseRequest(BaseModel):
    set_name: str
    test_name: str  # stem, e.g. "input1"


class Verdict(BaseModel):
    test_case: str
    test_set: str
    verdict: str  # "AC" | "WA" | "TLE" | "RE"
    time_ms: float | None = None
    comment: str = ""


class RunSolutionResponse(BaseModel):
    solution_path: str
    verdicts: list[Verdict]
    overall: str  # aggregate verdict


class RunSolutionsResponse(BaseModel):
    solutions: list[RunSolutionResponse]


class RunValidatorsRequest(BaseModel):
    test_set: str | None = None  # None = validate all sets


class ValidatorResult(BaseModel):
    validator: str
    test_case: str
    test_set: str
    passed: bool
    error: str = ""


class RunValidatorsResponse(BaseModel):
    results: list[ValidatorResult]


class GenerateTestsRequest(BaseModel):
    test_set: str
    generator_name: str = "gen_tests.py"


class GenerateMultipleTestsRequest(BaseModel):
    requests: list[GenerateTestsRequest]


class ExportRequest(BaseModel):
    target: str  # key in export_config


class ExportResponse(BaseModel):
    target: str
    location: str
    exported_files: list[str]


# --- Async job system ---


class JobResponse(BaseModel):
    # Ordered list of job IDs to poll.  Single-step endpoints return one entry;
    # orchestrations (e.g. run_problem) return multiple in execution order.
    job_ids: list[str]


class JobStatusResponse(BaseModel):
    id: str
    status: str  # "pending" | "running" | "done" | "failed"
    result: Any | None = None
    error: str | None = None


# --- Problem state update ---


class PatchProblemRequest(BaseModel):
    state: str  # "draft" | "in-progress" | "review" | "complete"


# --- Statement ---


class StatementResponse(BaseModel):
    raw: str


# --- Review ---


class CheckResult(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class ReviewResponse(BaseModel):
    checks: list[CheckResult]


# --- Test set / test case creation and editing ---


class CreateTestSetRequest(BaseModel):
    name: str
    description: str | None = None
    points: float = 0.0
    marking_style: str = "all_or_nothing"  # "progressive" | "all_or_nothing"


class CreateTestCaseRequest(BaseModel):
    content: str
    name: str | None = None  # auto-assigned if absent
    description: str | None = None


class CreateTestCaseResponse(BaseModel):
    name: str


class UpdateTestCaseRequest(BaseModel):
    description: str


class UpdateTestSetRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    points: float | None = None
    marking_style: str | None = None


class TestContentResponse(BaseModel):
    content: str
