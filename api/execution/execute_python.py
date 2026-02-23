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
    kwargs = {}
    if stdin is not None:
        with open(stdin, "r") as f:
            text = f.read()
        kwargs["input"] = text
    result = subprocess.run(
        ["pypy3", str(file_path.resolve())],
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        **kwargs,
    )
    return RunFileResult(
        exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr
    )
