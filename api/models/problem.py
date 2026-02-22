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


class ProblemConfig(BaseModel):
    name: str
    type: str  # "standard" | "interactive"
    tags: list[str] = []
    difficulty: int | None = None
    export_config: dict[str, ExportTarget] = {}


class TestCase(BaseModel):
    name: str
    set_name: str
    description: str | None = None

    def full_path(self, problem_dir: Path):
        return problem_dir / "data" / self.set_name / f"{self.name}.in"


class Solution(BaseModel):
    path: str  # relative path within solutions/
    language: str | None = None  # "python" | "cpp"; inferred from file extension
    name: str
    expectation: str | list[dict[str, str]]  # "AC" | "WA" | "TLE" or per-set list
    description: str | None = None


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


class ValidatorSet(BaseModel):
    input: list[Validator] = []
    output: OutputValidator | None = None


class TestSet(BaseModel):
    name: str  # directory slug
    config: TestSetConfig | None = None
    test_cases: list[TestCase] = []


class Problem(BaseModel):
    slug: str
    config: ProblemConfig
    test_sets: list[str]
    solutions: list[Solution]
    validators: list[Validator]


class TestGenerator(BaseModel):
    name: str  # Name of file
    test_set: str  # Set folder
    description: str  # Sourced from docstring


# --- Request / Response models for API operations ---


class RunSolutionRequest(BaseModel):
    solution_path: str  # relative path, e.g. "complete_ac/sol.py"
    test_set: str | None = None  # None = run all sets


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


class GenerateTestsResponse(BaseModel):
    test_set: str
    generated: list[str]  # names of newly created .in files


class ExportRequest(BaseModel):
    target: str  # key in export_config


class ExportResponse(BaseModel):
    target: str
    location: str
    exported_files: list[str]
