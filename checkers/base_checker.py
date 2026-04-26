from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class CheckResult:
    module: str
    passed: bool
    violations: List[dict]
    summary: str
    recommendations: List[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)   # arbitrary per-module payload

    def violation_count(self) -> int:
        return len(self.violations)


class BaseChecker(ABC):
    def __init__(self):
        from utils.logger import get_logger
        from utils import config_loader
        self.logger = get_logger(self.__class__.__name__)
        self.config = config_loader

    @abstractmethod
    def run(self) -> CheckResult:
        """Execute the check and return a CheckResult."""
        ...
