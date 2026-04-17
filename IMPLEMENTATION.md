# Security Checker — Implementation Plan
# 终端安全检查工具 — 实施方案

---

## Overview / 项目概述

**English:**
Security Checker is a cross-platform (Windows / UOS Linux / macOS) lightweight desktop security compliance tool targeting government agencies and enterprise intranet endpoints. It scans across four dimensions — software inventory, account security, system policies, and sensitive file detection — then generates encrypted compliance reports in multiple formats.

**中文：**
终端安全检查工具是一款跨平台（Windows / 统信UOS / macOS）轻量化桌面安全合规检查软件，面向党政机关和企事业单位内网终端。工具覆盖软件清单、账号密码、安全策略、敏感信息四大检查维度，并支持生成多格式加密合规报告。

---

## Improvements Over Original Spec / 相较原方案的改进

| Area / 方向 | Original / 原方案 | Improvement / 改进 |
|---|---|---|
| Config / 配置管理 | Hardcoded constants / 常量硬编码 | `config.json` loaded at runtime — passwords, blacklists, keywords configurable without recompiling / 运行时加载，无需重新打包即可调整配置 |
| Result model / 结果模型 | Ad-hoc strings per checker / 各模块自行定义字符串 | Shared `CheckResult` dataclass — uniform structure across all 4 checkers / 统一数据结构，四个检查器共用 |
| Checker architecture / 检查器架构 | 4 independent classes / 四个独立类 | Common `BaseChecker` abstract class — enforces `run()` contract, enables future plug-in checkers / 抽象基类统一接口，支持未来插件式扩展 |
| CLI mode / 命令行模式 | GUI only / 仅图形界面 | `--headless` flag for scriptable, GUI-free execution / 支持无界面批量执行，适合自动化部署场景 |
| Logging / 日志 | Single flat log file / 单一平铺日志 | `RotatingFileHandler` — capped at 5MB, 3 backups / 滚动日志，单文件上限5MB，保留3个备份 |
| Password security / 密码安全 | Hardcoded `Sec@2026` in source / 密码硬编码在源码中 | Loaded from `config.json`; first-run wizard prompts for custom password / 从配置文件加载，首次运行引导用户设置 |
| Platform support / 平台支持 | Windows + UOS only / 仅Windows和统信UOS | Added macOS branch for dev/testing / 新增macOS分支，便于开发和测试 |
| Tests / 测试 | None specified / 未设计测试 | `tests/` with `pytest` unit tests for all checkers and utils / 为所有模块编写pytest单元测试 |
| Report caching / 报告缓存 | None / 无 | Last scan cached to `cache/last_scan.json` — re-export without re-scanning / 缓存上次扫描结果，支持重复导出无需重新扫描 |

---

## Project Structure / 项目结构

```
Security-Checker/
├── main.py                      # Entry point / 程序入口，支持 --headless 参数
├── config.json                  # Runtime config / 运行时配置（密码、黑名单、关键词、扫描目录）
├── requirements.txt             # Python dependencies / Python依赖列表
├── README.md                    # User guide / 用户使用说明
├── IMPLEMENTATION.md            # This file / 本文件（实施方案）
│
├── ui/                          # GUI layer / 界面层
│   ├── __init__.py
│   ├── main_window.py           # MainWindow(QMainWindow) — toolbar + tab layout / 主窗口（工具栏 + 标签页）
│   ├── tabs/
│   │   ├── software_tab.py      # Tab 1: software scan results / 标签页1：软件清单
│   │   ├── account_tab.py       # Tab 2: account/password results / 标签页2：账号密码
│   │   ├── policy_tab.py        # Tab 3: security policy results / 标签页3：安全策略
│   │   └── sensitive_tab.py     # Tab 4: sensitive info + directory picker / 标签页4：敏感信息（含目录选择）
│   └── dialogs/
│       ├── export_dialog.py     # Format picker (HTML/Excel/PDF/TXT) / 导出格式选择对话框
│       └── view_report_dialog.py # Password prompt + decrypted preview / 密码输入 + 解密预览
│
├── checkers/                    # Core logic / 核心检查逻辑
│   ├── __init__.py
│   ├── base_checker.py          # Abstract BaseChecker + CheckResult dataclass / 抽象基类 + 统一结果数据类
│   ├── software_checker.py      # SoftwareChecker(BaseChecker) / 软件清单检查器
│   ├── account_checker.py       # AccountChecker(BaseChecker) / 账号密码检查器
│   ├── policy_checker.py        # PolicyChecker(BaseChecker) / 安全策略检查器
│   └── sensitive_checker.py     # SensitiveChecker(BaseChecker) / 敏感信息检查器
│
├── utils/                       # Shared utilities / 公共工具模块
│   ├── __init__.py
│   ├── crypto.py                # AES-256-CFB encrypt/decrypt / 加密解密（AES-256-CFB）
│   ├── report_generator.py      # HTML/Excel/PDF/TXT report generation / 多格式报告生成
│   ├── system_info.py           # hostname, OS, MAC, IP / 系统信息采集
│   ├── config_loader.py         # Loads + validates config.json / 配置文件加载与校验
│   └── logger.py                # RotatingFileHandler setup / 日志滚动配置
│
├── cache/                       # Runtime cache / 运行时缓存（已加入.gitignore）
│   └── last_scan.json           # Last scan results / 上次扫描结果缓存
│
└── tests/                       # Unit tests / 单元测试
    ├── test_crypto.py
    ├── test_report_generator.py
    ├── test_software_checker.py
    ├── test_account_checker.py
    ├── test_policy_checker.py
    └── test_sensitive_checker.py
```

