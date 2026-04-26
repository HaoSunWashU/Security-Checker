from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLabel


class SoftwareTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("软件清单检查 — 点击「开始检查」运行")
        self.browser = QTextBrowser()
        layout.addWidget(self.label)
        layout.addWidget(self.browser)

    def update_result(self, result):
        status = "合规 ✓" if result.passed else "不合规 ✗"
        total = len(result.extra.get("all_software", []))
        self.label.setText(
            f"软件清单检查 — {status}  (已安装: {total} 个，违规: {result.violation_count()} 个)"
        )
        self.browser.setHtml(self._to_html(result))

    def clear(self):
        self.label.setText("软件清单检查 — 点击「开始检查」运行")
        self.browser.clear()

    def _to_html(self, result) -> str:
        all_sw = result.extra.get("all_software", [])
        violation_names = {v.get("name", "").lower() for v in result.violations}

        status_color = "#155724" if result.passed else "#721c24"
        status_bg    = "#d4edda" if result.passed else "#f8d7da"
        summary_box  = (
            f'<div style="background:{status_bg};padding:8px;border-radius:4px;'
            f'color:{status_color};margin-bottom:10px">'
            + result.summary.replace("\n", "<br>") + "</div>"
        )

        if not all_sw:
            return summary_box

        rows = ""
        for sw in all_sw:
            name = sw.get("name", "N/A")
            is_vio = name.lower() in violation_names
            row_style = (
                'background:#f8d7da;color:#721c24;font-weight:bold'
                if is_vio else ''
            )
            flag = " 🚫" if is_vio else ""
            rows += (
                f'<tr style="{row_style}">'
                f'<td>{name}{flag}</td>'
                f'<td>{sw.get("version","N/A")}</td>'
                f'<td>{sw.get("publisher","N/A")}</td>'
                f'<td style="font-size:0.85em">{sw.get("path","N/A")}</td>'
                f'</tr>'
            )

        table = (
            '<table border="1" cellpadding="4" cellspacing="0" '
            'style="border-collapse:collapse;width:100%;font-size:0.88em">'
            '<tr style="background:#343a40;color:white;position:sticky;top:0">'
            '<th>软件名称</th><th>版本</th><th>发行商</th><th>安装路径</th>'
            '</tr>'
            + rows + '</table>'
        )
        return summary_box + table
