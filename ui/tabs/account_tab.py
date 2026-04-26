from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLabel


class AccountTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("账号密码检查 — 点击「开始检查」运行")
        self.browser = QTextBrowser()
        layout.addWidget(self.label)
        layout.addWidget(self.browser)

    def update_result(self, result):
        status = "合规 ✓" if result.passed else "不合规 ✗"
        total = len(result.extra.get("all_accounts", []))
        self.label.setText(
            f"账号密码检查 — {status}  (账号总数: {total}，风险: {result.violation_count()} 个)"
        )
        self.browser.setHtml(self._to_html(result))

    def clear(self):
        self.label.setText("账号密码检查 — 点击「开始检查」运行")
        self.browser.clear()

    def _to_html(self, result) -> str:
        all_accounts = result.extra.get("all_accounts", [])
        risk_map = {v["name"]: v["issues"] for v in result.violations}

        status_color = "#155724" if result.passed else "#721c24"
        status_bg    = "#d4edda" if result.passed else "#f8d7da"
        summary_box  = (
            f'<div style="background:{status_bg};padding:8px;border-radius:4px;'
            f'color:{status_color};margin-bottom:10px">'
            + result.summary.replace("\n", "<br>") + "</div>"
        )

        if not all_accounts:
            return summary_box

        rows = ""
        for acc in all_accounts:
            name   = acc.get("name", "N/A")
            issues = risk_map.get(name)
            is_risk = bool(issues)
            row_style = (
                'background:#f8d7da;color:#721c24;font-weight:bold'
                if is_risk else ''
            )
            issue_cell = ', '.join(issues) if issues else '—'
            flag = " ⚠" if is_risk else ""
            rows += (
                f'<tr style="{row_style}">'
                f'<td>{name}{flag}</td>'
                f'<td>{acc.get("type","N/A")}</td>'
                f'<td>{"是" if acc.get("empty_password") else "否"}</td>'
                f'<td>{"是" if acc.get("password_never_expires") else "否"}</td>'
                f'<td>{"是" if acc.get("disabled") else "否"}</td>'
                f'<td>{issue_cell}</td>'
                f'</tr>'
            )

        table = (
            '<table border="1" cellpadding="4" cellspacing="0" '
            'style="border-collapse:collapse;width:100%;font-size:0.88em">'
            '<tr style="background:#343a40;color:white">'
            '<th>账号名</th><th>类型</th><th>空密码</th>'
            '<th>密码永不过期</th><th>已禁用</th><th>风险项</th>'
            '</tr>'
            + rows + '</table>'
        )
        return summary_box + table