---

## Implementation Phases / 实施阶段

### Phase 1 — Scaffold & Config / 第一阶段：脚手架与配置

**English:**
- `main.py`: argument parsing (`--headless`, `--export=html`), launches GUI or headless runner
- `config.json`: defines `report_password`, `blacklist_software`, `sensitive_keywords`, `default_scan_dirs`, `max_file_size_mb`
- `utils/config_loader.py`: singleton `CONFIG` dict, validates required keys on load
- `utils/logger.py`: `RotatingFileHandler` writing to `check_error.log`, max 5MB × 3 backups
- `utils/system_info.py`: collects hostname, OS version, MAC address, IP once at startup
- `checkers/base_checker.py`: defines `CheckResult` dataclass (`module`, `passed`, `violations`, `summary`, `recommendations`) and abstract `BaseChecker.run() -> CheckResult`
- `requirements.txt`: PyQt5, cryptography, pandas, openpyxl, python-docx, pdfplumber, pytest

**中文：**
- `main.py`：参数解析（`--headless`、`--export=html`），按模式启动图形界面或无头运行器
- `config.json`：定义 `report_password`、`blacklist_software`、`sensitive_keywords`、`default_scan_dirs`、`max_file_size_mb`
- `utils/config_loader.py`：单例 `CONFIG` 字典，加载时校验必填字段
- `utils/logger.py`：`RotatingFileHandler` 写入 `check_error.log`，单文件上限5MB，保留3个备份
- `utils/system_info.py`：启动时一次性采集主机名、操作系统版本、MAC地址、IP地址
- `checkers/base_checker.py`：定义 `CheckResult` 数据类（`module`、`passed`、`violations`、`summary`、`recommendations`）及抽象 `BaseChecker.run() -> CheckResult`
- `requirements.txt`：PyQt5、cryptography、pandas、openpyxl、python-docx、pdfplumber、pytest

---

### Phase 2 — Four Checkers / 第二阶段：四大检查器

**English:**
Each checker inherits `BaseChecker` and dispatches on `platform.system()` → `Windows` / `Linux` / `Darwin`.

**中文：**
每个检查器继承 `BaseChecker`，根据 `platform.system()` 分发到 `Windows` / `Linux` / `Darwin` 分支。

#### SoftwareChecker / 软件清单检查器
- **Windows**: Registry walk `HKLM\SOFTWARE\...\Uninstall` (32-bit + 64-bit nodes)
- **Linux**: `dpkg-query -W -f='${Package} ${Version}\n'`
- **macOS**: `/Applications` directory scan + `brew list`
- Match names against `CONFIG['blacklist_software']` (remote tools, proxies, cloud drives, cracking tools)

- **Windows**：遍历注册表 `HKLM\SOFTWARE\...\Uninstall`（32位+64位节点）
- **Linux**：调用 `dpkg-query`
- **macOS**：扫描 `/Applications` 目录 + `brew list`
- 与 `CONFIG['blacklist_software']` 匹配（远控工具、代理、网盘、破解软件）

#### AccountChecker / 账号密码检查器
- **Windows**: `net user` + `wmic useraccount`
- **Linux/macOS**: `/etc/passwd`, `/etc/shadow` (if root)
- Weak password list from `CONFIG['weak_passwords']` (50 common passwords by default)
- Flags: empty password, never-expires, disabled accounts, guest-like names

- **Windows**：解析 `net user` 和 `wmic useraccount` 输出
- **Linux/macOS**：读取 `/etc/passwd` 和 `/etc/shadow`（需root）
- 弱口令字典来自 `CONFIG['weak_passwords']`（默认内置50个常见密码）
- 检测项：空密码、永不过期、已禁用账号、类Guest账号名

