import sys
import os
import tempfile
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checkers.sensitive_checker import SensitiveChecker


def _make_checker(extra_dirs=None):
    with patch("utils.config_loader.load"):
        checker = SensitiveChecker(extra_dirs=extra_dirs or [])
        checker.config = MagicMock()
        checker.config.get = lambda k, d=None: {
            "sensitive_keywords": ["绝密", "机密"],
            "scan_extensions": [".txt"],
            "max_file_size_mb": 50,
            "default_scan_dirs": [],
        }.get(k, d)
        return checker


def test_id_number_detection():
    checker = _make_checker()
    with tempfile.TemporaryDirectory() as tmpdir:
        f = os.path.join(tmpdir, "test.txt")
        with open(f, "w") as fp:
            fp.write("身份证号: 110101199001011234")
        checker.extra_dirs = [tmpdir]
        with patch.object(checker, "_get_scan_dirs", return_value=[tmpdir]):
            result = checker.run()
    assert not result.passed
    assert any("身份证号" in str(v["hits"]) for v in result.violations)


def test_keyword_detection():
    checker = _make_checker()
    with tempfile.TemporaryDirectory() as tmpdir:
        f = os.path.join(tmpdir, "secret.txt")
        with open(f, "w") as fp:
            fp.write("这是一份绝密文件，请勿外传。")
        with patch.object(checker, "_get_scan_dirs", return_value=[tmpdir]):
            result = checker.run()
    assert not result.passed


def test_clean_file():
    checker = _make_checker()
    with tempfile.TemporaryDirectory() as tmpdir:
        f = os.path.join(tmpdir, "normal.txt")
        with open(f, "w") as fp:
            fp.write("这只是普通的会议纪要，没有敏感内容。")
        with patch.object(checker, "_get_scan_dirs", return_value=[tmpdir]):
            result = checker.run()
    assert result.passed
