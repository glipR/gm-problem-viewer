"""Collection layer — parse problem directories into Pydantic models.

Public API
----------
TODO

Utilities
---------
parse_frontmatter(path)  -> dict   (YAML frontmatter from .py / .cpp)
infer_language(path)     -> str | None
"""

from api.collection.frontmatter import *
from api.collection.problems import *
from api.collection.solutions import *
from api.collection.statement import *
from api.collection.test_sets import *
from api.collection.validators import *
