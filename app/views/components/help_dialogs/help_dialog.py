# help_dialog.py - 메인 다이얼로그 클래스
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

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
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 제목 레이블
        title_label = QLabel("Help Guide")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # 탭 위젯 생성
        tab_widget = QTabWidget()

        # 분리된 컴포넌트 추가
        overview_tab = OverviewTabComponent()
        data_input_tab = DataInputTabComponent()
        planning_tab = PlanningTabComponent()
        result_tab = ResultTabComponent()

        # 탭 추가
        tab_widget.addTab(overview_tab, "개요")
        tab_widget.addTab(data_input_tab, "데이터 입력")
        tab_widget.addTab(planning_tab, "계획 수립")
        tab_widget.addTab(result_tab, "결과 분석")

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)  # 다이얼로그 닫기
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)

        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(title_label)
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)