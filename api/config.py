from pathlib import Path
from functools import lru_cache
import os

_PROJECT_ROOT = Path(__file__).parent.parent


def _load_yaml_config() -> dict:
    config_file = _PROJECT_ROOT / "config.yaml"
    if not config_file.exists():
        return {}
    import yaml
    return yaml.safe_load(config_file.read_text()) or {}


class Settings:
    def __init__(self):
        cfg = _load_yaml_config()

        # Root directory where problem directories live.
        # Override via PROBLEMS_ROOT env var or config.yaml problems_root key.
        self.problems_root: Path = Path(
            os.environ.get("PROBLEMS_ROOT", cfg.get("problems_root", _PROJECT_ROOT / "examples"))
        )

        # Root directory for async job cache files ({slug}/{type}/{timestamp_ms}.yaml).
        # Override via CACHE_ROOT env var or config.yaml cache_root key.
        self.cache_root: Path = Path(
            os.environ.get("CACHE_ROOT", cfg.get("cache_root", _PROJECT_ROOT / ".cache"))
        )

        # Port the uvicorn server listens on.
        # Override via PORT env var or config.yaml port key.
        self.port: int = int(os.environ.get("PORT", cfg.get("port", 8001)))

        # C++ compile flags for solution execution.
        # Override via config.yaml cpp_flags key (list of strings).
        _default_cpp_flags = [
            "-std=c++17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Wshadow",
            "-DONLINE_JUDGE",
        ]
        raw = cfg.get("cpp_flags")
        if raw is not None:
            if isinstance(raw, list):
                self.cpp_flags: list[str] = [str(f) for f in raw]
            else:
                self.cpp_flags = str(raw).split()
        else:
            self.cpp_flags = _default_cpp_flags


@lru_cache
def get_settings() -> Settings:
    return Settings()
