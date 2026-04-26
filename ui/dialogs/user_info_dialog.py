from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QLabel
)
from PyQt5.QtCore import Qt


class UserInfoDialog(QDialog):
    """Collect operator info (org / dept / name) before each scan."""

    def __init__(self, parent=None, prefill: dict = None):
        super().__init__(parent)
        self.setWindowTitle("填写被检查人信息")
        self.setMinimumWidth(360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        prefill = prefill or {}
        layout = QVBoxLayout(self)

        hint = QLabel("请填写被检查终端使用人信息，将写入检查报告以确保不可否认性。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #555; margin-bottom: 8px;")
        layout.addWidget(hint)

        form = QFormLayout()
        self.org_edit  = QLineEdit(prefill.get("org", ""))
        self.dept_edit = QLineEdit(prefill.get("dept", ""))
        self.name_edit = QLineEdit(prefill.get("name", ""))

        self.org_edit.setPlaceholderText("例：XX公司 / XX单位")
        self.dept_edit.setPlaceholderText("例：信息安全部")
        self.name_edit.setPlaceholderText("例：张三")

        form.addRow("单位：", self.org_edit)
        form.addRow("部门：", self.dept_edit)
        form.addRow("姓名：", self.name_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确定，开始检查")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_user_info(self) -> dict:
        return {
            "org":  self.org_edit.text().strip(),
            "dept": self.dept_edit.text().strip(),
            "name": self.name_edit.text().strip(),
        }
