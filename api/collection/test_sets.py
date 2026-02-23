from __future__ import annotations

import re
from pathlib import Path

import yaml

from api.utils.frontmatter import parse_frontmatter
from api.models.problem import TestCase, TestSet, TestSetConfig, TestGenerator


def _natural_key(p: Path) -> list[int | str]:
    """Sort key that orders embedded integers by value, so rand-2 < rand-10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.name)]


def get_test_generators(problem_path: Path) -> list[TestGenerator]:
    """Discover all test generators under ``<problem>/data/``.

    For now, this is just all .py files.
    """
    data_dir = problem_path / "data"
    if not data_dir.exists():
        return []

    generators = []
    for generator in sorted(data_dir.glob("**/*.py"), key=_natural_key):
        test_set = generator.relative_to(data_dir).parts[0]
        generators.append(
            TestGenerator(
                name=str(generator.relative_to(data_dir / test_set)),
                test_set=test_set,
                **parse_frontmatter(generator),
            )
        )
    return generators


def get_test_sets(problem_path: Path) -> list[TestSet]:
    """Discover all test sets under ``<problem>/data/``.

    Each subdirectory of ``data/`` is treated as a test set regardless of
    whether it has a ``config.yaml``.  Test cases are all ``*.in`` files;
    optional ``.yaml`` sidecars provide per-case descriptions.
    """
    data_dir = problem_path / "data"
    if not data_dir.exists():
        return []

    test_sets: list[TestSet] = []
    for set_dir in sorted(
        (d for d in data_dir.iterdir() if d.is_dir()), key=_natural_key
    ):
        test_sets.append(
            TestSet(
                name=set_dir.name,
                config=_load_set_config(set_dir),
                test_cases=_get_test_cases(set_dir),
            )
        )

    return test_sets


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_set_config(set_dir: Path) -> TestSetConfig | None:
    config_path = set_dir / "config.yaml"
    if not config_path.exists():
        return None
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not data:
        return None
    try:
        return TestSetConfig(**data)
    except Exception:
        return None


def _get_test_cases(set_dir: Path) -> list[TestCase]:
    cases: list[TestCase] = []
    for in_file in sorted(set_dir.glob("*.in"), key=_natural_key):
        cases.append(
            TestCase(
                name=in_file.stem,
                set_name=set_dir.name,
                **_load_case_info(in_file),
            )
        )
    return cases


def _load_case_info(in_file: Path):
    sidecar = in_file.with_suffix(".yaml")
    if not sidecar.exists():
        return {}
    data = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    return data or {}
