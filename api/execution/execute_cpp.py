"""
Utilities for compiling and running a C++ file.
"""

import hashlib
import subprocess
from pathlib import Path

from api.config import get_settings
from api.execution.execute_python import RunFileResult


class CompileError(Exception):
    """Raised when g++ compilation fails."""

    def __init__(self, stderr: str):
        self.stderr = stderr
        super().__init__(stderr)


def _binary_path(source_path: Path) -> Path:
    """Deterministic binary path based on source file content + mtime."""
    stat = source_path.stat()
    key = f"{source_path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    cache_dir = get_settings().cache_root / "cpp_binaries"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{source_path.stem}_{digest}"


def compile_cpp(
    source_path: Path,
    *,
    extra_flags: list[str] | None = None,
) -> Path:
    """
    Compile a C++ source file, returning the path to the binary.

    Uses a content-addressed cache so unchanged sources are not recompiled.
    Raises CompileError on compilation failure.
    """
    binary = _binary_path(source_path)
    if binary.exists():
        return binary

    flags = list(get_settings().cpp_flags)
    if extra_flags:
        flags = flags + extra_flags

    result = subprocess.run(
        ["g++", *flags, "-o", str(binary), str(source_path.resolve())],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise CompileError(result.stderr)
    return binary


def run_cpp_file(
    file_path: Path,
    stdin: Path | None,
    timeout_sec: float = 1,
    *,
    extra_flags: list[str] | None = None,
) -> RunFileResult:
    """
    Compile (if needed) and run a C++ source file.

    Mirrors the signature of run_python_file: takes a source path, optional
    stdin file, and timeout. Returns RunFileResult with exit_code/stdout/stderr.

    Raises CompileError if compilation fails.
    """
    binary = compile_cpp(file_path, extra_flags=extra_flags)

    kwargs = {}
    if stdin is not None:
        with open(stdin, "r") as f:
            text = f.read()
        kwargs["input"] = text

    result = subprocess.run(
        [str(binary)],
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        **kwargs,
    )
    return RunFileResult(
        exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr
    )
