from contextlib import contextmanager
import os
import inspect
from collections import defaultdict
from pathlib import Path

import yaml

rpt_map = defaultdict(lambda: 0)


@contextmanager
def test_case(
    rpt_name=None,
    case_name=None,
    relative_dir="../",
    **config,
):
    # First, get __file__ of the code that calls this function
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back.f_back  # two levels up - avoid context manager
        caller_file = caller_frame.f_code.co_filename
        caller_file = Path(os.path.abspath(caller_file))
    except Exception as e:
        raise e
    finally:
        del frame

    class WriterObj:
        def __init__(self, path: str, extra: str | None = None):
            self.path = path
            self.writer = None
            self.output = None
            if extra:
                self.output = WriterObj(extra)

        def write_lines(self, lines: list[str]):
            if self.writer is None:
                self.writer = open(self.path, "w")
            self.writer.write("\n".join(map(str, lines)) + "\n")

        def write_line(self, line: str):
            if self.writer is None:
                self.writer = open(self.path, "w")
            self.writer.write(str(line) + "\n")

        def close(self):
            if self.writer:
                self.writer.close()
            if self.output:
                self.output.close()

    directory = (caller_file / relative_dir).resolve()
    if case_name is None and rpt_name is None:
        raise ValueError("Need case name or repeat name")
    if case_name:
        fname = f"{case_name}.in"
    elif rpt_name:
        rpt_map[rpt_name] += 1
        fname = f"{rpt_name}{rpt_map[rpt_name]}.in"
    writer = WriterObj(directory / fname, (directory / fname).with_suffix(".out"))
    yield writer

    writer.close()

    # Configuration write
    def get_data_dir(p: Path):
        if p.name == "data":
            return p
        return get_data_dir(p.parent)

    cfg = {"generated_by": str(caller_file.relative_to(get_data_dir(caller_file)))}
    cfg.update(config)

    with open((directory / fname).with_suffix(".yaml"), "w") as f:
        f.write(yaml.safe_dump(cfg))
