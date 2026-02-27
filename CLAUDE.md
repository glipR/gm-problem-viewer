# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands


### Backend (FastAPI)

Backend Commands in general shouldn't be used in chats - just write the code and the human can do manual review and testing.

```bash
# Run server (default port 8001)
uv run python -m api

# Custom port
PORT=9000 uv run python -m api

# Run with custom problems directory
PROBLEMS_ROOT=/path/to/problems uv run python -m api
```

API docs available at `http://localhost:8001/docs` when running.

### Frontend (Vite + React)

```bash
# Must use Node v24 via nvm; run from fish shell
fish -c "nvm use v24.13.0 && cd frontend && npm run dev"
```

Dev server proxies `/api/*` → `http://localhost:8001/*`.

## Configuration

Settings are resolved from (in priority order): env vars → `config.yaml` at project root → defaults.

| Setting | Env var | Default |
|---|---|---|
| Problems directory | `PROBLEMS_ROOT` | `examples/` |
| Job cache directory | `CACHE_ROOT` | `.cache/` |
| Server port | `PORT` | `8001` |

## Architecture

### Backend layers

```
api/
├── routes/       # FastAPI routers — thin HTTP layer only
├── collection/   # Disk-reading logic (problems, solutions, test sets, validators, statement)
├── execution/    # Subprocess runners (execute_python, run_testcase, run_validators, run_testgen)
├── checks/       # Deterministic review checks (solutions, statement, tests, validators, collated)
├── models/       # Pydantic models for all domain objects + request/response types
├── jobs.py       # Filesystem-backed async job system
└── config.py     # Settings (PROBLEMS_ROOT, CACHE_ROOT, PORT)
```

**Async job pattern**: Long-running operations (run solutions, validators, test generators, review) return `{ job_ids: [...] }` immediately and run via FastAPI `BackgroundTasks`. Jobs are stored as YAML files under `.cache/{slug}/{type}/{timestamp_ms}.yaml`. Poll via `GET /jobs/{job_id}`. Use `run_sequential(tasks)` to chain dependent jobs (e.g., generate → validate → run).

### Frontend

State-based navigation: `App.tsx` holds `selectedSlug` — when set, renders `ProblemDetailPage`; when null, renders the Kanban/Search tabs.

```
src/
├── App.tsx                        # Top-level navigation
├── pages/
│   ├── KanbanPage.tsx             # Board grouped by problem state
│   ├── SearchPage.tsx             # Full-text + tag search
│   └── ProblemDetailPage.tsx      # Per-problem view (tabs: Statement, Solutions, Tests, Review)
├── components/
│   ├── kanban/                    # Board, lane, card components
│   └── detail/                   # StatementTab, SolutionsTab, TestsTab, ProgressOverlay
├── api/problems.ts                # All API calls (axios, baseURL=/api)
├── types/problem.ts               # TypeScript types mirroring Pydantic models
└── store/problemsStore.ts         # Zustand store
```

### Problem format

Problems live as subdirectories under `PROBLEMS_ROOT`. Each contains:
- `config.yaml` — name, type (`standard`|`interactive`), tags, difficulty, state, author, limits, export_config
- `statement.md` — problem statement (LaTeX math, `:::test_block` directives)
- `data/<set_name>/` — test sets; each has optional `config.yaml`, `.in` files, `.yaml` sidecar metadata, and generator `.py` scripts
- `solutions/` — `.py` or `.cpp` files with YAML frontmatter in docstring (`name`, `expectation`)
- `validators/input/` — Python validators using `assert`, with optional `checks` frontmatter field to scope to test sets
- `validators/output/checker.py` (standard) or `validators/output/judge.py` (interactive)

**No `.out` files are stored** — output is generated on-the-fly from a reference solution (AC expectation) and compared.

### Frontmatter parsing

Solutions and validators embed YAML config in their top-level comment block (`"""..."""` for Python, `/*...*/` for C++). Parsed by `api/utils/frontmatter.py`. The format is:

```python
"""---
name: Human-readable name
expectation: AC | WA | TLE  # or dict of {set_name: verdict}
---

Optional prose description.
"""
```

### Review system

`api/checks/` contains individual check functions organized by category (`CheckCategory` enum). `api/checks/collated.py` runs them in two phases: phase 1 (blocking issues like missing AC solution or sample test) and phase 2 (improvement suggestions). Returns `ReviewResult` with per-category color coding (red/yellow/green).

### Solution execution

`api/execution/execute_python.py` runs Python files as subprocesses with a configurable timeout, piping `.in` file content to stdin. The project root is injected into `PYTHONPATH` so test generators can import from `api/`. C++ solutions are not yet implemented.

## Key conventions

- Routes use `get_settings()` for the problems root; all disk I/O goes through `api/collection/`.
- `list_problems()` is lightweight (config only); `get_problem()` loads everything.
- Job IDs encode `{slug}/{type}/{timestamp_ms}` — the path structure matches the filesystem layout under `.cache/`.
- Individual solution runs use a deeper path: `{slug}/run_solution/{solution_path_encoded}/{timestamp_ms}` so each solution has its own history; `GET /problems/{slug}/solutions/merged-results` coalesces group + individual runs, preferring the more recent timestamp.
- Cursor editor integration: several routes open files via `subprocess.Popen(["cursor", workspace, file])`.
