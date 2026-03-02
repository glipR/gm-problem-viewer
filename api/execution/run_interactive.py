"""
Run an interactive problem: spawn the solution as a subprocess and drive it
with a judge.py that defines read_line, write_line, make_result, and grade.

The judge module is loaded dynamically; we replace its read_line / write_line /
make_result with implementations wired to the solution subprocess, then call
grade(input_data, points).
"""

import importlib.util
import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InteractiveResult:
    verdict: str  # "AC" | "WA" etc.
    points: float
    comment: str


class _ResultSignal(BaseException):
    """Raised by make_result to short-circuit grade() and capture the result."""

    def __init__(self, result: InteractiveResult):
        self.result = result


def run_interactive_testcase(
    problem_path: Path,
    judge_path: Path,
    solution_cmd: list[str],
    input_data: str,
    points: float,
    timeout_sec: float,
) -> InteractiveResult:
    """
    Spawn *solution_cmd* as a subprocess, load the judge from *judge_path*,
    wire up read_line/write_line/make_result, and call grade(input_data, points).
    """
    root_dir = Path(__file__).parent.parent.parent.resolve()
    python_path = os.pathsep.join(
        [os.environ.get("PYTHONPATH", ""), str(root_dir)]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = python_path

    proc = subprocess.Popen(
        solution_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    # -- Patch functions onto the judge module --

    def read_line() -> str:
        line = proc.stdout.readline()
        if not line:
            raise EOFError("Solution closed stdout")
        return line.rstrip("\n")

    def write_line(s: str) -> None:
        proc.stdin.write(str(s) + "\n")
        proc.stdin.flush()

    def make_result(code: str, pts: float, comment: str = ""):
        raise _ResultSignal(InteractiveResult(verdict=code, points=pts, comment=comment))

    # Load the judge module, then patch the stub functions with our wired versions.
    # (exec_module runs the module body which re-defines the stubs, so we patch after.)
    spec = importlib.util.spec_from_file_location("_judge", judge_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.read_line = read_line
    mod.write_line = write_line
    mod.make_result = make_result

    # Run grade() in a thread so we can enforce the timeout
    result_holder: list[InteractiveResult] = []
    exc_holder: list[Exception] = []

    def _run():
        try:
            mod.grade(input_data, points)
            # If grade() returns without calling make_result, treat as WA
            result_holder.append(
                InteractiveResult(verdict="WA", points=0, comment="Judge returned without calling make_result")
            )
        except _ResultSignal as sig:
            result_holder.append(sig.result)
        except EOFError:
            result_holder.append(
                InteractiveResult(verdict="WA", points=0, comment="Solution closed stdout unexpectedly")
            )
        except Exception as e:
            exc_holder.append(e)

    thread = threading.Thread(target=_run)
    thread.start()
    thread.join(timeout=timeout_sec)

    if thread.is_alive():
        proc.kill()
        proc.wait()
        thread.join(timeout=2)
        return InteractiveResult(verdict="TLE", points=0, comment="Time Limit Exceeded")

    # Clean up
    try:
        proc.stdin.close()
    except Exception:
        pass
    try:
        proc.stdout.close()
    except Exception:
        pass
    if proc.poll() is None:
        proc.kill()
    proc.wait()

    if exc_holder:
        raise exc_holder[0]

    return result_holder[0] if result_holder else InteractiveResult(
        verdict="IE", points=0, comment="No result from judge"
    )
