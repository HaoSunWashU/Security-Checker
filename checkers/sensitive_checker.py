import os
import re
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from checkers.base_checker import BaseChecker, CheckResult


class SensitiveChecker(BaseChecker):

    ID_PATTERN = re.compile(r"\b\d{17}[\dXx]\b")
    PHONE_PATTERN = re.compile(r"\b1[3-9]\d{9}\b")
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

    def __init__(self, extra_dirs: list = None):
        super().__init__()
        self.extra_dirs = extra_dirs or []

    def run(self) -> CheckResult:
        self.logger.info("SensitiveChecker started")
        dirs = self._get_scan_dirs()
        keywords = self.config.get("sensitive_keywords", [])
        extensions = set(self.config.get("scan_extensions", []))
        max_mb = self.config.get("max_file_size_mb", 50)
        max_bytes = max_mb * 1024 * 1024

        files = []
        for d in dirs:
            files.extend(self._collect_files(d, extensions, max_bytes))

        violations = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(self._scan_file, f, keywords, max_bytes): f for f in files
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    violations.append(result)

        passed = len(violations) == 0
        total_scanned = len(files)

        summary = f"扫描目录: {dirs}\n扫描文件总数: {total_scanned}\n发现敏感文件数: {len(violations)}\n"
        if violations:
            summary += "\n敏感文件列表:\n"
            for v in violations:
                summary += f"  - {v['path']}\n    命中: {', '.join(v['hits'])}\n"
        else:
            summary += "\n未发现敏感信息文件。"

        recommendations = []
        if violations:
            recommendations.append("请及时清理或加密上述包含敏感信息的文件，避免明文存储身份证号、手机号、密级关键词等信息。")

        self.logger.info(f"SensitiveChecker done: {len(violations)} sensitive files found")
        return CheckResult(
            module="敏感信息检查",
            passed=passed,
            violations=violations,
            summary=summary,
            recommendations=recommendations,
        )

    def _get_scan_dirs(self) -> list:
        home = os.path.expanduser("~")
        system = platform.system()
        if system == "Windows":
            defaults = [
                os.path.join(home, "Desktop"),
                os.path.join(home, "Documents"),
            ]
        else:
            defaults = [
                os.path.join(home, "Desktop"),
                os.path.join(home, "Documents"),
            ]
        configured = self.config.get("default_scan_dirs", [])
        all_dirs = defaults + configured + self.extra_dirs
        return [d for d in all_dirs if os.path.isdir(d)]

    def _collect_files(self, directory: str, extensions: set, max_bytes: int) -> list:
        result = []
        try:
            for entry in os.scandir(directory):
                if entry.is_dir(follow_symlinks=False):
                    result.extend(self._collect_files(entry.path, extensions, max_bytes))
                elif entry.is_file(follow_symlinks=False):
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in extensions:
                        try:
                            if entry.stat().st_size <= max_bytes:
                                result.append(entry.path)
                        except OSError:
                            pass
        except PermissionError:
            pass
        except Exception as e:
            self.logger.warning(f"Error scanning {directory}: {e}")
        return result

    def _scan_file(self, path: str, keywords: list, max_bytes: int) -> dict | None:
        hits = []
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        try:
            if ext in (".txt", ".csv", ".md"):
                text = self._read_text_partial(path)
            elif ext in (".doc", ".docx"):
                text = self._read_docx(path)
            elif ext == ".pdf":
                text = self._read_pdf(path)
            elif ext in (".xls", ".xlsx"):
                text = self._read_excel(path)
            else:
                return None

            if self.ID_PATTERN.search(text):
                hits.append("身份证号")
            if self.PHONE_PATTERN.search(text):
                hits.append("手机号")
            if self.EMAIL_PATTERN.search(text):
                hits.append("邮箱地址")
            for kw in keywords:
                if kw in text:
                    hits.append(f"密级关键词({kw})")
                    break

        except Exception as e:
            self.logger.debug(f"Could not scan {path}: {e}")
            return None

        if hits:
            return {"path": path, "hits": hits}
        return None

    def _read_text_partial(self, path: str) -> str:
        chunk = 10 * 1024
        try:
            with open(path, "rb") as f:
                head = f.read(chunk)
                try:
                    f.seek(-chunk, 2)
                except OSError:
                    f.seek(0)
                tail = f.read(chunk)
            return (head + tail).decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def _read_docx(self, path: str) -> str:
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs[:30])
        except Exception:
            return ""

    def _read_pdf(self, path: str) -> str:
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                pages = pdf.pages[:3]
                return "\n".join(p.extract_text() or "" for p in pages)
        except Exception:
            return ""

    def _read_excel(self, path: str) -> str:
        try:
            import pandas as pd
            df = pd.read_excel(path, nrows=100)
            return df.to_string()
        except Exception:
            return ""
