# help_dialog.py - 메인 다이얼로그 클래스
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QFrame
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt, QFile, QTextStream

# 분리된 탭 컴포넌트 import
from app.views.components.help_dialogs import (
    OverviewTabComponent,
    DataInputTabComponent,
    PlanningTabComponent,
    ResultTabComponent
)


class HelpDialog(QDialog):
    """도움말 다이얼로그 창"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Samsung Production Planning Optimization System")
        self.resize(1200, 800)
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 레이블
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("background-color: #1428A0; border: none;")
        title_frame.setFixedHeight(40)

        # 프레임 레이아웃 생성
        title_frame_layout = QVBoxLayout(title_frame)
        title_frame_layout.setContentsMargins(10, 0, 10, 0)
        title_frame_layout.setAlignment(Qt.AlignCenter)

        # 제목 레이블 생성
        title_label = QLabel("Help Guide")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")  # 텍스트 색상 설정

        # 레이아웃에 레이블 추가
        title_frame_layout.addWidget(title_label)

        # 메인 레이아웃에 프레임 추가
        main_layout.addWidget(title_frame)

        # 탭 위젯 생성
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("margin-left: 10px;")

        # 분리된 컴포넌트 추가
        overview_tab = OverviewTabComponent()
        data_input_tab = DataInputTabComponent()
        planning_tab = PlanningTabComponent()
        result_tab = ResultTabComponent()

        # 탭 추가
        tab_widget.addTab(overview_tab, "OverView")
        tab_widget.addTab(data_input_tab, "Data Input")
        tab_widget.addTab(planning_tab, "Pre-Assigned")
        tab_widget.addTab(result_tab, "Results")

        # 버튼 레이아웃
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #F0F0F0; border: none;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 30, 10)

        close_button = QPushButton("Close")
        close_button_font = QFont("Arial", 10)
        close_button_font.setBold(True)
        close_button.setFont(close_button_font)
        close_button.setStyleSheet("""
        QPushButton {
            background-color: #1428A0;
            border: none;
            color: white;
            border-radius: 10px;
            width: 130px;
            height: 50px;
        }
        QPushButton:hover {
            background-color: #228B22;
            border: none;
            color: yellow;
        }
        """)
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.clicked.connect(self.accept)  # 다이얼로그 닫기

        button_layout.addStretch(1)
        button_layout.addWidget(close_button)

        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(tab_widget)
        main_layout.addWidget(button_frame)  # addLayout에서 addWidget으로 수정