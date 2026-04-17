from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLabel


class SoftwareTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("软件清单检查 — 点击"开始检查"运行")
        self.browser = QTextBrowser()
        layout.addWidget(self.label)
        layout.addWidget(self.browser)

    def update_result(self, result):
        status = "合规 ✓" if result.passed else "不合规 ✗"
        self.label.setText(f"软件清单检查 — {status}  ({result.violation_count()} 个违规项)")
        self.browser.setHtml(self._to_html(result))

    def clear(self):
        self.label.setText("软件清单检查 — 点击"开始检查"运行")
        self.browser.clear()

    def _to_html(self, result) -> str:
        body = result.summary.replace("\n", "<br>")
        color = "#155724" if result.passed else "#721c24"
        bg = "#d4edda" if result.passed else "#f8d7da"
        return f'<div style="background:{bg};padding:8px;border-radius:4px;color:{color}">{body}</div>'
