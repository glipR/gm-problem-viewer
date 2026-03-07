# Problem Format Reference

This document details the schema for problem directories used by GM Problem Viewer.

[Back to README](../README.md)

---

## Quick Example

A minimal problem directory looks like this:

```
my_problem/
├── config.yaml         # name, type, and metadata
├── statement.md        # problem statement with LaTeX support
├── data/
│   └── sample/
│       └── 1.in        # sample test input
├── solutions/
│   └── brute.py        # solution with frontmatter
└── validators/
    └── input/
        └── bounds.py   # input validator
```

The bundled `examples/` directory contains two complete problems:
- **`maximum_of_list`** — A standard problem with multiple test sets, generators, per-set solution expectations, and DMOJ export config
- **`guess_a_number`** — An interactive problem with a custom judge (`judge.py`)

---

## Directory Structure

Each problem lives in a directory named after its slug (e.g., `maximum_of_list/`, `guess_a_number/`):

```
<problem_slug>/
├── config.yaml
├── statement.md
├── editorial.md                    # optional editorial
├── data/
│   └── <set_name>/                 # e.g. "real", "setA", "setB", "sample"
│       ├── config.yaml             # optional set metadata
│       ├── <gen_name>.py           # test generators (optional)
│       ├── <name>.in               # test input
│       └── <name>.yaml             # optional sidecar metadata
├── solutions/
│   ├── <name>.py                   # flat solution file
│   └── <group_name>/               # or grouped into a subdirectory
│       └── <name>.py
└── validators/
    ├── input/
    │   └── <name>.py               # validator for input files
    └── output/
        ├── checker.py              # standard problems
        └── judge.py                # interactive problems
```

---

## `config.yaml`

```yaml
name: <Human-readable problem name>       # required
type: standard | interactive              # required
state: draft | in-progress | review       # optional; used by Kanban board
author: <string>                          # optional
difficulty: <integer>                     # optional; Codeforces-style rating (e.g. 800, 1200)
quality: <integer>                       # optional; 1-5 star rating
tags:                                     # optional list of topic tags
  - <tag>
contests:                                 # optional list of contest slugs
  - <contest>
limits:                                   # optional
  time: <seconds>                         # default: 1
  memory: <bytes>                         # default: 262144 (256 MB)
visibility: public | private              # optional; default: private
external_judge_url: <url>                 # optional; link to try the problem on an external judge
export_config:                            # optional; keyed by export target name
  <target_name>:
    type: problemtools | dmoj | direct-copy
    location: <path>
    problemtools_config: {}               # for type: problemtools
    dmoj_config:                          # for type: dmoj
      include_archive: <bool>
```

### `visibility`

Controls whether a problem is included in the public static site (see [Static Site](static-site.md)). Problems default to `private` and must be explicitly set to `public` to appear on the generated site.

### `external_judge_url`

An optional URL linking to the problem on an external online judge (e.g. DMOJ, Codeforces). When set, the static site displays a "Try on Judge" button.

---

## `statement.md`

Problem statements are written in Markdown with the following extensions:

- **LaTeX math**: `$...$` for inline, `$$...$$` for display
- **Test blocks**: Include sample test cases with the `@include` directive:
  ```markdown
  @include[sample/1.in][sample/1.out]{title: "Test Title"}
  ```
- **Code includes**: `@code_include[path]` to embed code files
- **Spoilers**: `||hidden text||` for click-to-reveal content
- **Images**: Relative paths resolve to the problem directory

---

## Test Data

### Input files (`.in`)

For **standard** problems, `.in` files contain the raw problem input as a contestant would receive it.

For **interactive** problems, `.in` files contain the judge's private information (e.g., the secret number and query limit: `169 51`). The format is problem-defined.

### Output files (`.out`)

Either test generators can generate expected output files, or the candidate solution can be used to generate the output file when it runs.

### Test sets

Test sets are subdirectories under `data/`. They can be named anything. A `config.yaml` within the folder specifies metadata.

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

A script that generates `.in`/`.yaml` files into its own directory. Uses `Path(__file__).parent` to get a reference to the folder to create files within.

---

## Solutions

Solutions are Python or C++ files. Every solution has a docstring at the top containing a YAML frontmatter block:

**Python:**
```python
"""---
name: <Human-readable solution name>
expectation: AC | WA | TLE | ...
---

Optional prose description of the approach.
"""
```

**C++:**
```cpp
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
expectation: AC   # Should pass all tests
expectation: WA   # Should WA at least one test
```

A mapping of `{set_name: verdict}` gives per-test-set expectations:
```yaml
expectation:
  sample: AC
  setA: AC
  setB: WA
```

Valid verdict strings: `AC`, `WA`, `TLE`.

### Solution file organization

Solutions can be placed either as flat files directly under `solutions/`, or grouped into subdirectories. The directory name is purely organizational; the frontmatter is the source of truth.

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

- If `checks` is **absent**, the validator applies to every test case (global constraints).
- If `checks` is **present**, the validator only runs on test cases in the listed sets.

### Output checker — standard (`validators/output/checker.py`)

Used optionally for standard (non-interactive) problems. The framework calls `check(...)` and provides stub implementations of `make_result`.

If no output checker is provided for standard problems, output is compared against the reference solution's output.

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
