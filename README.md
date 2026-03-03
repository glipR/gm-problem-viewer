# GM Problem Viewer

A local-first tool for authoring, testing, and reviewing competitive programming problems.

GM Problem Viewer gives you a web UI on top of your problem directories — manage problem lifecycle on a Kanban board, render statements with custom markdown snippets, execute solutions, generate tests, run validators, and export to common online judge formats.


|     |     |     |
| --- | --- | --- |
| ![](/images/kanban.png) | ![](/images/search.png) | ![](/images/statement.png) |
| ![](/images/solutions.png) | ![](/images/tests.png) | ![](/images/editorial.png) |

## Key Features

- **Kanban board** — Drag problems through Draft / In Progress / Review stages
- **Statement rendering** — Markdown + LaTeX math + code tabs + spoilers + image embedding
- **Solution execution** — Run Python/C++ solutions with automatic verdict tracking (AC/WA/TLE/RTE)
- **Test management** — Hand-written tests, Python generators, sidecar metadata, on-the-fly output generation
- **Input/output validators** — Assert-based input validators with per-set scoping, custom checkers and interactive judges
- **Deterministic review** — Automated checklist of blocking issues and improvement suggestions with color-coded progress
- **AI-powered review** — Statement proofreading, validator coverage analysis, boundary test suggestions, solution optimality checks
- **Export** — Export to DMOJ format (more targets planned)
- **Search & filter** — Full-text search with tag, contest, and difficulty filtering

## Quick Start

**Prerequisites:** Python 3.11+, Node 24+, [uv](https://docs.astral.sh/uv/), npm

```bash
git clone <repo-url> && cd gm-problem-viewer

# Install dependencies
./setup.sh

# Launch backend + frontend
./start.sh
```

The UI opens at **http://localhost:5173** and the API at **http://localhost:8001** (docs at `/docs`).

By default, the bundled `examples/` directory is used. Copy `config.example.yaml` to `config.yaml` and point `problems_root` at your own problems directory.

See [Getting Started](docs/getting-started.md) for a full walkthrough of creating your first problem.

![](/images/statement.png)

## Configuration

Settings are resolved in priority order: **environment variables** > **`config.yaml`** (project root) > **defaults**. See [`config.example.yaml`](config.example.yaml) for an annotated template.

| Setting | Env var | `config.yaml` key | Default |
|---|---|---|---|
| Problems directory | `PROBLEMS_ROOT` | `problems_root` | `examples/` |
| Job cache directory | `CACHE_ROOT` | `cache_root` | `.cache/` |
| Server port | `PORT` | `port` | `8001` |

## Documentation

- **[Getting Started](docs/getting-started.md)** — Installation, setup, and creating your first problem
- **[Problem Format](docs/problem-format.md)** — Full schema reference for problem directories
- **[Features](docs/features.md)** — Detailed documentation of all features

## Project Structure

```
api/
├── routes/         # FastAPI routers (thin HTTP layer)
├── collection/     # Disk-reading logic (problems, solutions, tests, validators, statements)
├── execution/      # Subprocess runners (solutions, test generation, validators)
├── checks/         # Deterministic + AI review checks
├── export/         # Export implementations (DMOJ)
├── models/         # Pydantic models
├── jobs.py         # Filesystem-backed async job system
└── config.py       # Settings

frontend/src/
├── pages/          # KanbanPage, SearchPage, ProblemDetailPage
├── components/     # Kanban board, detail tabs, overlays
├── api/            # Axios API client
├── types/          # TypeScript types mirroring backend models
└── store/          # Zustand state management
```

## Development

```bash
# Backend only
uv run python -m api

# Frontend only (requires Node 24 via nvm)
cd frontend && npm run dev

# Custom port
PORT=9000 uv run python -m api

# Custom problems directory
PROBLEMS_ROOT=/path/to/problems uv run python -m api
```

API docs available at `http://localhost:8001/docs` when the backend is running. The frontend dev server proxies `/api/*` to the backend automatically.
