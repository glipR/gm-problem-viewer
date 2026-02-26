"""
Utilities for running a python command.
"""

import os
import subprocess
from pathlib import Path

from pydantic import BaseModel


class RunFileResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str


def run_python_file(
    file_path: Path,
    stdin: Path | None,
    timeout_sec: float = 1,
    **env_kwargs,
) -> RunFileResult:
    root_dir = Path(__file__).parent.parent.parent.resolve()
    kwargs = {}
    if stdin is not None:
        with open(stdin, "r") as f:
            text = f.read()
        kwargs["input"] = text

    # Append to the current PYTHONPATH if it exists
    python_path = os.pathsep.join([os.environ.get("PYTHONPATH", ""), str(root_dir)])
    # Use a copy of the current environment so you are not affecting the parent
    curr_env = os.environ.copy()
    modified_env = curr_env | {"PYTHONPATH": python_path} | env_kwargs

    result = subprocess.run(
        ["python", str(file_path.resolve())],
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        env=modified_env,
        **kwargs,
    )
    return RunFileResult(
        exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr
    )
