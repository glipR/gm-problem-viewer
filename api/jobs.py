"""Job cache — filesystem-backed async job storage.

Job IDs have the form  {slug}/{type}/{timestamp_ms}
and are stored at      {cache_root}/{slug}/{type}/{timestamp_ms}.yaml

The YAML file is written on creation and updated in-place as the job
progresses, so callers can write partial results by calling update_job
multiple times before the job reaches a terminal status.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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


# ---------------------------------------------------------------------------
# Individual solution run jobs (stored one level deeper than group runs)
# ---------------------------------------------------------------------------

def _solution_key(solution_path: str) -> str:
    """Encode a solution path as a single directory name (/ → __)."""
    return solution_path.replace("/", "__")


def solution_path_from_key(key: str) -> str:
    return key.replace("__", "/")


def create_individual_job(slug: str, solution_path: str) -> str:
    """Create a run_solution job stored under the solution's own sub-directory."""
    key = _solution_key(solution_path)
    ts = int(time.time() * 1000)
    job_id = f"{slug}/{JobType.RUN_SOLUTION}/{key}/{ts}"
    path = _job_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    now = _now_iso()
    data: dict[str, Any] = {
        "id": job_id,
        "slug": slug,
        "type": JobType.RUN_SOLUTION,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "result": None,
        "error": None,
    }
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    return job_id


def get_latest_individual_job_id(slug: str, solution_path: str) -> str | None:
    """Return the most recent individual run_solution job ID for one solution."""
    key = _solution_key(solution_path)
    dir_path = _cache_root() / slug / JobType.RUN_SOLUTION / key
    if not dir_path.exists():
        return None
    files = sorted(dir_path.glob("*.yaml"), key=lambda p: p.stem)
    if not files:
        return None
    return f"{slug}/{JobType.RUN_SOLUTION}/{key}/{files[-1].stem}"


def list_individual_solution_keys(slug: str) -> list[str]:
    """Return encoded keys for all solutions that have a cached individual run."""
    run_dir = _cache_root() / slug / JobType.RUN_SOLUTION
    if not run_dir.exists():
        return []
    return [d.name for d in run_dir.iterdir() if d.is_dir()]


# --- Sequential orchestration ---


@dataclass
class JobTask:
    """A job function bound to its arguments, ready to be called.

    job_id must match the ID that was passed to the job function so that
    run_sequential can mark downstream jobs as skipped on failure.

    Use with run_sequential to chain multiple jobs in order:

        tasks = [
            JobTask(job_id=id1, fn=run_generators_job, args=(problem_dir, req, id1)),
            JobTask(job_id=id2, fn=run_validators_job, args=(problem_dir, req, id2)),
        ]
        bg.add_task(run_sequential, tasks)
    """

    job_id: str
    fn: Callable[..., None]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __call__(self) -> None:
        self.fn(*self.args, **self.kwargs)


def purge_stale_jobs() -> int:
    """Delete all but the latest job file in each {slug}/{type}/ folder.

    Returns the count of files removed.
    """
    root = _cache_root()
    deleted = 0
    if not root.exists():
        return deleted
    for type_dir in root.glob("*/*"):
        if not type_dir.is_dir():
            continue
        files = sorted(type_dir.glob("*.yaml"), key=lambda p: p.stem)
        for stale in files[:-1]:  # keep only the newest
            stale.unlink(missing_ok=True)
            deleted += 1
    return deleted


def run_sequential(tasks: list[JobTask]) -> None:
    """Run a list of JobTasks one after another in the calling thread.

    Designed to be registered as a single FastAPI BackgroundTask so that
    multi-step orchestrations (e.g. generate → validate → run) return all
    their job IDs upfront while still executing in the correct order.

    If a task raises, all remaining jobs are immediately marked 'failed'
    (with an explanatory error message) and execution stops.  Individual
    job functions are responsible for marking themselves failed before
    re-raising, so this only needs to handle the downstream jobs.
    """
    remaining = iter(tasks)
    for task in remaining:
        try:
            task()
        except Exception:
            for skipped in remaining:
                update_job(skipped.job_id, status="failed", error="Skipped: earlier job in sequence failed")
            return
