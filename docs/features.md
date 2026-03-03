# Features

Detailed documentation of GM Problem Viewer's features.

[Back to README](../README.md)

---

## Kanban Board

The main view organizes problems into three columns representing their lifecycle state:

- **Draft** — Problems being initially written
- **In Progress** — Problems with active development (tests, validators, solutions)
- **Review** — Problems ready for final review before use

Drag and drop problems between columns to update their state. Each column has a **Create** button to scaffold a new problem directory.

![](/images/kanban.png)

---

## Search & Filter

The Search tab provides full-text search across problem names, tags, and metadata. You can filter by:

- **Tags** — Topic tags (e.g., "dp", "graphs", "implementation")
- **Contest** — Contest association
- **Difficulty** — Codeforces-style rating sort

![](/images/search.png)

---

## Problem Detail Page

Clicking a problem card opens the detail view with a header showing the problem name, badges (type, state, difficulty, tags), author, and time/memory limits. The detail page has several tabs:

### Statement Tab

Renders `statement.md` with full Markdown support including:

- **LaTeX math** — Inline (`$...$`) and display (`$$...$$`) via KaTeX
- **Test blocks** — `:::test_block` directives render sample I/O in formatted blocks
- **Code tabs** — Tabbed code blocks for showing multiple implementations
- **Spoilers** — `||hidden text||` renders as click-to-reveal content
- **Images** — Relative paths resolve to the problem directory; supports `|width=N` in alt text
- **Details/summary** — Collapsible sections for editorial hints

![](/images/statement.png)

### Solutions Tab

Displays all solutions grouped by directory. Each solution shows:

- Name (from frontmatter)
- Expected verdict badge (AC/WA/TLE)
- Run button to execute against all test cases
- Results with per-test-case verdicts when available

Solutions can be run individually or all at once. Results are persisted and the most recent run is shown.

![](/images/solutions.png)

### Tests Tab

A split-panel view:

- **Left panel** — Accordion of test sets, each showing generators and test cases
- **Right panel** — Selected test content viewer with description editor

You can add new test sets and new test cases from this tab. Test generators can be run to produce test files.

![](/images/tests.png)

### Validator Tab

View the outcome for input validators on the test sets. Click each validator to view per-test results

![](/images/validator.png)

### TODO Tab

Write (and hopefully remove) TODOs for the problem

![](/images/todo.png)

### Editorial Tab

Write an editorial, with support for spoiler text, code snippets, and standard mathjax + more.

![](/images/editorial.png)

---

## Solutions

### Frontmatter Format

Solutions embed configuration in their top-level comment block:

```python
"""---
name: Brute Force O(n^2)
expectation: AC
---

Checks all pairs.
"""
```

### Expectations

- **Global**: A single verdict (`AC`, `WA`, `TLE`) applies to all test sets
- **Per-set**: A mapping of `{set_name: verdict}` for different expected outcomes per test set

```yaml
expectation:
  sample: AC
  real: AC
  stress: TLE
```

### Supported Languages

- **Python** — Executed as subprocesses with configurable timeout
- **C++** — Executed as subprocesses with configurable timeout

### Execution Model

Solutions are run as subprocesses. `.in` file content is piped to stdin. The project root is injected into `PYTHONPATH` so test generators can import shared utilities. Execution uses the time limit from the problem's `config.yaml`.

---

## Test Management

### Test Sets

Test sets are directories under `data/`. Each can have:

- **`config.yaml`** — Name, description, points, marking style (`progressive` or `all_or_nothing`)
- **`.in` / `.out` files** — Test input / output
- **Optional `.yaml` sidecars** — Per-test metadata (description of what the case tests)
- **Generator scripts** — Python files that produce `.in`, maybe `.out` and `.yaml` files

### Generators

Generator scripts are Python files colocated with their test set. They use `Path(__file__).parent` to write `.in` files into the correct directory. Generators can be run from the UI.

---

## Validators

### Input Validators

Python scripts under `validators/input/` that read from stdin and use `assert` to validate input constraints. They support:

- **Global scope** — No `checks` field means the validator runs against all test sets
- **Per-set scope** — A `checks` list limits which test sets the validator applies to

