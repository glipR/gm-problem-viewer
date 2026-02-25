This document details the exact schemata of problems you'll define.
This departs from existing formats in a few key locations.

---

## Directory Structure

Each problem lives in a directory named after its slug (e.g., `maximum_of_list/`, `guess_a_number/`):

```
<problem_slug>/
├── config.yaml
├── statement.md
├── data/
│   └── <set_name>/             # e.g. "real", "setA", "setB", "sample"
│       ├── <gen_tests or some other name>.py        # Test generators are colocated with problem sets (optional)
│       ├── <name>.in           # Test input
│       └── <name>.yaml         # optional sidecar metadata
├── solutions/
│   ├── <name>.py               # flat solution file
│   └── <group_name>/           # or grouped into a subdirectory
│       └── <name>.py
└── validators/
    ├── input/
    │   ├── <name>.py           # validator for input files (can be scoped to sets, or global)
    └── output/
        ├── checker.py          # standard problems
        └── judge.py            # interactive problems
```

---

## `config.yaml`

```yaml
name: <Human-readable problem name>       # required
type: standard | interactive              # required
tags:                                     # optional list of topic tags
  - <tag>
difficulty: <integer>                     # optional; Codeforces-style rating (e.g. 800, 1200)
export_config:                            # optional; keyed by export target name
  <target_name>:
    type: problemtools | dmoj | direct-copy
    location: <path>
    problemtools_config: {}               # for type: problemtools
    dmoj_config:                          # for type: dmoj
      include_archive: <bool>
```

---

## `statement.md`

This is up to the user, but includes a few plugins to aid 

```markdown
:::test_block
@include[sample/1.in]
:::
```

LaTeX math uses `$...$` inline, `$$...$$` separate line. Constraints use a bullet list.

---

## Test Data

### Input files (`.in`)

All test cases are `.in` files only — there are **no** `.out` files saved. For standard problems, the .out files are generated on the fly from a base specified solution.

For **standard** problems, `.in` files contain the raw problem input as a contestant would receive it.

For **interactive** problems, `.in` files contain the judge's private information (e.g., the secret number and query limit: `169 51`). The format is problem-defined.

### Test sets

- Can be named whatever. `config.yaml` within the folder specifies some metadata 

### `<test_set>/config.yaml`

```yaml
name: <Human-readable set name>
description: optional string
points: float
marking_style: progressive | all_or_nothing
```

### Sidecar metadata (`<test_name>.yaml`)

A `.yaml` file with the same stem as a `.in` file provides optional metadata:

```yaml
description: <string>   # human-readable description of what this case tests
```

### `<test_set>/<gen_name>.py`

A script that generates `.in/.yaml` files into its own directory. For now, uses `Path(__file__).parent` to get a reference to the folder to create files within.

---

## Solutions

Solutions are Python/CPP files. Every solution has a docstring at the top containing a YAML frontmatter block:

```python
"""---
name: <Human-readable solution name>
expectation: AC | WA | TLE | ...
---

Optional prose description of the approach.
"""
```

```c++
/*---
name: <Human-readable solution name>
expectation: AC | WA | TLE | ...
---

Optional prose description of the approach
*/

```

### `expectation` field

A single verdict string means the expectation applies to all test sets in aggregate:
```yaml
expectation: AC # Should pass all tests
expectation: WA # Should WA at least one test
```

A mapping of `{set_name: verdict}` mappings gives per-test-set expectations:
```yaml
expectation:
  sample: AC
  setA: AC
  setB: WA
```

Valid verdict strings: `AC`, `WA`, `TLE`.

### Solution file organization

Solutions can be placed either as flat `.py` files directly under `solutions/`, or grouped into a subdirectory (with any name) under `solutions/`. The directory name is purely organizational; the frontmatter is the source of truth.

---

## Validators

### Input validators (`validators/input/<name>.py`)

Input validators read from stdin and use Python `assert` statements to validate constraints. A passing run (no assertion errors) means the input is valid.

Every input validator has a docstring frontmatter:

```python
"""---
name: <Human-readable name>
checks:            # optional; if absent, applies to ALL test sets
  - <set_name>
---

Optional description.
"""
```

- If `checks` is **absent**, the validator applies to every test case (i.e., it checks the "complete" constraints).
- If `checks` is **present**, the validator only runs on test cases in the listed sets.

### Output checker — standard (`validators/output/checker.py`)

Used optionally for standard (non-interactive) problems. The framework calls `check(...)` and provides stub implementations of `make_result`.

If no output check is provided for standard problems, `.out` files should be generated from a known complete solution and compared.

```python
def make_result(code: str, points: float, comment: str):
    pass  # stub; implemented by the framework

def check(input_data: str, process_data: str, judge_data: str, points: float):
    # input_data:   raw contents of the .in file
    # process_data: the solution's stdout
    # judge_data:   unused / reserved for a reference answer
    # points:       point value assigned to this test case
    # Returns make_result(...)
    ...
```

No frontmatter is required for checkers.

### Interactive judge (`validators/output/judge.py`)

Used for interactive problems (required). The framework calls `grade(...)` and provides stubs for I/O and result construction.

```python
def read_line() -> str:
    pass  # reads one line from the solution's stdout

def write_line(s: str):
    pass  # writes one line to the solution's stdin

def make_result(code: str, points: float, comment: str):
    pass  # stub; implemented by the framework

def grade(input_file: str, points: float):
    # input_file: raw contents of the .in file (the judge's private data)
    # points:     point value assigned to this test case
    # Returns make_result(...)
    ...
```

The judge file may have a docstring frontmatter with `name` and optionally `description`, though it is not required.
