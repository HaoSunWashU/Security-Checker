import json
import os
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from utils.logger import get_logger
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QProgressBar,
    QToolBar, QAction, QLabel, QMessageBox, QWidget, QVBoxLayout
)
from ui.tabs.software_tab import SoftwareTab
from ui.tabs.account_tab import AccountTab
from ui.tabs.policy_tab import PolicyTab
from ui.tabs.sensitive_tab import SensitiveTab
from ui.dialogs.export_dialog import ExportDialog
from ui.dialogs.view_report_dialog import ViewReportDialog


class _CheckerSignals(QObject):
    result_ready = pyqtSignal(str, object)
    error = pyqtSignal(str, str)


class _CheckerRunner(QRunnable):
    def __init__(self, checker, signals: _CheckerSignals):
        super().__init__()
        self.checker = checker
        self.signals = signals

    def run(self):
        try:
            result = self.checker.run()
            self.signals.result_ready.emit(result.module, result)
        except Exception as e:
            self.signals.error.emit(self.checker.__class__.__name__, str(e))


class MainWindow(QMainWindow):
    def __init__(self, system_info: dict):
        super().__init__()
        self.logger = get_logger("MainWindow")
        self.logger.info(f"GUI started — host: {system_info.get('hostname')}, OS: {system_info.get('os')}")
        self.system_info = system_info
        self.results = {}
        self._completed = 0

        self.setWindowTitle("终端安全合规检查工具")
        self.setMinimumSize(900, 680)

        self._build_toolbar()
        self._build_central()

    def _build_toolbar(self):
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        self.start_action = QAction("开始检查", self)
        self.start_action.triggered.connect(self._start_scan)
        toolbar.addAction(self.start_action)

        toolbar.addSeparator()

        view_action = QAction("查看报告", self)
        view_action.triggered.connect(self._view_report)
        toolbar.addAction(view_action)

        export_action = QAction("导出报告", self)
        export_action.triggered.connect(self._export_report)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        clear_action = QAction("清空记录", self)
        clear_action.triggered.connect(self._clear)
        toolbar.addAction(clear_action)

        toolbar.addSeparator()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(200)
        toolbar.addWidget(self.progress_bar)

        self.status_label = QLabel("  就绪")
        toolbar.addWidget(self.status_label)

    def _build_central(self):
        self.tabs = QTabWidget()
        self.software_tab = SoftwareTab()
        self.account_tab = AccountTab()
        self.policy_tab = PolicyTab()
        self.sensitive_tab = SensitiveTab()

        self.tabs.addTab(self.software_tab, "软件清单")
        self.tabs.addTab(self.account_tab, "账号密码")
        self.tabs.addTab(self.policy_tab, "安全策略")
        self.tabs.addTab(self.sensitive_tab, "敏感信息检查")

        self.setCentralWidget(self.tabs)

    def _start_scan(self):
        from checkers.software_checker import SoftwareChecker
        from checkers.account_checker import AccountChecker
        from checkers.policy_checker import PolicyChecker
        from checkers.sensitive_checker import SensitiveChecker

        self.logger.info("User started scan")
        self.results = {}
        self._completed = 0
        self.progress_bar.setValue(0)
        self.start_action.setEnabled(False)
        self.status_label.setText("  检查中…")

        extra_dirs = self.sensitive_tab.get_extra_dirs()
        checkers = [
            SoftwareChecker(),
            AccountChecker(),
            PolicyChecker(),
            SensitiveChecker(extra_dirs=extra_dirs),
        ]

        self._signals = _CheckerSignals()
        self._signals.result_ready.connect(self._on_result)
        self._signals.error.connect(self._on_error)

        pool = QThreadPool.globalInstance()
        for checker in checkers:
            runner = _CheckerRunner(checker, self._signals)
            pool.start(runner)

    def _on_result(self, module: str, result):
        status = "PASS" if result.passed else "FAIL"
        self.logger.info(f"[{status}] {module} — {result.violation_count()} violation(s)")
        self.results[module] = result
        self._completed += 1
        self.progress_bar.setValue(self._completed * 25)

        tab_map = {
            "软件清单检查": self.software_tab,
            "账号密码检查": self.account_tab,
            "安全策略检查": self.policy_tab,
            "敏感信息检查": self.sensitive_tab,
        }
        tab = tab_map.get(module)
        if tab:
            tab.update_result(result)

        self._cache_results()

        if self._completed == 4:
            self.start_action.setEnabled(True)
            self.status_label.setText("  检查完成")
            violations_total = sum(r.violation_count() for r in self.results.values())
            self.logger.info(f"Scan complete — total violations: {violations_total}")
            QMessageBox.information(
                self, "检查完成",
                f"全部检查完成！\n共发现 {violations_total} 项风险/违规。\n可点击"导出报告"生成合规报告。"
            )

    def _on_error(self, checker_name: str, error_msg: str):
        self.logger.error(f"{checker_name} failed: {error_msg}")
        self._completed += 1
        self.progress_bar.setValue(self._completed * 25)
        QMessageBox.warning(self, "检查出错", f"{checker_name} 运行时出错:\n{error_msg}")
        if self._completed == 4:
            self.start_action.setEnabled(True)
            self.status_label.setText("  检查完成（有错误）")

    def _export_report(self):
        if not self.results:
            QMessageBox.warning(self, "提示", "请先运行检查，再导出报告。")
            return
        dialog = ExportDialog(self)
        if dialog.exec_():
            fmt, path = dialog.get_selection()
            if not path:
                QMessageBox.warning(self, "提示", "请选择保存路径。")
                return
            self.logger.info(f"User exporting report: fmt={fmt}, path={path}")
            try:
                from utils import report_generator
                report_generator.generate(list(self.results.values()), fmt, path, self.system_info)
                self.logger.info("Report export successful")
                QMessageBox.information(self, "导出成功", f"报告已保存至:\n{path}\n同时已生成加密备份 .sec 文件。")
            except Exception as e:
                self.logger.error(f"Report export failed: {e}")
                QMessageBox.critical(self, "导出失败", str(e))

    def _view_report(self):
        dialog = ViewReportDialog(self)
        dialog.exec_()

    def _clear(self):
        self.logger.info("User cleared results")
        self.results = {}
        self._completed = 0
        self.progress_bar.setValue(0)
        self.status_label.setText("  就绪")
        for tab in (self.software_tab, self.account_tab, self.policy_tab, self.sensitive_tab):
            tab.clear()

    def _cache_results(self):
        try:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, "last_scan.json")
            data = {
                module: {
                    "passed": r.passed,
                    "summary": r.summary,
                    "violations": r.violations,
                    "recommendations": r.recommendations,
                }
                for module, r in self.results.items()
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
