# Static Site

[Back to README](../README.md)

---

GM Problem Viewer includes a static site generator for sharing public problems. The generated site requires no backend or database — it produces plain HTML/JS/CSS that can be hosted on GitHub Pages or any static hosting provider.

## What the static site shows

- **Statement** and **editorial** tabs (with full markdown rendering: LaTeX math, code tabs, spoilers, test I/O tables)
- Problem metadata (name, type, author, time/memory limits)
- **Tags and difficulty** are hidden by default to avoid spoilers — viewers can reveal them with a click
- **"Try on Judge"** link when `external_judge_url` is set in the problem config

The static site intentionally does **not** expose solutions, validators, test cases, or any development tooling.

## Marking problems as public

Only problems with `visibility: public` in their `config.yaml` are included. All other problems are ignored during build.

```yaml
# config.yaml
name: My Problem
type: standard
visibility: public
external_judge_url: https://judge.example.com/problem/my-problem  # optional
```

See [Problem Format](problem-format.md) for the full config reference.

## Building locally

**Prerequisites:** Python 3.11+, Node 24+, [uv](https://docs.astral.sh/uv/), npm

```bash
# 1. Generate problem data (JSON + images)
uv run python site/build.py

# With a custom problems directory:
uv run python site/build.py --problems-root /path/to/problems

# 2. Install frontend dependencies (first time only)
cd site && npm install

# 3. Build the static site
npm run build

# 4. Preview locally
npm run preview
# Opens at http://localhost:4173
```

The build process has two stages:

1. **`site/build.py`** — Python script that reads problems from disk, filters to `visibility: public`, compiles statement and editorial markdown (expanding `@include`, `@code_include`, and spoiler macros), and writes JSON data files and image assets to `site/public/data/`.

2. **`npm run build`** — Vite builds the React app, bundling the generated data into `site/dist/`.

## Deploying to GitHub Pages

A GitHub Actions workflow is included at `.github/templates/deploy-site.yml`. It runs automatically on pushes to `main`.

To enable it:

1. Add a similar config to your problem repository in `.github/workflows`
2. Go to your repo's **Settings > Pages**
3. Set **Source** to **GitHub Actions**
4. Push to `main` — the site will deploy automatically

The workflow sets `VITE_BASE_URL` to `/<repo-name>/` so asset paths work correctly under the GitHub Pages subdirectory.

### Custom domain

If using a custom domain, set `VITE_BASE_URL=/` in the workflow or remove the env var entirely.

## Output structure

```
site/dist/
├── index.html              # SPA entry point
├── 404.html                # GitHub Pages SPA routing fix
├── assets/                 # Bundled JS/CSS/fonts
└── data/
    ├── index.json           # Array of problem summaries
    └── <slug>/
        ├── data.json        # Full problem data (statement + editorial)
        └── files/           # Copied images referenced by the problem
```

## Customization

### Base URL

Set `VITE_BASE_URL` to control the base path:

```bash
# Deploying to username.github.io/my-repo/
VITE_BASE_URL=/my-repo/ npm run build

# Deploying to a root domain
VITE_BASE_URL=/ npm run build
```

### Problems directory

The build script defaults to `examples/` but accepts any path:

```bash
uv run python site/build.py --problems-root ~/my-problems
```
