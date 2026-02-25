import os
import inspect
from collections import defaultdict
from pathlib import Path

import yaml

rpt_map = defaultdict(lambda: 0)


def write_test_case(
    case_data: str,
    rpt_name=None,
    case_name=None,
    relative_dir="../",
    out_data=None,
    **config,
):
    # First, get __file__ of the code that calls this function
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back  # one level up
        caller_file = caller_frame.f_code.co_filename
        caller_file = Path(os.path.abspath(caller_file))
    except Exception as e:
        raise e
    finally:
        del frame

    directory = (caller_file / relative_dir).resolve()
    if case_name is None and rpt_name is None:
        raise ValueError("Need case name or repeat name")
    if case_name:
        fname = f"{case_name}.in"
    elif rpt_name:
        rpt_map[rpt_name] += 1
        fname = f"{rpt_name}{rpt_map[rpt_name]}.in"
    with open(directory / fname, "w") as f:
        f.write(case_data)
    if out_data:
        with open((directory / fname).with_suffix(".out"), "w") as f:
            f.write(out_data)

    # Configuration
    def get_data_dir(p: Path):
        if p.name == "data":
            return p
        return get_data_dir(p.parent)

    cfg = {"generated_by": str(caller_file.relative_to(get_data_dir(caller_file)))}
    cfg.update(config)

    with open((directory / fname).with_suffix(".yaml"), "w") as f:
        f.write(yaml.safe_dump(cfg))
