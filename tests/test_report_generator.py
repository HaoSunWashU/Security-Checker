import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checkers.base_checker import CheckResult
from utils import report_generator

SYSTEM_INFO = {
    "hostname": "TEST-PC",
    "os": "Windows 10",
    "mac": "AA:BB:CC:DD:EE:FF",
    "ip": "192.168.1.1",
    "check_time": "2026-04-16 10:00:00",
}

RESULTS = [
    CheckResult(
        module="软件清单检查",
        passed=False,
        violations=[{"name": "TeamViewer", "version": "15.0", "path": "C:\\TeamViewer"}],
        summary="已安装软件总数: 50\n违规软件数量: 1\n  - TeamViewer",
        recommendations=["请卸载违规软件。"],
    ),
    CheckResult(
        module="账号密码检查",
        passed=True,
        violations=[],
        summary="检测账号总数: 3\n风险账号数量: 0\n未发现风险账号。",
    ),
]


def test_generate_txt():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        path = f.name
    try:
        report_generator.generate(RESULTS, "txt", path, SYSTEM_INFO)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "TEST-PC" in content
        assert "软件清单检查" in content
        assert "TeamViewer" in content
        assert "账号密码检查" in content
        enc_path = path.replace(".txt", "_encrypted.sec")
        assert os.path.exists(enc_path)
    finally:
        for p in (path, path.replace(".txt", "_encrypted.sec")):
            if os.path.exists(p):
                os.unlink(p)


def test_generate_html():
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        path = f.name
    try:
        report_generator.generate(RESULTS, "html", path, SYSTEM_INFO)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "TeamViewer" in content
        assert "TEST-PC" in content
    finally:
        for p in (path, path.replace(".html", "_encrypted.sec")):
            if os.path.exists(p):
                os.unlink(p)
