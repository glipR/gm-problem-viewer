from pathlib import Path
from functools import lru_cache
import os

_PROJECT_ROOT = Path(__file__).parent.parent


class Settings:
    # Root directory where problem directories live.
    # Override via PROBLEMS_ROOT env var.
    problems_root: Path = Path(
        os.environ.get("PROBLEMS_ROOT", _PROJECT_ROOT / "examples")
    )

    # Root directory for async job cache files ({slug}/{type}/{timestamp_ms}.yaml).
    # Override via CACHE_ROOT env var.
    cache_root: Path = Path(
        os.environ.get("CACHE_ROOT", _PROJECT_ROOT / ".cache")
    )

    # Port the uvicorn server listens on.
    # Override via PORT env var.
    port: int = int(os.environ.get("PORT", 8001))


@lru_cache
def get_settings() -> Settings:
    return Settings()
