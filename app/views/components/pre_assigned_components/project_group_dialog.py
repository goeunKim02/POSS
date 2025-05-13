from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QDialogButtonBox, QLabel, QFrame, QScrollArea, QWidget, QPushButton
)
from ....resources.styles.pre_assigned_style import (
    DETAIL_DIALOG_STYLE
)


class ProjectGroupDialog(QDialog):
    def __init__(self, project_groups: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(DETAIL_DIALOG_STYLE)
        # 다이얼로그에 ? 버튼 없애는 코드
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Select Project Groups")
        self.setModal(True)
        self.resize(800, 600)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 제목 프레임
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("background-color: #1428A0; border: none;")
        title_frame.setFixedHeight(60)

        # 제목 프레임 레이아웃
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 0, 20, 0)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 제목 레이블
        title_label = QLabel("Select Project Groups")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)

        # 메인 레이아웃에 제목 프레임 추가
        main_layout.addWidget(title_frame)

        # 콘텐츠 영역
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # 설명 레이블 프레임
        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(20, 15, 20, 15)

        desc_label = QLabel("Select the project group to include in the optimization Process")
        desc_font = QFont("Arial", 12, QFont.Bold)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("background-color: transparent; color: #333333; border:none; ")
        desc_layout.addWidget(desc_label)

        content_layout.addWidget(desc_frame)

        # 체크박스 영역
        checkbox_frame = QFrame()
        checkbox_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """)
        checkbox_layout = QVBoxLayout(checkbox_frame)
        checkbox_layout.setContentsMargins(20, 20, 20, 20)
        checkbox_layout.setSpacing(10)

        # 스크롤 영역 (체크박스가 많을 경우 대비)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")

        # 스크롤 컨텐츠 위젯
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        # 체크박스 생성
        self.checkboxes = {}
        for group_id, projects in project_groups.items():
            cb = QCheckBox(f"{', '.join(projects)}")
            cb.setStyleSheet("""
                QCheckBox {
                    font-family: Arial;
                    font-size: 11pt;
                    color: #333333;
                    padding: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox:hover {
                    background-color: #f0f0f0;
                    border-radius: 4px;
                }
            """)
            cb.setChecked(False)
            cb.stateChanged.connect(self._update_ok_button)

            scroll_layout.addWidget(cb)
            self.checkboxes[group_id] = cb

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        checkbox_layout.addWidget(scroll_area)

        content_layout.addWidget(checkbox_frame)
        content_layout.addStretch(1)

        # 스크롤 영역 생성 (전체 콘텐츠)
        main_scroll_area = QScrollArea()
        main_scroll_area.setWidgetResizable(True)
        main_scroll_area.setStyleSheet("background-color: #F9F9F9; border: none;")
        main_scroll_area.setWidget(content_widget)
        main_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 메인 레이아웃에 스크롤 영역 추가
        main_layout.addWidget(main_scroll_area)

        # 버튼 프레임
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #F0F0F0; border: none;")
        button_frame.setFixedHeight(80)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 20, 30, 20)
        button_layout.addStretch(1)

        # OK 버튼
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(100, 40)
        ok_font = QFont("Arial", 11)
        ok_font.setBold(True)
        self.ok_button.setFont(ok_font)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                border: none;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1e429f;
            }
            QPushButton:disabled {
                background-color: #ACACAC;
                color: white;
            }
        """)
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self.accept)

        # Cancel 버튼
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(100, 40)
        cancel_font = QFont("Arial", 11)
        cancel_font.setBold(True)
        self.cancel_button.setFont(cancel_font)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                border: none;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #545B62;
            }
        """)
        self.cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addSpacing(15)
        button_layout.addWidget(self.cancel_button)

        # 메인 레이아웃에 버튼 프레임 추가
        main_layout.addWidget(button_frame)

    def _update_ok_button(self):
        # 체크된 항목에 따른 버튼 활성화
        any_checked = any(cb.isChecked() for cb in self.checkboxes.values())
        self.ok_button.setEnabled(any_checked)

        # 활성화 상태에 따른 커서 설정
        if any_checked:
            self.ok_button.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            self.ok_button.setCursor(Qt.ArrowCursor)

    def selected_groups(self):
        # 사용자가 선택한 프로젝트 그룹 리스트
        return [gid for gid, cb in self.checkboxes.items() if cb.isChecked()]