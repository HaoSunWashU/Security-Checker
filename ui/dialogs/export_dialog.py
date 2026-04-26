from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFileDialog
)


class ExportDialog(QDialog):
    def __init__(self, parent=None, suggested_name: str = "security_report"):
        super().__init__(parent)
        self.setWindowTitle("导出报告")
        self.setMinimumWidth(420)
        self._fmt = "html"
        self._path = ""
        self._suggested_name = suggested_name

        layout = QVBoxLayout(self)

        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("导出格式:"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["HTML", "Excel", "PDF", "TXT"])
        fmt_layout.addWidget(self.fmt_combo)
        layout.addLayout(fmt_layout)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("保存路径:"))
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("点击右侧按钮选择保存位置…")
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("导出")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _browse(self):
        ext_map = {"HTML": "html", "Excel": "xlsx", "PDF": "pdf", "TXT": "txt"}
        fmt = self.fmt_combo.currentText()
        ext = ext_map.get(fmt, "txt")
        path, _ = QFileDialog.getSaveFileName(
            self, "保存报告", f"{self._suggested_name}.{ext}",
            f"{fmt} Files (*.{ext});;All Files (*)"
        )
        if path:
            self.path_edit.setText(path)

    def get_selection(self):
        return self.fmt_combo.currentText().lower(), self.path_edit.text()
