from pathlib import Path
from functools import lru_cache
import os


class Settings:
    # Root directory where problem directories live.
    # Override via PROBLEMS_ROOT env var.
    problems_root: Path = Path(
        os.environ.get("PROBLEMS_ROOT", Path(__file__).parent.parent / "examples")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
