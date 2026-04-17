import platform
import subprocess
import os
from checkers.base_checker import BaseChecker, CheckResult


class SoftwareChecker(BaseChecker):

    def run(self) -> CheckResult:
        self.logger.info("SoftwareChecker started")
        system = platform.system()
        try:
            if system == "Windows":
                installed = self._get_windows_software()
            elif system == "Linux":
                installed = self._get_linux_software()
            elif system == "Darwin":
                installed = self._get_macos_software()
            else:
                installed = []
                self.logger.warning(f"Unsupported platform: {system}")
        except Exception as e:
            self.logger.error(f"SoftwareChecker error: {e}")
            installed = []

        blacklist = [s.lower() for s in self.config.get("blacklist_software", [])]
        violations = []
        for sw in installed:
            name_lower = sw.get("name", "").lower()
            for bl in blacklist:
                if bl in name_lower:
                    violations.append(sw)
                    break

        passed = len(violations) == 0
        summary = (
            f"已安装软件总数: {len(installed)}\n"
            f"违规软件数量: {len(violations)}\n"
        )
        if violations:
            summary += "\n违规软件列表:\n"
            for v in violations:
                summary += f"  - {v.get('name', 'N/A')} (版本: {v.get('version', 'N/A')}) 路径: {v.get('path', 'N/A')}\n"
        else:
            summary += "\n未发现违规软件。"

        recommendations = []
        if violations:
            recommendations.append("请卸载上述违规软件，禁止在内网终端使用未授权的远控、代理、网盘及破解工具。")

        self.logger.info(f"SoftwareChecker done: {len(violations)} violations")
        return CheckResult(
            module="软件清单检查",
            passed=passed,
            violations=violations,
            summary=summary,
            recommendations=recommendations,
        )

    def _get_windows_software(self) -> list:
        import winreg
        software = []
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for hive, path in keys:
            try:
                key = winreg.OpenKey(hive, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("KB"):
                            continue
                        subkey = winreg.OpenKey(key, subkey_name)
                        name = self._reg_value(subkey, "DisplayName")
                        if not name:
                            continue
                        software.append({
                            "name": name,
                            "version": self._reg_value(subkey, "DisplayVersion") or "N/A",
                            "path": self._reg_value(subkey, "InstallLocation") or "N/A",
                            "publisher": self._reg_value(subkey, "Publisher") or "N/A",
                        })
                    except Exception:
                        continue
            except Exception:
                continue
        return software

    def _reg_value(self, key, name: str) -> str:
        try:
            import winreg
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
        except Exception:
            return ""

    def _get_linux_software(self) -> list:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Package}\t${Version}\n"],
            capture_output=True, text=True, timeout=10
        )
        software = []
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                software.append({"name": parts[0], "version": parts[1], "path": "N/A", "publisher": "N/A"})
        return software

    def _get_macos_software(self) -> list:
        software = []
        apps_dir = "/Applications"
        try:
            for entry in os.scandir(apps_dir):
                if entry.name.endswith(".app"):
                    software.append({
                        "name": entry.name.replace(".app", ""),
                        "version": "N/A",
                        "path": entry.path,
                        "publisher": "N/A",
                    })
        except Exception as e:
            self.logger.warning(f"macOS app scan error: {e}")

        try:
            result = subprocess.run(
                ["brew", "list", "--versions"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if parts:
                    software.append({
                        "name": parts[0],
                        "version": parts[1] if len(parts) > 1 else "N/A",
                        "path": "N/A",
                        "publisher": "Homebrew",
                    })
        except Exception:
            pass

        return software
