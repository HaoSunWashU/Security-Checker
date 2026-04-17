# Security Checker — 终端安全合规检查工具

> Cross-platform terminal security compliance checker for Windows, UOS Linux, and macOS.
> 跨平台终端安全合规检查工具，支持 Windows、统信UOS 和 macOS。

---

## Table of Contents / 目录

- [Overview / 概述](#overview--概述)
- [System Requirements / 系统要求](#system-requirements--系统要求)
- [Download / 下载](#download--下载)
- [Installation / 安装](#installation--安装)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [User Guide / 使用说明](#user-guide--使用说明)
  - [Starting the Application / 启动程序](#starting-the-application--启动程序)
  - [Running a Scan / 执行检查](#running-a-scan--执行检查)
  - [Understanding Results / 查看结果](#understanding-results--查看结果)
  - [Exporting Reports / 导出报告](#exporting-reports--导出报告)
  - [Viewing Encrypted Reports / 查看加密报告](#viewing-encrypted-reports--查看加密报告)
  - [Adding Custom Scan Directories / 添加自定义扫描目录](#adding-custom-scan-directories--添加自定义扫描目录)
  - [Clearing Results / 清空记录](#clearing-results--清空记录)
  - [Headless / CLI Mode / 命令行无界面模式](#headless--cli-mode--命令行无界面模式)
- [What Gets Checked / 检查内容说明](#what-gets-checked--检查内容说明)
- [Report Formats / 报告格式](#report-formats--报告格式)
- [Configuration / 配置说明](#configuration--配置说明)
- [Log File / 日志文件](#log-file--日志文件)
- [Privacy & Security / 隐私与安全](#privacy--security--隐私与安全)
- [Troubleshooting / 常见问题](#troubleshooting--常见问题)
- [Packaging / 打包发布](#packaging--打包发布)

---

## Overview / 概述

**English:**
Security Checker scans your computer across four dimensions and generates a compliance report. It runs entirely offline — no data is uploaded. It is designed for government agencies, enterprises, and anyone performing internal network security self-assessments.

**中文：**
终端安全检查工具对您的计算机进行四大维度安全自查，并生成合规报告。工具完全离线运行，数据不上传。适用于党政机关、企事业单位及需要执行内网安全自查的场景。

**Four check modules / 四大检查模块：**

| Module / 模块 | What it checks / 检查内容 |
|---|---|
| Software Inventory / 软件清单 | Blacklisted software (remote tools, proxies, cloud drives, cracking tools) / 违规软件（远控、代理、网盘、破解工具）|
| Account & Password / 账号密码 | Weak passwords, empty passwords, guest accounts / 弱口令、空密码、来宾账号 |
| Security Policy / 安全策略 | Firewall, auto-update, open ports, USB, screen lock, remote desktop, logging, antivirus / 防火墙、自动更新、危险端口、USB、锁屏、远程桌面、日志、杀软 |
| Sensitive Files / 敏感信息 | Files containing ID numbers, phone numbers, emails, or classified keywords / 含身份证号、手机号、邮箱、密级关键词的文件 |

---

## System Requirements / 系统要求

| Item / 项目 | Requirement / 要求 |
|---|---|
| OS / 操作系统 | Windows 7 / 10 / 11, 统信UOS V20+, macOS 12+ |
| Python | 3.10 or above / 3.10 及以上 |
| Permissions / 权限 | **Run as Administrator** (recommended) / **建议以管理员身份运行** |
| Disk space / 磁盘空间 | ~50 MB |
| Network / 网络 | Not required — fully offline / 不需要，完全离线运行 |

---

## Download / 下载

**English:**
The easiest way to get started on Windows is to download the pre-built executable from the GitHub Releases page — no Python installation required.

**中文：**
Windows用户最简单的方式是从 GitHub Releases 页面下载预编译的可执行文件，无需安装 Python。

| Platform / 平台 | Download / 下载 | Notes / 说明 |
|---|---|---|
| Windows 7 / 10 / 11 | [SecurityChecker.exe](https://github.com/HaoSunWashU/Security-Checker/releases/latest) | Double-click to run / 双击运行 |
| UOS Linux / macOS | Run from source / 源码运行 | See Installation below / 见下方安装说明 |

> **Windows users / Windows用户:** Right-click → "Run as administrator" for full results. / 右键 → "以管理员身份运行"以获取完整检查结果。

---

## Installation / 安装

### Option A: Download pre-built executable (Windows) / 方式A：下载预编译文件（Windows）

1. Go to [Releases](https://github.com/HaoSunWashU/Security-Checker/releases/latest)
2. Download `SecurityChecker.exe`
3. Right-click → **Run as administrator**

前往 [Releases](https://github.com/HaoSunWashU/Security-Checker/releases/latest) 下载 `SecurityChecker.exe`，右键以管理员身份运行即可。

---

### Option B: Run from source / 方式B：源码运行

```bash
# 1. Clone the repository / 克隆仓库
git clone https://github.com/HaoSunWashU/Security-Checker.git
cd Security-Checker

# 2. Install dependencies / 安装依赖
pip install -r requirements.txt

# 3. Run / 运行
python main.py
```

### Option C: Run packaged executable (UOS Linux) / 方式C：运行打包后的可执行文件（统信UOS）

- **UOS Linux**: Run `./SecurityChecker` in terminal / 在终端中执行 `./SecurityChecker`

> **Antivirus note / 杀软注意事项:** Your antivirus may flag the `.exe` on first run. This is a false positive common with PyInstaller — add it to your trusted list. / 首次运行时杀毒软件可能误报（PyInstaller常见问题），请将其添加到信任列表。

---

## Quick Start / 快速开始

**English:**
1. Launch the application as Administrator
2. Click **"开始检查"** (Start Check)
3. Wait for the progress bar to reach 100%
4. Review results in each tab
5. Click **"导出报告"** (Export Report) to save your report

**中文：**
1. 以管理员身份启动程序
2. 点击 **"开始检查"**
3. 等待进度条到达100%
4. 查看各标签页中的检查结果
5. 点击 **"导出报告"** 保存报告

---

## User Guide / 使用说明

### Starting the Application / 启动程序

**English:**
- **Windows:** Right-click `SecurityChecker.exe` → "Run as administrator"
- **UOS Linux:** Open terminal → `sudo ./SecurityChecker`
- **Source:** Open terminal → `sudo python main.py` (Linux/macOS) or run as admin (Windows)

**中文：**
- **Windows：** 右键点击 `SecurityChecker.exe` → 选择"以管理员身份运行"
- **统信UOS：** 打开终端 → `sudo ./SecurityChecker`
- **源码运行：** 打开终端 → `sudo python main.py`（Linux/macOS）或以管理员身份运行（Windows）

---

### Running a Scan / 执行检查

**English:**
1. Click the **"开始检查"** button in the toolbar.
2. All four modules run in parallel. The progress bar advances by 25% as each module finishes.
3. Each tab updates automatically when its module completes.
4. A summary dialog appears when all checks are done.

**中文：**
1. 点击工具栏中的 **"开始检查"** 按钮。
2. 四个检查模块并行运行，每完成一个模块进度条增加25%。
3. 每个标签页在对应模块完成后自动显示结果。
4. 全部完成后弹出检查完成提示框。

---

### Understanding Results / 查看结果

**English:**
Each tab displays results with color coding:

- **Green background** — module passed, no issues found
- **Red background** — issues were found; red-highlighted lines show specific violations
- **Recommendations** — listed below the results when non-compliant items are found

**中文：**
每个标签页以颜色区分检查结果：

- **绿色背景** — 该模块合规，未发现问题
- **红色背景** — 发现问题，红色高亮行显示具体违规项
- **整改建议** — 不合规时在结果下方列出具体建议

---

### Exporting Reports / 导出报告

**English:**
1. Click **"导出报告"** in the toolbar.
2. Select a format: **HTML**, **Excel**, **PDF**, or **TXT**.
3. Choose a save location and click **"导出"**.
4. Two files are created automatically:
   - Your chosen report file (e.g., `security_report.html`)
   - An encrypted backup: `security_report_encrypted.sec`

**中文：**
1. 点击工具栏中的 **"导出报告"**。
2. 选择格式：**HTML**、**Excel**、**PDF** 或 **TXT**。
3. 选择保存位置，点击 **"导出"**。
4. 程序自动生成两个文件：
   - 您选择格式的报告文件（如 `security_report.html`）
   - 加密备份文件：`security_report_encrypted.sec`

| Format / 格式 | Best for / 适用场景 |
|---|---|
| HTML | General viewing, printing / 通用查看、打印 |
| Excel | Data analysis, statistics / 数据统计分析 |
| PDF | Formal filing, tamper-evident / 正式存档 |
| TXT | Small file size, maximum compatibility / 体积小、兼容性最强 |

---

### Viewing Encrypted Reports / 查看加密报告

**English:**
1. Click **"查看报告"** in the toolbar.
2. Click **"浏览"** and select a `.sec` encrypted file.
3. Enter the report password (default: `Sec@2026`).
4. Click **"解密预览"** — the first 2,000 characters are shown.

> To change the default password, edit `config.json` and update the `report_password` field.

**中文：**
1. 点击工具栏中的 **"查看报告"**。
2. 点击 **"浏览"**，选择 `.sec` 加密文件。
3. 输入报告密码（默认：`Sec@2026`）。
4. 点击 **"解密预览"** — 显示前2000字符内容。

> 如需修改默认密码，请编辑 `config.json`，更新 `report_password` 字段。

---

### Adding Custom Scan Directories / 添加自定义扫描目录

**English:**
The sensitive file scanner checks your Desktop and Documents folders by default. To add more directories:
1. Switch to the **"敏感信息检查"** tab.
2. Click **"添加目录"** and select any folder (e.g., `D:\work`, `E:\projects`).
3. To remove a directory, select it in the list and click **"移除选中"**.
4. Custom directories are used in the next scan when you click "开始检查".

**中文：**
敏感信息检查默认扫描桌面和文档文件夹，如需扫描其他目录：
1. 切换到 **"敏感信息检查"** 标签页。
2. 点击 **"添加目录"**，选择需要扫描的文件夹（如 `D:\work`、`E:\项目`）。
3. 如需移除，选中列表中的目录后点击 **"移除选中"**。
4. 自定义目录将在下次点击"开始检查"时生效。

---

### Clearing Results / 清空记录

**English:**
Click **"清空记录"** in the toolbar to reset all tabs and clear cached scan results. This does not delete any exported report files.

**中文：**
点击工具栏中的 **"清空记录"** 可重置所有标签页并清除缓存的扫描结果。此操作不会删除已导出的报告文件。

---

### Headless / CLI Mode / 命令行无界面模式

**English:**
For automated or scripted use (no GUI):

```bash
# Run all checks and export as HTML
python main.py --headless --export html --output /path/to/report.html

# Export as TXT
python main.py --headless --export txt --output report.txt

# Available formats: html, txt, excel, pdf
```

Exit code: `0` = no violations found, `1` = violations found.

**中文：**
适用于自动化、脚本化执行场景（无图形界面）：

```bash
# 执行全部检查并导出HTML报告
python main.py --headless --export html --output /path/to/report.html

# 导出TXT格式
python main.py --headless --export txt --output report.txt

# 可选格式：html、txt、excel、pdf
```

退出码：`0` = 未发现违规，`1` = 发现违规项。

---

## What Gets Checked / 检查内容说明

### Software Inventory / 软件清单检查

**English:**
Scans all installed software and flags anything matching the blacklist, including:
- Remote control tools: TeamViewer, AnyDesk, ToDesk, 向日葵, UltraViewer
- Proxy/VPN tools: Shadowsocks, V2Ray, Clash, Tor Browser, Freegate
- Cloud storage: 百度网盘, 阿里云盘, Dropbox, OneDrive
- Hacking tools: Wireshark, Nmap, Metasploit, Burp Suite, mimikatz
- Cracked/pirated software

> The blacklist can be extended in `config.json` under `blacklist_software`.

**中文：**
扫描所有已安装软件，检测是否存在以下类型的违规软件：
- 远程控制工具：TeamViewer、AnyDesk、ToDesk、向日葵、UltraViewer
- 代理/翻墙工具：Shadowsocks、V2Ray、Clash、Tor Browser、Freegate
- 云存储工具：百度网盘、阿里云盘、Dropbox、OneDrive
- 黑客工具：Wireshark、Nmap、Metasploit、Burp Suite、mimikatz
- 破解/盗版软件

> 可在 `config.json` 的 `blacklist_software` 字段中扩展黑名单。

---

### Account & Password / 账号密码检查

**English:**
Checks all local user accounts for:
- Empty passwords
- Passwords that never expire
- Guest or anonymous accounts
- Account names that are themselves common weak passwords

**中文：**
检查本机所有用户账号，包括：
- 空密码账号
- 密码永不过期的账号
- 来宾/匿名账号
- 账号名本身为弱口令的账号

---

### Security Policy / 安全策略检查

**English:**
Checks 9 system policy items:

| # | Policy / 策略项 | Compliant condition / 合规条件 |
|---|---|---|
| 1 | Firewall / 防火墙 | Enabled on all profiles / 所有配置文件均已启用 |
| 2 | Auto-update / 自动更新 | Enabled / 已启用 |
| 3 | Dangerous ports / 危险端口 | 21, 22, 23, 135, 139, 445, 3389 etc. not listening / 未监听 |
| 4 | USB storage / USB存储 | Disabled or read-only / 已禁用或只读 |
| 5 | Screen lock / 屏幕锁屏 | Auto-lock within 10 minutes / 10分钟内自动锁屏 |
| 6 | Remote desktop/SSH | Disabled / 已关闭 |
| 7 | Audit logging / 审计日志 | Enabled / 已启用 |
| 8 | Antivirus running / 安全软件运行 | Active / 正在运行 |
| 9 | Antivirus updated / 安全软件更新 | Requires manual verification / 需人工核实 |

**中文：**
检查9项系统安全策略（详见上表）。

---

### Sensitive File Scan / 敏感信息检查

**English:**
Scans files in Desktop, Documents, and any custom directories you add. Detects:
- **Chinese ID numbers** — 18-digit format
- **Mobile phone numbers** — 11-digit Chinese mobile numbers
- **Email addresses**
- **Classified keywords** — 绝密、机密、秘密、商密、内部敏感、不予公开, etc.

Supported file types: `.txt`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.pdf`, `.csv`, `.md`

Files larger than 50 MB are skipped. Only the first/last 10 KB of text files and first 3 pages of PDFs/Word docs are scanned for performance.

**中文：**
扫描桌面、文档及您添加的自定义目录中的文件，检测以下内容：
- **身份证号** — 18位格式
- **手机号** — 11位中国大陆手机号
- **电子邮箱地址**
- **密级关键词** — 绝密、机密、秘密、商密、内部敏感、不予公开等

支持文件格式：`.txt`、`.doc`、`.docx`、`.xls`、`.xlsx`、`.pdf`、`.csv`、`.md`

超过50MB的文件将被跳过。文本文件仅读取头尾各10KB，PDF/Word文档仅读取前3页，以确保扫描性能。

---

## Report Formats / 报告格式

**English:**
Every report includes device name, OS, MAC address, IP address, and check time at the top, followed by results from all four modules and remediation recommendations.

An encrypted backup (`.sec`) is automatically generated alongside every export. It uses AES-256-CFB encryption and can only be decrypted with the correct password via the "查看报告" function.

**中文：**
每份报告顶部包含设备名称、操作系统、MAC地址、IP地址和检查时间，正文包含四大模块的检查结果及整改建议。

每次导出时自动生成加密备份（`.sec`），采用AES-256-CFB加密，只能通过"查看报告"功能输入正确密码后解密查看。

---

## Configuration / 配置说明

Edit `config.json` to customize behavior. Key fields:

| Field / 字段 | Description / 说明 | Default / 默认值 |
|---|---|---|
| `report_password` | Password for encrypted `.sec` reports / 加密报告密码 | `Sec@2026` |
| `blacklist_software` | List of blacklisted software names / 软件黑名单列表 | See file |
| `sensitive_keywords` | Classified keywords to detect / 密级关键词列表 | See file |
| `weak_passwords` | Weak password dictionary / 弱口令字典 | 50 common passwords |
| `dangerous_ports` | Port numbers to check / 危险端口列表 | 21,22,23,135,139,445,3389... |
| `max_file_size_mb` | Skip files larger than this / 跳过超过此大小的文件 | `50` |
| `default_scan_dirs` | Additional directories always scanned / 固定额外扫描目录 | `[]` |

> After editing `config.json`, restart the application for changes to take effect.
> 修改 `config.json` 后，重启程序使配置生效。

---

## Log File / 日志文件

**English:**
The application writes a log file `check_error.log` in the same directory as the executable. If you encounter unexpected behavior and want to report it, please attach this file. The log records:
- Startup information (Python version, OS, platform)
- Each check module's start, results, and any errors with full stack traces
- Report export and encryption events
- All user actions (scan start, export, clear)

The log file rotates automatically at 5 MB and keeps 3 backups (`check_error.log.1`, `.2`, `.3`).

**中文：**
程序运行时在可执行文件同目录下生成日志文件 `check_error.log`。如遇异常情况需要反馈，请附上此文件。日志记录以下内容：
- 启动信息（Python版本、操作系统、平台）
- 每个检查模块的启动、结果及完整错误堆栈
- 报告导出和加密事件
- 所有用户操作（开始检查、导出、清空）

日志文件超过5MB时自动轮转，保留3个备份（`check_error.log.1`、`.2`、`.3`）。

---

## Privacy & Security / 隐私与安全

**English:**
- **Fully offline.** No data is sent to any server at any time.
- **Sensitive scan results** are only stored locally in `cache/last_scan.json` and in your exported report.
- The encrypted `.sec` file uses AES-256-CFB encryption. Without the correct password it cannot be read.
- The default report password `Sec@2026` should be changed before deployment in your organization.

**中文：**
- **完全离线运行。** 任何数据均不会上传至任何服务器。
- **敏感扫描结果** 仅存储在本地 `cache/last_scan.json` 及您导出的报告中。
- 加密备份 `.sec` 文件采用AES-256-CFB加密，没有正确密码无法读取。
- 默认报告密码 `Sec@2026` 在组织内部署前应修改为自定义密码。

---

## Troubleshooting / 常见问题

**Q: The antivirus flags the `.exe` file.**
**Q: 杀毒软件提示`.exe`文件有风险。**

EN: This is a false positive common with PyInstaller-packaged executables. Add the file to your antivirus trusted list and re-run.
中文：这是PyInstaller打包程序常见的误报。将文件添加到杀毒软件信任列表后重新运行。

---

**Q: Software check shows 0 installed programs.**
**Q: 软件清单检查显示已安装软件数量为0。**

EN: This usually means the application was not run with administrator privileges. Restart as Administrator.
中文：通常是因为未以管理员身份运行。请以管理员身份重新启动程序。

---

**Q: Sensitive file scan finds nothing but I know sensitive files exist.**
**Q: 敏感信息检查未发现文件，但我知道存在敏感文件。**

EN: Check that the files are in a scanned directory and are one of the supported formats (`.txt`, `.docx`, `.xlsx`, `.pdf`, etc.). Files over 50 MB are skipped. You can also add the specific directory in the "敏感信息检查" tab before scanning.
中文：请确认文件位于已扫描目录中，且文件格式为支持的类型（`.txt`、`.docx`、`.xlsx`、`.pdf`等）。超过50MB的文件会被跳过。您也可以在"敏感信息检查"标签页中手动添加指定目录后重新扫描。

---

**Q: "查看报告" shows "解密失败".**
**Q: "查看报告"显示"解密失败"。**

EN: The password is incorrect, or the `.sec` file is corrupted. The default password is `Sec@2026`. If you changed it in `config.json`, use your updated password.
中文：密码错误或文件已损坏。默认密码为 `Sec@2026`。如已在 `config.json` 中修改，请使用更新后的密码。

---

**Q: How do I report a bug?**
**Q: 如何反馈问题？**

EN: Please provide: (1) a description of what happened, (2) your OS and version, and (3) the `check_error.log` file. Submit via GitHub Issues.
中文：请提供：(1) 问题描述，(2) 操作系统及版本，(3) `check_error.log` 日志文件。通过 GitHub Issues 提交反馈。

---

## Packaging / 打包发布

**English:**
To build a standalone `.exe` yourself (must be done on a Windows machine):

```bash
# Install dependencies + PyInstaller
pip install -r requirements.txt
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --windowed --name SecurityChecker main.py
```

Output: `dist/SecurityChecker.exe`. Copy this file to any Windows machine — no Python required.

To publish it as a GitHub Release:
1. Build the `.exe` on Windows using the command above
2. Go to [Releases](https://github.com/HaoSunWashU/Security-Checker/releases) → edit the draft release
3. Attach `dist/SecurityChecker.exe` and publish

**中文：**
自行打包独立 `.exe`（必须在 Windows 机器上执行）：

```bash
# 安装依赖及打包工具
pip install -r requirements.txt
pip install pyinstaller

# 打包为单文件可执行程序
pyinstaller --onefile --windowed --name SecurityChecker main.py
```

输出文件：`dist/SecurityChecker.exe`，可直接复制到任意 Windows 机器运行，无需安装 Python。

发布到 GitHub Release：
1. 在 Windows 机器上使用上述命令打包生成 `.exe`
2. 前往 [Releases](https://github.com/HaoSunWashU/Security-Checker/releases) → 编辑草稿发布
3. 上传 `dist/SecurityChecker.exe` 并发布

---

## License / 许可证

For internal use only. / 仅供内部使用。