#### PolicyChecker / 安全策略检查器
- 9 policy items per spec; each returns `(label, compliant: bool, detail, recommendation)`
- All `subprocess.run` calls use `timeout=10`; failures logged and treated as non-compliant
- `netstat` called once per scan, result cached in-memory for all port checks

| Policy Item / 策略项 | Windows | Linux/macOS |
|---|---|---|
| Firewall / 防火墙 | `netsh advfirewall` | `ufw status` |
| Auto-update / 自动更新 | Registry query | `systemctl status unattended-upgrades` |
| Dangerous ports / 危险端口 | `netstat -an` | `netstat -an` |
| USB storage / USB存储 | Registry `USBSTOR` | `udev` rules |
| Screen lock / 锁屏时间 | Registry `ScreenSaveTimeOut` | `gsettings idle-delay` |
| Remote desktop / 远程桌面 | Registry `fDenyTSConnections` | `systemctl status ssh` |
| Audit logging / 日志审计 | `wevtutil gl Security` | `systemctl status rsyslog` |
| Antivirus running / 杀软运行 | WMI `AntiVirusProduct` | `systemctl status clamav-daemon` |
| Antivirus updated / 杀软更新 | Vendor API (simplified) | Vendor API (simplified) |

#### SensitiveChecker / 敏感信息检查器
- Scan dirs: `CONFIG['default_scan_dirs']` (Desktop + Documents) + user-added paths via UI
- Extension whitelist: `.txt .doc .docx .xls .xlsx .pdf .csv .md`
- Skip files > `CONFIG['max_file_size_mb']` (default 50MB)
- Text files: read first + last 10KB only
- DOCX: `python-docx`, first 3 paragraphs
- PDF: `pdfplumber`, first 3 pages
- Regex patterns: 18-digit ID number, 11-digit phone, email address + keyword list from config
- `ThreadPoolExecutor(max_workers=4)` across directories

- 扫描目录：`CONFIG['default_scan_dirs']`（桌面+文档）+ UI中用户添加的目录
- 扩展名白名单：`.txt .doc .docx .xls .xlsx .pdf .csv .md`
- 跳过超过 `CONFIG['max_file_size_mb']`（默认50MB）的文件
- 文本文件：仅读取头尾各10KB
- DOCX：`python-docx`，仅读取前3段
- PDF：`pdfplumber`，仅读取前3页
- 正则匹配：18位身份证、11位手机号、邮箱地址 + 配置文件中的密级关键词
- `ThreadPoolExecutor(max_workers=4)` 并行扫描多个目录

---

### Phase 3 — UI / 第三阶段：图形界面

**English:**
- `MainWindow`: toolbar buttons (Start / View Report / Export / Clear), `QProgressBar`, `QTabWidget`
- Each tab uses `QTextBrowser` for HTML rich-text (red highlights for violations)
- `sensitive_tab.py`: embedded `QListWidget` for custom directories + Add/Remove buttons
- Thread model: each checker wrapped in `QRunnable`, results emitted via `pyqtSignal(str, object)` back to main thread — never touch GUI from worker threads
- Progress: +25% per completed checker

**中文：**
- `MainWindow`：工具栏按钮（开始检查 / 查看报告 / 导出报告 / 清空记录）、`QProgressBar`、`QTabWidget`
- 每个标签页使用 `QTextBrowser`（支持HTML富文本，不合规项红色高亮）
- `sensitive_tab.py`：内嵌 `QListWidget` 管理自定义目录，支持添加/移除
- 线程模型：每个检查器封装为 `QRunnable`，通过 `pyqtSignal(str, object)` 将结果传回主线程（严禁在工作线程中直接操作GUI）
- 进度：每完成一个检查器进度条增加25%

---

### Phase 4 — Crypto & Reports / 第四阶段：加密与报告

#### `utils/crypto.py`
- `encrypt(plaintext: str, password: str) -> str`
  - AES-256-CFB, random 16-byte IV
  - Output: `Base64(IV + ciphertext)`
  - Key: `SHA-256(password)` → 32 bytes
- `decrypt(b64_data: str, password: str) -> str`: reverse of above

- `encrypt(plaintext: str, password: str) -> str`：AES-256-CFB，随机16字节IV，输出 `Base64(IV+密文)`，密钥由 `SHA-256(password)` 派生
- `decrypt(b64_data: str, password: str) -> str`：上述过程的逆操作

