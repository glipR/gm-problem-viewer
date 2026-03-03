# Getting Started

A step-by-step guide to setting up GM Problem Viewer and creating your first problem.

[Back to README](../README.md)

---

## Prerequisites

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Node 24+** — Install via [nvm](https://github.com/nvm-sh/nvm): `nvm install v24`
- **uv** — Python package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **npm** — Comes with Node

---

## Installation

```bash
git clone <repo-url>
cd gm-problem-viewer
./setup.sh
```

The setup script installs Python dependencies (via `uv sync`) and frontend dependencies (via `npm install`).

---

## Running

```bash
./start.sh
```

This launches both the backend API and the frontend dev server:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8001 (interactive docs at http://localhost:8001/docs)

Press `Ctrl+C` to stop both servers.

---

## Pointing to Your Problems

By default, the bundled `examples/` directory is used. To use your own problems:

**Option 1 — `config.yaml`** (recommended):

Copy the annotated template and edit it:

```bash
cp config.example.yaml config.yaml
```

```yaml
problems_root: /path/to/your/problems
```

**Option 2 — Environment variable**:

```bash
PROBLEMS_ROOT=/path/to/your/problems ./start.sh
```

Your problems directory should contain subdirectories, one per problem, following the [Problem Format](problem-format.md).

---

## Creating a New Problem

### Via the UI

Click the **Create** button in any Kanban column. This scaffolds a new problem directory with the basics.

### Manually

Create a directory under your problems root:

```bash
mkdir -p my_problem/{data/sample,solutions,validators/input,validators/output}
```

### 1. Write `config.yaml`

```yaml
name: My First Problem
type: standard
state: draft
difficulty: 800
tags:
  - implementation
limits:
  time: 1
  memory: 262144
```

### 2. Write `statement.md`

```markdown
# My First Problem

Given an integer $n$, print $n \times 2$.

## Input

A single integer $n$ ($1 \le n \le 10^9$).

## Output

Print $n \times 2$.

:::test_block
@include[sample/1.in]
:::
```

### 3. Add a Solution

Create `solutions/correct.py`:

```python
"""---
name: Correct solution
expectation: AC
---
"""
n = int(input())
print(n * 2)
```

Optionally add a wrong solution to `solutions/wrong.py`:

```python
"""---
name: Off by one
expectation: WA
---
"""
n = int(input())
print(n * 2 + 1)
```

### 4. Add Test Cases

Create a sample test at `data/sample/1.in`:

```
5
```

For more tests, create another test set directory (e.g., `data/real/`) and either add `.in` files manually or write a generator:

`data/real/gen.py`:

```python
from pathlib import Path
import random

out_dir = Path(__file__).parent

for i in range(10):
    n = random.randint(1, 10**9)
    (out_dir / f"rand-{i+1}.in").write_text(f"{n}\n")
    (out_dir / f"rand-{i+1}.yaml").write_text(f"description: Random case {i+1}\n")
```

Add a `data/real/config.yaml`:

```yaml
name: Random Tests
points: 100
```

### 5. Add an Input Validator

Create `validators/input/bounds.py`:

```python
"""---
name: Check bounds
---
"""
import sys

data = sys.stdin.read().split()
assert len(data) == 1, "Expected exactly one integer"
n = int(data[0])
assert 1 <= n <= 10**9, f"n={n} out of bounds"
```

### 6. Run and Review

Open the UI at http://localhost:5173. Your problem should appear on the Kanban board. Click it to:

1. **Statement tab** — Verify the rendered statement looks correct
2. **Solutions tab** — Click **Run** to execute solutions against all tests
3. **Tests tab** — View test cases, run generators, add new tests
4. **Review** — Click the **Review** button to run the deterministic checklist

The review system will flag any issues (missing sample tests, no AC solution, etc.) and suggest improvements (add input validators, test generators, editorial, etc.).

---

## Next Steps

- Read the full [Problem Format](problem-format.md) reference for all configuration options
- See [Features](features.md) for detailed documentation on each feature
- Explore the bundled `examples/` problems (`maximum_of_list` and `guess_a_number`) for real-world examples
- Try the **AI Review** feature to get automated feedback on validator coverage, boundary tests, and statement quality
