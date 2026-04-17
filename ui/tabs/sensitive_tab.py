from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QLabel, QListWidget, QPushButton, QFileDialog, QGroupBox
)


class SensitiveTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.label = QLabel("敏感信息检查 — 点击「开始检查」运行")
        layout.addWidget(self.label)

        dir_group = QGroupBox("自定义扫描目录（默认扫描桌面和文档，可添加其他目录）")
        dir_layout = QVBoxLayout(dir_group)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加目录")
        self.remove_btn = QPushButton("移除选中")
        self.add_btn.clicked.connect(self._add_directory)
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()

        self.dir_list = QListWidget()
        self.dir_list.setMaximumHeight(100)

        dir_layout.addLayout(btn_layout)
        dir_layout.addWidget(self.dir_list)
        layout.addWidget(dir_group)

        self.browser = QTextBrowser()
        layout.addWidget(self.browser)

    def get_extra_dirs(self) -> list:
        return [self.dir_list.item(i).text() for i in range(self.dir_list.count())]

    def update_result(self, result):
        status = "合规 ✓" if result.passed else "不合规 ✗"
        self.label.setText(f"敏感信息检查 — {status}  ({result.violation_count()} 个敏感文件)")
        self.browser.setHtml(self._to_html(result))

    def clear(self):
        self.label.setText("敏感信息检查 — 点击「开始检查」运行")
        self.browser.clear()

    def _add_directory(self):
        path = QFileDialog.getExistingDirectory(self, "选择目录")
        if path:
            existing = self.get_extra_dirs()
            if path not in existing:
                self.dir_list.addItem(path)

    def _remove_selected(self):
        for item in self.dir_list.selectedItems():
            self.dir_list.takeItem(self.dir_list.row(item))

    def _to_html(self, result) -> str:
        lines = []
        for line in result.summary.split("\n"):
            if line.strip().startswith("-"):
                lines.append(f'<span style="color:#dc3545">{line}</span>')
            else:
                lines.append(line)
        body = "<br>".join(lines)
        color = "#155724" if result.passed else "#721c24"
        bg = "#d4edda" if result.passed else "#f8d7da"
        return f'<div style="background:{bg};padding:8px;border-radius:4px;color:{color}">{body}</div>'
