"""
Tests router — generate, view, and edit test cases and test sets.

TODO: Implement all endpoints below.
"""

from __future__ import annotations
import re
import os
import subprocess

import yaml
from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.collection.test_sets import (
    get_test_content,
    get_test_sets,
    get_test_generators,
)
from api.config import get_settings
from api.execution.run_testgen import run_testgen_job
from api.jobs import JobType, create_job
from api.models.problem import (
    CreateTestCaseRequest,
    CreateTestCaseResponse,
    CreateTestSetRequest,
    GenerateMultipleTestsRequest,
    GenerateTestsRequest,
    JobResponse,
    OpenGeneratorRequest,
    OpenTestCaseRequest,
    TestCase,
    TestContentResponse,
    TestSetConfig,
    TestSetDetail,
    UpdateTestCaseRequest,
    UpdateTestSetRequest,
)

router = APIRouter(prefix="/problems/{slug}/tests", tags=["tests"])


@router.get("/", response_model=list[TestSetDetail])
def list_test_sets(slug: str):
    """Return all test sets for a problem, including test cases and generators."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    sets = get_test_sets(problem_path)
    all_generators = get_test_generators(problem_path) or []

    return [
        TestSetDetail(
            name=ts.name,
            config=ts.config,
            test_cases=ts.test_cases,
            generators=[g for g in all_generators if g.test_set == ts.name],
        )
        for ts in sets
    ]


@router.post("/generate", response_model=JobResponse)
def generate_tests(slug: str, req: GenerateMultipleTestsRequest, bg: BackgroundTasks):
    """
    Enqueue test generation for a problem by executing the named generator
    script. Returns a job_id to poll via GET /jobs/{job_id}.

    The generator script is run from within its own directory (so that
    `Path(__file__).parent` resolves correctly).
    """
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    job_id = create_job(slug, JobType.GENERATE_TESTS)
    bg.add_task(run_testgen_job, problem_path, req, job_id)

    return JobResponse(job_ids=[job_id])


@router.post("/open-generator")
def open_generator_in_editor(slug: str, req: OpenGeneratorRequest):
    """Open a test generator file in Cursor with the problems root as workspace."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    file_path = problem_path / "data" / req.set_name / req.gen_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Generator not found: {req.gen_name}")

    subprocess.Popen(["cursor", str(settings.problems_root), str(file_path)])
    return {"ok": True}


@router.post("/open-test")
def open_test_case_in_editor(slug: str, req: OpenTestCaseRequest):
    """Open a test case .in file in Cursor with the problems root as workspace."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    file_path = problem_path / "data" / req.set_name / (req.test_name + ".in")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Test case not found: {req.test_name}.in")

    subprocess.Popen(["cursor", str(settings.problems_root), str(file_path)])
    return {"ok": True}


@router.post("/", response_model=None, status_code=201)
def create_test_set(slug: str, req: CreateTestSetRequest):
    """Create a new test set directory with a config.yaml."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    test_path = problem_path / "data" / req.name
    test_path.mkdir(parents=True, exist_ok=True)
    test_config = test_path / "config.yaml"
    config_obj = TestSetConfig(
        name=req.name,
        description=req.description,
        points=req.points,
        marking_style=req.marking_style,
    )
    test_config.write_text(
        yaml.dump(config_obj.model_dump(), default_flow_style=False, allow_unicode=True)
    )
    return None


@router.post("/{set_name}", response_model=CreateTestCaseResponse, status_code=201)
def create_test_case(slug: str, set_name: str, req: CreateTestCaseRequest):
    """
    Write a new .in file (and optional sidecar .yaml) into the named test set.
    The file name is auto-assigned from the highest existing numeric stem + 1,
    or taken from req.name if provided.
    """
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    test_path = problem_path / "data" / set_name
    if not test_path.exists():
        raise HTTPException(status_code=404, detail=f"Test Set '{set_name}' not found")

    name = req.name
    if name is None:
        # try to assign input<x>, starting from 1
        num_set = set()
        for file in os.listdir(test_path):
            m = re.match(r"input(\d+).in", file)
            if m:
                num_set.add(int(m.group(1)))
        x = 1
        while x in num_set:
            x += 1
        name = f"input{x}"

    file_path = test_path / (name + ".in")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(req.content)
    case = TestCase(name=name, set_name=set_name, description=req.description)
    cfg = file_path.with_suffix(".yaml")
    obj = case.model_dump(
        exclude={"name", "set_name"}, exclude_none=True, exclude_unset=True
    )
    if obj:
        cfg.write_text(
            yaml.dump(
                obj,
                default_flow_style=False,
                allow_unicode=True,
            )
        )

    return CreateTestCaseResponse(name=name)


@router.get("/{set_name}/{test_name:path}", response_model=TestContentResponse)
def get_test_case(slug: str, set_name: str, test_name: str):
    """Return the raw contents of a .in file."""
    settings = get_settings()
    problem_path = settings.problems_root / slug
    if not problem_path.exists():
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    return get_test_content(problem_path, set_name, test_name)


@router.patch("/{set_name}/{test_name:path}", response_model=None)
def update_test_case(
    slug: str, set_name: str, test_name: str, req: UpdateTestCaseRequest
):
    """Update the description in a test case's sidecar .yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/{set_name}", response_model=None)
def update_test_set(slug: str, set_name: str, req: UpdateTestSetRequest):
    """Update fields in a test set's config.yaml."""
    raise HTTPException(status_code=501, detail="Not implemented")
