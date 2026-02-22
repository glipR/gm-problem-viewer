"""Collection layer — parse problem directories into Pydantic models.

Public API
----------
get_problem(problems_dir, problem_slug)  -> Problem
get_test_sets(problem_path)              -> list[TestSet]
get_statement(problem_path)              -> str | None
get_solutions(problem_path)              -> list[Solution]
get_validators(problem_path)             -> ValidatorSet

Utilities
---------
parse_frontmatter(path)  -> dict   (YAML frontmatter from .py / .cpp)
infer_language(path)     -> str | None
"""

from api.collection.frontmatter import infer_language, parse_frontmatter
from api.collection.problems import get_problem, list_problems
from api.collection.solutions import get_solutions
from api.collection.statement import get_statement
from api.collection.test_sets import get_test_sets
from api.collection.validators import get_validators

__all__ = [
    "list_problems",
    "get_problem",
    "get_test_sets",
    "get_statement",
    "get_solutions",
    "get_validators",
    "parse_frontmatter",
    "infer_language",
]
