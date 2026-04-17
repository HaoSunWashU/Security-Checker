import platform
import subprocess
import re
from checkers.base_checker import BaseChecker, CheckResult


class AccountChecker(BaseChecker):

    def run(self) -> CheckResult:
        self.logger.info("AccountChecker started")
        system = platform.system()
        try:
            if system == "Windows":
                accounts = self._get_windows_accounts()
            elif system in ("Linux", "Darwin"):
                accounts = self._get_unix_accounts()
            else:
                accounts = []
        except Exception as e:
            self.logger.error("AccountChecker failed to retrieve accounts", exc_info=True)
            accounts = []

        weak_passwords = [p.lower() for p in self.config.get("weak_passwords", [])]
        violations = []

        for acc in accounts:
            issues = []
            name = acc.get("name", "").lower()

            if acc.get("empty_password"):
                issues.append("空密码")
            if acc.get("password_never_expires"):
                issues.append("密码永不过期")
            if name in ("guest", "来宾", "anonymous"):
                issues.append("匿名/来宾账号")
            if name in weak_passwords:
                issues.append("账号名为弱口令")
            if acc.get("disabled"):
                issues.append("账号已禁用但存在")

            if issues:
                violations.append({
                    "name": acc.get("name"),
                    "issues": issues,
                    "type": acc.get("type", "N/A"),
                })

        passed = len(violations) == 0
        summary = f"检测账号总数: {len(accounts)}\n风险账号数量: {len(violations)}\n"
        if violations:
            summary += "\n风险账号详情:\n"
            for v in violations:
                summary += f"  - {v['name']} [{v['type']}]: {', '.join(v['issues'])}\n"
        else:
            summary += "\n未发现风险账号。"

        recommendations = []
        if any("空密码" in v["issues"] for v in violations):
            recommendations.append("立即为空密码账号设置强密码。")
        if any("密码永不过期" in v["issues"] for v in violations):
            recommendations.append("启用密码定期过期策略，建议周期不超过90天。")
        if any("匿名/来宾账号" in v["issues"] for v in violations):
            recommendations.append("禁用或删除来宾/匿名账号。")

        self.logger.info(f"AccountChecker done: {len(accounts)} accounts checked, {len(violations)} at risk")
        for v in violations:
            self.logger.info(f"  [RISK] {v['name']} ({v['type']}): {', '.join(v['issues'])}")
        return CheckResult(
            module="账号密码检查",
            passed=passed,
            violations=violations,
            summary=summary,
            recommendations=recommendations,
        )

    def _get_windows_accounts(self) -> list:
        accounts = []
        try:
            result = subprocess.run(
                ["net", "user"], capture_output=True, text=True, timeout=10, encoding="gbk", errors="replace"
            )
            names = re.findall(r"^(\S+)", result.stdout, re.MULTILINE)
            names = [n for n in names if n not in ("用户帐户", "User", "----", "命令成功完成。", "The")]

            for name in names:
                detail = subprocess.run(
                    ["net", "user", name],
                    capture_output=True, text=True, timeout=10, encoding="gbk", errors="replace"
                )
                out = detail.stdout

                empty_pw = bool(re.search(r"密码.*?不需要|Password not required.*?Yes", out, re.IGNORECASE))
                pw_never = bool(re.search(r"密码永不过期.*?是|Password expires.*?Never", out, re.IGNORECASE))
                disabled = bool(re.search(r"帐户.*?禁用.*?是|Account active.*?No", out, re.IGNORECASE))

                acc_type = "管理员" if "Administrators" in out or "管理员" in out else "普通用户"
                accounts.append({
                    "name": name,
                    "type": acc_type,
                    "empty_password": empty_pw,
                    "password_never_expires": pw_never,
                    "disabled": disabled,
                })
        except Exception as e:
            self.logger.error("Windows account enumeration failed", exc_info=True)
        return accounts

    def _get_unix_accounts(self) -> list:
        accounts = []
        try:
            with open("/etc/passwd", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) < 7:
                        continue
                    name, pw_field, uid, gid, _, _, shell = parts[:7]
                    if int(uid) < 1000 and name not in ("root",):
                        continue
                    if shell in ("/sbin/nologin", "/usr/sbin/nologin", "/bin/false"):
                        continue
                    accounts.append({
                        "name": name,
                        "type": "root" if uid == "0" else "普通用户",
                        "empty_password": pw_field == "",
                        "password_never_expires": False,
                        "disabled": False,
                    })
        except Exception as e:
            self.logger.warning("Could not read /etc/passwd", exc_info=True)

        try:
            with open("/etc/shadow", "r") as f:
                shadow = {l.split(":")[0]: l.split(":")[1] for l in f if ":" in l}
            for acc in accounts:
                pw = shadow.get(acc["name"], "!")
                if pw in ("", "!!", "*"):
                    acc["empty_password"] = True
                if pw.startswith("!") or pw.startswith("*"):
                    acc["disabled"] = True
        except PermissionError:
            self.logger.warning("Cannot read /etc/shadow (not root) — skipping shadow check")
        except Exception as e:
            self.logger.warning("Shadow file read error", exc_info=True)

        return accounts
