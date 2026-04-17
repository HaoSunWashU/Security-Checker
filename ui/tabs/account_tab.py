from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLabel


class AccountTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("账号密码检查 — 点击"开始检查"运行")
        self.browser = QTextBrowser()
        layout.addWidget(self.label)
        layout.addWidget(self.browser)

    def update_result(self, result):
        status = "合规 ✓" if result.passed else "不合规 ✗"
        self.label.setText(f"账号密码检查 — {status}  ({result.violation_count()} 个风险账号)")
        self.browser.setHtml(self._to_html(result))

    def clear(self):
        self.label.setText("账号密码检查 — 点击"开始检查"运行")
        self.browser.clear()

    def _to_html(self, result) -> str:
        lines = []
        for line in result.summary.split("\n"):
            if "不合规" in line or "风险" in line or "弱口令" in line or "空密码" in line:
                lines.append(f'<span style="color:#dc3545;font-weight:bold">{line}</span>')
            else:
                lines.append(line)
        body = "<br>".join(lines)
        color = "#155724" if result.passed else "#721c24"
        bg = "#d4edda" if result.passed else "#f8d7da"
        return f'<div style="background:{bg};padding:8px;border-radius:4px;color:{color}">{body}</div>'
