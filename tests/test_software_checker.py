import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checkers.software_checker import SoftwareChecker


def _make_checker():
    with patch("utils.config_loader.load"):
        checker = SoftwareChecker()
        checker.config = MagicMock()
        checker.config.get = lambda k, d=None: {
            "blacklist_software": ["TeamViewer", "AnyDesk"],
        }.get(k, d)
        return checker


def test_no_violations():
    checker = _make_checker()
    installed = [{"name": "Microsoft Office", "version": "2021", "path": "C:\\Office", "publisher": "Microsoft"}]
    with patch.object(checker, "_get_macos_software", return_value=installed), \
         patch("platform.system", return_value="Darwin"):
        result = checker.run()
    assert result.passed
    assert result.violation_count() == 0


def test_violation_detected():
    checker = _make_checker()
    installed = [
        {"name": "TeamViewer", "version": "15.0", "path": "C:\\TV", "publisher": "TeamViewer GmbH"},
        {"name": "Word", "version": "2021", "path": "C:\\Word", "publisher": "Microsoft"},
    ]
    with patch.object(checker, "_get_macos_software", return_value=installed), \
         patch("platform.system", return_value="Darwin"):
        result = checker.run()
    assert not result.passed
    assert result.violation_count() == 1
    assert result.violations[0]["name"] == "TeamViewer"
