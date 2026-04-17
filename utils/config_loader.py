import json
import os
from typing import Any

_CONFIG: dict = {}

REQUIRED_KEYS = [
    "report_password",
    "blacklist_software",
    "weak_passwords",
    "sensitive_keywords",
    "scan_extensions",
    "dangerous_ports",
    "max_file_size_mb",
]

_DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load(path: str = _DEFAULT_CONFIG_PATH) -> None:
    global _CONFIG
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ValueError(f"config.json is missing required keys: {missing}")

    _CONFIG = data


def get(key: str, default: Any = None) -> Any:
    if not _CONFIG:
        load()
    return _CONFIG.get(key, default)


def all_config() -> dict:
    if not _CONFIG:
        load()
    return dict(_CONFIG)
