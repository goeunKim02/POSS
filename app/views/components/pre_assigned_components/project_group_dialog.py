from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QDialogButtonBox, QLabel, QFrame
)
from ....resources.styles.pre_assigned_style import (
    DETAIL_DIALOG_STYLE,
    DETAIL_LABEL_TRANSPARENT,
    DETAIL_FRAME_TRANSPARENT,
    DETAIL_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE
)

class ProjectGroupDialog(QDialog):
    def __init__(self, project_groups: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(DETAIL_DIALOG_STYLE)
        self.setWindowTitle("Select Project Groups")
        self.resize(450, 400)

        layout = QVBoxLayout(self)

        # 설명 레이블
        lbl = QLabel("최적화에 포함할 프로젝트 그룹을 선택하세요:")
        lbl.setStyleSheet(DETAIL_LABEL_TRANSPARENT)
        layout.addWidget(lbl)

        # 체크박스 생성
        self.checkboxes = {}
        for group_id, projects in project_groups.items():
            frame = QFrame()
            frame.setStyleSheet(DETAIL_FRAME_TRANSPARENT)
            hbox = QHBoxLayout(frame)

            cb = QCheckBox(f"{', '.join(projects)}")
            cb.setStyleSheet(DETAIL_LABEL_TRANSPARENT)
            cb.setChecked(False)
            # 상태 변경될 때마다 OK 버튼 상태 업데이트
            cb.stateChanged.connect(self._update_ok_button)

            hbox.addWidget(cb)
            layout.addWidget(frame)
            self.checkboxes[group_id] = cb

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = self.btn_box.button(QDialogButtonBox.Ok)
        cancel_btn = self.btn_box.button(QDialogButtonBox.Cancel)

        ok_btn.setStyleSheet(DETAIL_BUTTON_STYLE)
        cancel_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        
        ok_btn.setEnabled(False)

        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addWidget(self.btn_box)

    def _update_ok_button(self):
        # 체크된 항목에 따른 버튼 활성화
        any_checked = any(cb.isChecked() for cb in self.checkboxes.values())
        self.btn_box.button(QDialogButtonBox.Ok).setEnabled(any_checked)

    def selected_groups(self):
        # 사용자가 선택한 프로젝트 그룹 리스트
        return [gid for gid, cb in self.checkboxes.items() if cb.isChecked()]