```python
"""---
name: Check bounds
checks:
  - real
  - real2
---
"""
import sys

data = sys.stdin.read().split()
n = int(data[0])
assert 1 <= n <= 100000
```

### Output Checkers (Standard Problems)

Optional `validators/output/checker.py` for custom output comparison. If absent, output is compared exactly against the reference solution's output.

The checker receives `input_data`, `process_data` (solution output), `judge_data`, and `points`, and returns a result via `make_result(code, points, comment)`.

### Interactive Judges

Required for interactive problems as `validators/output/judge.py`. The judge communicates with the solution via `read_line()` and `write_line()` stubs, and returns a verdict via `make_result()`.

---

## Review System

The review system runs deterministic checks in two phases:

### Phase 1 — Blocking Issues

These must be resolved before a problem is considered ready:

- **Statement structure** — Requires Input/Output headers (standard) or Interaction section (interactive)
- **Sample test cases** — Standard problems must have test cases in a 0-point test set
- **AC solution** — At least one solution with `AC` expectation must exist
- **Expectation coverage** — Every per-set solution expectation must have a corresponding test set with cases

### Phase 2 — Improvement Suggestions

Optional but recommended:

- **Input validation** — Input validators should exist
- **Test generators** — At least one generator recommended
- **Verdict diversity** — Solutions for WA/TLE verdicts help validate the checker
- **Sub-task solutions** — Non-zero point test sets should have sub-task-only solutions
- **Multiple languages** — Solutions in 2+ languages preferred
- **Editorial** — An editorial should exist and be substantive (100+ characters)

### Progress Tracking

Each check category (Statement, Solution, Validator, Test) gets a color:
- **Red** — Phase 1 failures (blocking)
- **Yellow** — Phase 1 passes but Phase 2 has suggestions
- **Green** — All checks pass

---

## AI Review

AI-powered checks use a local `claude` CLI subprocess to analyze problems. Six checks are available:

1. **Output Validator Alignment** — Verifies the checker/judge aligns with statement requirements; can create or fix validators
2. **Input Validator Coverage** — Checks that input validators cover all constraints mentioned in the statement; can create or edit validators
3. **Boundary Test Coverage** — Analyzes test generators for missing edge cases (analysis only)
4. **Statement Spelling** — Fixes typos and grammar in `statement.md`
5. **Solution Optimality** — Evaluates whether AC solutions use optimal algorithms (analysis only)
6. **Editorial Spelling** — Fixes typos and grammar in `editorial.md`

AI checks that modify files do so directly — changes appear in your problem directory and can be reviewed via git diff.

---

## Export

### DMOJ Export

The DMOJ exporter (`POST /problems/{slug}/export/`) produces a complete DMOJ problem package:

- Renders and compiles the statement
- Copies solutions with folder-structure-prefixed names to `sol/`
- Copies input validators with `val_inp_` prefix
- Transforms output validators (wraps checkers in DMOJ template, converts interactive judges to DMOJ grader format)
- Creates `init.yml` with test layout, checker/judge references, and point values

### Export Configuration

Configure in the problem's `config.yaml`:

```yaml
export_config:
  my-target:
    type: dmoj
    location: /path/to/output
    dmoj_config:
      include_archive: true
    clear_directory: true
```

Other export types (`problemtools`, `direct-copy`) are planned but not yet implemented.

---

## Configuration

### Global Configuration (`config.yaml`)

Located at the project root. Copy the annotated template to get started:

```bash
cp config.example.yaml config.yaml
```

```yaml
problems_root: examples    # path to problems directory
cache_root: .cache         # path for job cache files
port: 8001                 # server port
```

### Environment Variables

Environment variables take priority over `config.yaml`:

| Variable | Description |
|---|---|
| `PROBLEMS_ROOT` | Path to problems directory |
| `CACHE_ROOT` | Path for job cache files |
| `PORT` | Server port |

### Problem Configuration

Each problem has its own `config.yaml` — see [Problem Format](problem-format.md) for the full schema.

### Test Set Configuration

Each test set can have a `config.yaml` with `name`, `description`, `points`, and `marking_style`.
