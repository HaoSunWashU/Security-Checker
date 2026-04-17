import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextBrowser, QFileDialog, QMessageBox
)
from utils import crypto


class ViewReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("查看加密报告")
        self.setMinimumSize(600, 480)

        layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("加密文件:"))
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("选择 .sec 加密报告文件…")
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        pw_layout = QHBoxLayout()
        pw_layout.addWidget(QLabel("解密密码:"))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.setPlaceholderText("输入报告密码")
        decrypt_btn = QPushButton("解密预览")
        decrypt_btn.clicked.connect(self._decrypt_and_show)
        pw_layout.addWidget(self.pw_edit)
        pw_layout.addWidget(decrypt_btn)
        layout.addLayout(pw_layout)

        self.preview = QTextBrowser()
        layout.addWidget(self.preview)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择加密报告", "", "Encrypted Reports (*.sec);;All Files (*)"
        )
        if path:
            self.file_edit.setText(path)

    def _decrypt_and_show(self):
        path = self.file_edit.text().strip()
        password = self.pw_edit.text()

        if not path or not os.path.isfile(path):
            QMessageBox.warning(self, "错误", "请先选择有效的加密报告文件。")
            return
        if not password:
            QMessageBox.warning(self, "错误", "请输入解密密码。")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                b64 = f.read().strip()
            plaintext = crypto.decrypt(b64, password)
            preview = plaintext[:2000] + ("\n\n…（仅显示前2000字符）" if len(plaintext) > 2000 else "")
            self.preview.setPlainText(preview)
        except Exception:
            QMessageBox.critical(self, "解密失败", "密码错误或文件已损坏，无法解密。")
