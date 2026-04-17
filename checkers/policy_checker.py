import platform
import subprocess
import re
from checkers.base_checker import BaseChecker, CheckResult


class PolicyChecker(BaseChecker):

    def run(self) -> CheckResult:
        self.logger.info("PolicyChecker started")
        system = platform.system()
        self._netstat_cache = self._run_netstat()

        checks = [
            self._check_firewall,
            self._check_auto_update,
            self._check_dangerous_ports,
            self._check_usb_storage,
            self._check_screen_lock,
            self._check_remote_desktop,
            self._check_audit_logging,
            self._check_antivirus_running,
            self._check_antivirus_updated,
        ]

        results = []
        for check in checks:
            try:
                label, compliant, detail, recommendation = check(system)
            except Exception as e:
                self.logger.error(f"Policy check error in {check.__name__}: {e}")
                label = check.__name__
                compliant = False
                detail = f"检查失败: {e}"
                recommendation = "请手动核实该策略项。"
            results.append({
                "label": label,
                "compliant": compliant,
                "detail": detail,
                "recommendation": recommendation,
            })

        violations = [r for r in results if not r["compliant"]]
        passed = len(violations) == 0

        summary = "安全策略检查结果:\n\n"
        for r in results:
            icon = "✓ 合规" if r["compliant"] else "✗ 不合规"
            summary += f"  [{icon}] {r['label']}: {r['detail']}\n"

        recommendations = [r["recommendation"] for r in violations if r["recommendation"]]

        self.logger.info(f"PolicyChecker done: {len(violations)} non-compliant items")
        return CheckResult(
            module="安全策略检查",
            passed=passed,
            violations=violations,
            summary=summary,
            recommendations=recommendations,
        )

    def _run_netstat(self) -> str:
        try:
            result = subprocess.run(
                ["netstat", "-an"],
                capture_output=True, text=True, timeout=10, errors="replace"
            )
            return result.stdout
        except Exception as e:
            self.logger.warning(f"netstat failed: {e}")
            return ""

    def _run(self, cmd: list, timeout: int = 10) -> str:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="replace")
            return r.stdout + r.stderr
        except Exception as e:
            self.logger.warning(f"Command {cmd} failed: {e}")
            return ""

    def _check_firewall(self, system: str):
        label = "防火墙"
        if system == "Windows":
            out = self._run(["netsh", "advfirewall", "show", "allprofiles", "state"])
            compliant = "ON" in out.upper()
            detail = "已开启" if compliant else "未开启或部分配置文件未启用"
        elif system == "Linux":
            out = self._run(["ufw", "status"])
            compliant = "active" in out.lower()
            detail = "已开启" if compliant else "未开启 (ufw inactive)"
        else:
            out = self._run(["defaults", "read", "/Library/Preferences/com.apple.alf", "globalstate"])
            compliant = out.strip() in ("1", "2")
            detail = "已开启" if compliant else "未开启"
        return label, compliant, detail, "请立即开启防火墙并配置合适的出入站规则。" if not compliant else ""

    def _check_auto_update(self, system: str):
        label = "自动更新"
        if system == "Windows":
            out = self._run(["reg", "query",
                             r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update",
                             "/v", "AUOptions"])
            compliant = "4" in out or "3" in out
            detail = "已启用" if compliant else "未启用或配置为手动"
        elif system == "Linux":
            out = self._run(["systemctl", "is-enabled", "unattended-upgrades"])
            compliant = "enabled" in out.lower()
            detail = "已启用" if compliant else "未启用 unattended-upgrades"
        else:
            out = self._run(["softwareupdate", "--schedule"])
            compliant = "on" in out.lower()
            detail = "已启用" if compliant else "未启用自动更新"
        return label, compliant, detail, "建议开启系统自动更新，确保安全补丁及时安装。" if not compliant else ""

    def _check_dangerous_ports(self, system: str):
        label = "危险端口"
        dangerous = self.config.get("dangerous_ports", [])
        open_ports = []
        for port in dangerous:
            if re.search(rf"[:\.]({port})\s+(LISTEN|ESTABLISHED)", self._netstat_cache):
                open_ports.append(port)
        compliant = len(open_ports) == 0
        detail = "无危险端口监听" if compliant else f"开放危险端口: {open_ports}"
        return label, compliant, detail, f"请关闭或防火墙封堵以下端口: {open_ports}" if not compliant else ""

    def _check_usb_storage(self, system: str):
        label = "USB存储"
        if system == "Windows":
            out = self._run(["reg", "query",
                             r"HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR",
                             "/v", "Start"])
            compliant = "0x4" in out or "4" in out
            detail = "已禁用" if compliant else "未禁用 (USBSTOR Start != 4)"
        elif system == "Linux":
            out = self._run(["cat", "/etc/modprobe.d/blacklist.conf"])
            compliant = "usb-storage" in out.lower()
            detail = "已在blacklist中禁用" if compliant else "未在modprobe blacklist中禁用"
        else:
            detail = "macOS不适用此项检查"
            compliant = True
        return label, compliant, detail, "建议通过注册表或udev规则禁用USB存储设备。" if not compliant else ""

    def _check_screen_lock(self, system: str):
        label = "屏幕锁屏"
        if system == "Windows":
            out = self._run(["reg", "query",
                             r"HKCU\Control Panel\Desktop",
                             "/v", "ScreenSaveTimeOut"])
            match = re.search(r"0x(\w+)|(\d+)", out)
            if match:
                val = int(match.group(1) or match.group(2), 16 if match.group(1) else 10)
                compliant = 0 < val <= 600
                detail = f"锁屏时间: {val}秒" if compliant else f"锁屏时间过长或未设置: {val}秒"
            else:
                compliant = False
                detail = "未检测到锁屏配置"
        elif system == "Linux":
            out = self._run(["gsettings", "get", "org.gnome.desktop.session", "idle-delay"])
            match = re.search(r"uint32 (\d+)", out)
            val = int(match.group(1)) if match else 0
            compliant = 0 < val <= 600
            detail = f"空闲延迟: {val}秒" if compliant else f"未设置或超过600秒: {val}秒"
        else:
            out = self._run(["defaults", "-currentHost", "read", "com.apple.screensaver", "idleTime"])
            val = int(out.strip()) if out.strip().isdigit() else 0
            compliant = 0 < val <= 600
            detail = f"锁屏时间: {val}秒" if compliant else f"未设置或超过600秒: {val}秒"
        return label, compliant, detail, "请将屏幕锁屏时间设置为不超过10分钟（600秒）。" if not compliant else ""

    def _check_remote_desktop(self, system: str):
        label = "远程桌面/SSH"
        if system == "Windows":
            out = self._run(["reg", "query",
                             r"HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server",
                             "/v", "fDenyTSConnections"])
            compliant = "0x1" in out or " 1" in out
            detail = "已关闭" if compliant else "远程桌面(RDP)处于开启状态"
        elif system == "Linux":
            out = self._run(["systemctl", "is-active", "ssh"])
            compliant = "active" not in out.lower()
            detail = "SSH服务已关闭" if compliant else "SSH服务正在运行"
        else:
            out = self._run(["systemsetup", "-getremotelogin"])
            compliant = "off" in out.lower()
            detail = "远程登录已关闭" if compliant else "远程登录(SSH)处于开启状态"
        return label, compliant, detail, "如非必要，请关闭远程桌面/SSH服务，减少攻击面。" if not compliant else ""

    def _check_audit_logging(self, system: str):
        label = "审计日志"
        if system == "Windows":
            out = self._run(["wevtutil", "gl", "Security"])
            compliant = "enabled: true" in out.lower()
            detail = "安全审计日志已启用" if compliant else "安全审计日志未启用"
        elif system == "Linux":
            out = self._run(["systemctl", "is-active", "rsyslog"])
            compliant = "active" in out.lower()
            detail = "rsyslog运行中" if compliant else "rsyslog未运行"
        else:
            out = self._run(["log", "show", "--last", "1m"])
            compliant = len(out) > 0
            detail = "系统日志可读" if compliant else "系统日志不可访问"
        return label, compliant, detail, "请开启系统审计日志功能，确保安全事件可追溯。" if not compliant else ""

    def _check_antivirus_running(self, system: str):
        label = "安全软件运行"
        if system == "Windows":
            out = self._run(["wmic", "/namespace:\\\\root\\SecurityCenter2",
                             "path", "AntiVirusProduct", "get", "displayName,productState"])
            compliant = bool(re.search(r"\w+", out.replace("displayName", "").replace("productState", "").strip()))
            detail = f"检测到安全软件: {out[:80].strip()}" if compliant else "未检测到安全软件"
        elif system == "Linux":
            out = self._run(["systemctl", "is-active", "clamav-daemon"])
            compliant = "active" in out.lower()
            detail = "ClamAV运行中" if compliant else "ClamAV未运行"
        else:
            detail = "macOS内置XProtect/Gatekeeper，视为合规"
            compliant = True
        return label, compliant, detail, "请安装并启用终端安全防护软件。" if not compliant else ""

    def _check_antivirus_updated(self, system: str):
        label = "安全软件病毒库"
        detail = "需人工核实病毒库更新状态（依赖厂商更新策略）"
        compliant = True
        return label, compliant, detail, ""
