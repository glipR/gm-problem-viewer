"""
Static site data generator.

Reads problems from PROBLEMS_ROOT, filters to visibility: public,
compiles statement + editorial markdown, and writes JSON + assets
into site/public/data/ for the Vite static site to consume.

Usage:
    uv run python site/build.py [--problems-root PATH]
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from pathlib import Path

# Add project root to path so we can import api modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.collection.problems import list_problems
from api.collection.statement import compile_statement
from api.collection.editorial import compile_editorial


def find_image_refs(problem_path: Path) -> list[Path]:
    """Find image files referenced by statement/editorial (any common image format)."""
    images = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp"):
        images.extend(problem_path.rglob(ext))
    return images


def build_problem_data(slug: str, problem_path: Path, config: dict) -> dict | None:
    """Build JSON data for a single problem. Returns None if not public."""
    if config.get("visibility", "private") != "public":
        return None

    statement = compile_statement(problem_path)
    editorial = compile_editorial(problem_path)

    return {
        "slug": slug,
        "name": config["name"],
        "type": config.get("type", "standard"),
        "tags": config.get("tags", []),
        "difficulty": config.get("difficulty"),
        "quality": config.get("quality"),
        "author": config.get("author", ""),
        "limits": config.get("limits", {"time": 1, "memory": 262144}),
        "contests": config.get("contests"),
        "external_judge_url": config.get("external_judge_url"),
        "statement": statement,
        "editorial": editorial,
    }


def main():
    parser = argparse.ArgumentParser(description="Build static site data")
    parser.add_argument(
        "--problems-root",
        type=Path,
        default=PROJECT_ROOT / "examples",
        help="Path to problems directory (default: examples/)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "public" / "data",
        help="Output directory for generated data (default: site/public/data/)",
    )
    args = parser.parse_args()

    problems_root: Path = args.problems_root.resolve()
    out_dir: Path = args.out.resolve()

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    problems = list_problems(problems_root)
    index = []

    for problem in problems:
        slug = problem.slug
        problem_path = problems_root / slug
        config = problem.config.model_dump()

        data = build_problem_data(slug, problem_path, config)
        if data is None:
            continue

        # Write per-problem JSON
        problem_dir = out_dir / slug
        problem_dir.mkdir(parents=True, exist_ok=True)
        (problem_dir / "data.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # Copy images
        images = find_image_refs(problem_path)
        for img in images:
            rel = img.relative_to(problem_path)
            dest = problem_dir / "files" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img, dest)

        index.append({
            "slug": slug,
            "name": data["name"],
            "type": data["type"],
            "tags": data["tags"],
            "difficulty": data["difficulty"],
            "quality": data["quality"],
            "author": data["author"],
            "contests": data["contests"],
            "external_judge_url": data["external_judge_url"],
            "has_editorial": data["editorial"] is not None,
        })

    # Write index
    (out_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Built {len(index)} public problem(s) into {out_dir}")


if __name__ == "__main__":
    main()