#### `utils/report_generator.py`
- `generate(results: list[CheckResult], fmt: str, path: str)`
- **HTML**: inline CSS template, red `<span>` for violations, device info header
- **Excel**: `openpyxl`, one worksheet per module
- **PDF**: `QTextDocument` + `QPrinter` (avoids heavy `weasyprint` dependency)
- **TXT**: plain structured text
- After every export: auto-write `report_encrypted.sec` to same directory

- `generate(results: list[CheckResult], fmt: str, path: str)`
- **HTML**：内联CSS模板，不合规项用红色 `<span>` 标注，顶部包含设备信息
- **Excel**：`openpyxl`，每个模块单独一个工作表
- **PDF**：`QTextDocument` + `QPrinter`（避免引入 `weasyprint` 重量级依赖）
- **TXT**：纯文本格式
- 每次导出后自动在同目录生成 `report_encrypted.sec` 加密备份

---

### Phase 5 — Headless Mode & Tests / 第五阶段：无头模式与单元测试

**English:**
- `python main.py --headless --export=html --output=/path/report.html`
  - Runs all 4 checkers sequentially (no GUI), writes report, exits with code 0 (success) or 1 (violations found)
- `tests/`: pytest unit tests with mocked platform calls
  - `test_crypto.py`: encrypt → decrypt round-trip
  - `test_report_generator.py`: fixture `CheckResult` objects → valid HTML/TXT output
  - `test_*_checker.py`: mock `subprocess.run`, registry reads, file system — test on all platforms

**中文：**
- `python main.py --headless --export=html --output=/path/report.html`：无界面运行全部检查，生成报告后退出，退出码0表示合规，1表示发现违规项
- `tests/`：使用Mock模拟平台调用的pytest单元测试
  - `test_crypto.py`：加密→解密往返测试
  - `test_report_generator.py`：用固定 `CheckResult` 对象验证HTML/TXT输出
  - `test_*_checker.py`：Mock `subprocess.run`、注册表读取、文件系统，支持跨平台运行测试

---

## Key Files — Creation Order / 关键文件创建顺序

| Order / 顺序 | File / 文件 | Purpose / 说明 |
|---|---|---|
| 1 | `requirements.txt` | Dependencies / 依赖声明 |
| 2 | `config.json` | Runtime config / 运行时配置 |
| 3 | `utils/logger.py` | Logging setup / 日志初始化 |
| 4 | `utils/config_loader.py` | Config singleton / 配置单例 |
| 5 | `utils/system_info.py` | Device info / 设备信息采集 |
| 6 | `checkers/base_checker.py` | Base class + CheckResult / 基类与结果数据类 |
| 7 | `checkers/software_checker.py` | Software scan / 软件清单检查 |
| 8 | `checkers/account_checker.py` | Account scan / 账号密码检查 |
| 9 | `checkers/policy_checker.py` | Policy scan / 安全策略检查 |
| 10 | `checkers/sensitive_checker.py` | Sensitive file scan / 敏感信息检查 |
| 11 | `utils/crypto.py` | Encryption / 加密工具 |
| 12 | `utils/report_generator.py` | Report output / 报告生成 |
| 13 | `ui/main_window.py` | Main window / 主窗口 |
| 14 | `ui/tabs/*.py` | Tab pages / 各标签页 |
| 15 | `ui/dialogs/*.py` | Dialogs / 对话框 |
| 16 | `main.py` | Entry point / 程序入口 |
| 17 | `tests/*.py` | Unit tests / 单元测试 |

---

## Verification Checklist / 验证清单

| Test / 测试项 | Command / 命令 |
|---|---|
| Run unit tests / 运行单元测试 | `pytest tests/` |
| Headless mode / 无头模式 | `python main.py --headless --export=txt` |
| GUI launch / 图形界面启动 | `python main.py` |
| Encrypt/decrypt round-trip / 加解密往返 | Export report → "View Report" with correct password |
| HTML report / HTML报告 | Open in browser, verify red highlights |
| Package / 打包 | `pyinstaller --onefile --windowed --name SecurityChecker main.py` |

---

## Tech Stack Summary / 技术栈汇总

| Component / 组件 | Choice / 选型 |
|---|---|
| Language / 语言 | Python 3.10+ |
| GUI framework / 界面框架 | PyQt5 |
| Parallelism / 并行处理 | QThreadPool + QRunnable + pyqtSignal |
| Encryption / 加密 | AES-256-CFB (cryptography library) |
| Document parsing / 文档解析 | python-docx, pdfplumber, openpyxl, pandas |
| Packaging / 打包 | PyInstaller (single-file exe) |
| Logging / 日志 | Python logging + RotatingFileHandler |
| Testing / 测试 | pytest + unittest.mock |
| Platforms / 支持平台 | Windows 7/10/11, 统信UOS V20+, macOS (dev) |
