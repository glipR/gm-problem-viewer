"""Job cache — filesystem-backed async job storage.

Job IDs have the form  {slug}/{type}/{timestamp_ms}
and are stored at      {cache_root}/{slug}/{type}/{timestamp_ms}.yaml

The YAML file is written on creation and updated in-place as the job
progresses, so callers can write partial results by calling update_job
multiple times before the job reaches a terminal status.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from api.config import get_settings


# --- Canonical job types ---

class JobType:
    GENERATE_TESTS = "generate_tests"
    RUN_VALIDATORS = "run_validators"
    RUN_SOLUTION = "run_solution"
    EXPORT = "export"


# --- Internal helpers ---

def _cache_root() -> Path:
    return get_settings().cache_root


def _job_path(job_id: str) -> Path:
    return _cache_root() / f"{job_id}.yaml"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Public API ---

def make_job_id(slug: str, job_type: str) -> str:
    """Build a unique job ID from slug, type, and current time in ms."""
    ts = int(time.time() * 1000)
    return f"{slug}/{job_type}/{ts}"


def create_job(slug: str, job_type: str) -> str:
    """
    Create a new YAML job file on disk and return its ID.

    The file is written atomically; the job starts in "pending" status.
    """
    job_id = make_job_id(slug, job_type)
    path = _job_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    now = _now_iso()
    data: dict[str, Any] = {
        "id": job_id,
        "slug": slug,
        "type": job_type,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "result": None,
        "error": None,
    }
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    return job_id


def update_job(job_id: str, **fields: Any) -> None:
    """
    Merge *fields* into the job's YAML file and refresh updated_at.

    Typical use during execution:

        update_job(job_id, status="running")
        ...
        update_job(job_id, status="done", result={...})
    """
    path = _job_path(job_id)
    data: dict[str, Any] = yaml.safe_load(path.read_text())
    data.update(fields)
    data["updated_at"] = _now_iso()
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))


def read_job(job_id: str) -> dict[str, Any] | None:
    """Return the parsed YAML for a job, or None if it does not exist."""
    path = _job_path(job_id)
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text())


def get_latest_job_id(slug: str, job_type: str) -> str | None:
    """
    Return the job_id for the most recent job of *job_type* for *slug*,
    or None if no such job exists.

    Timestamps are monotonically increasing integers, so lexicographic
    sort on the stem is sufficient.
    """
    dir_path = _cache_root() / slug / job_type
    if not dir_path.exists():
        return None
    files = sorted(dir_path.glob("*.yaml"), key=lambda p: p.stem)
    if not files:
        return None
    return f"{slug}/{job_type}/{files[-1].stem}"
