from enum import Enum
from dataclasses import dataclass
from typing import Optional


class CheckCategory(str, Enum):
    STATEMENT = "statement"
    SOLUTION = "solution"
    VALIDATOR = "validator"
    TEST = "test"


@dataclass
class CheckResult:
    category: CheckCategory
    issue: Optional[str]  # None = passed
