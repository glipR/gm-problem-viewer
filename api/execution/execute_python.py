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


def run_python_file(file_path: Path, stdin: Path | None) -> RunFileResult:
    result = subprocess.run(
        ["python", str(file_path.resolve())],
        stdin=stdin,
        text=True,
        capture_output=True,
    )
    return RunFileResult(
        exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr
    )
