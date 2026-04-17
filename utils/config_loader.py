import json
import logging
import os
from typing import Any

_CONFIG: dict = {}
_logger = logging.getLogger("config_loader")

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
    _logger.info(f"Loading config from: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        _logger.error(f"Config file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        _logger.error(f"Config file JSON parse error: {e}")
        raise

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        _logger.error(f"config.json is missing required keys: {missing}")
        raise ValueError(f"config.json is missing required keys: {missing}")

    _CONFIG = data
    _logger.info(f"Config loaded successfully ({len(_CONFIG)} keys)")


def get(key: str, default: Any = None) -> Any:
    if not _CONFIG:
        load()
    return _CONFIG.get(key, default)


def all_config() -> dict:
    if not _CONFIG:
        load()
    return dict(_CONFIG)
