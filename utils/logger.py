import logging
import os
from logging.handlers import RotatingFileHandler

_logger = None


def get_logger(name: str = "security_checker") -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "check_error.log")

    handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(handler)
    _logger.addHandler(console)
    _logger.propagate = False

    return _logger
