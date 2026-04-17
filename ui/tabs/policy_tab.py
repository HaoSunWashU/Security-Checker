from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLabel


class PolicyTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("安全策略检查 — 点击「开始检查」运行")
        self.browser = QTextBrowser()
        layout.addWidget(self.label)
        layout.addWidget(self.browser)

    def update_result(self, result):
        status = "合规 ✓" if result.passed else "不合规 ✗"
        non = result.violation_count()
        self.label.setText(f"安全策略检查 — {status}  ({non} 项不合规)")
        self.browser.setHtml(self._to_html(result))

    def clear(self):
        self.label.setText("安全策略检查 — 点击「开始检查」运行")
        self.browser.clear()

    def _to_html(self, result) -> str:
        lines = []
        for line in result.summary.split("\n"):
            if "✗ 不合规" in line:
                lines.append(f'<span style="color:#dc3545;font-weight:bold">{line}</span>')
            elif "✓ 合规" in line:
                lines.append(f'<span style="color:#28a745">{line}</span>')
            else:
                lines.append(line)
        return "<br>".join(lines)
