"""
Utilities for running a python command.
"""

import subprocess
from pathlib import Path

from pydantic import BaseModel


class RunFileResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str


def run_python_file(
    file_path: Path, stdin: Path | None, timeout_sec: float = 1
) -> RunFileResult:
    # TODO: Add TLE support.
    with open(stdin, "r") as f:
        text = f.read()
    result = subprocess.run(
        ["python", str(file_path.resolve())],
        input=text,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
    )
    return RunFileResult(
        exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr
    )
