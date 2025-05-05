# help_components/planning_tab.py - 수정된 계획 수립 탭 컴포넌트
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .help_section_component import HelpSectionComponent


class PlanningTabComponent(BaseTabComponent):
    """계획 수립 탭 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 콘텐츠 프레임 생성
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #F9F9F9;
                border-radius: 10px;
                border: 1px solid #cccccc;
                margin: 10px;
            }
        """)

        # 콘텐츠 프레임 레이아웃 생성
        frame_layout = QVBoxLayout(self.content_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)

        # 제목 레이블 생성
        title_label = QLabel("Pre-Assigned Result")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("This page allows you to review the pre-assigned results.")
        desc_label.setWordWrap(True)
        desc_font = QFont("Arial", 11)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("margin-bottom: 15px; background-color: transparent; border:none;")

        # 섹션들을 담을 프레임
        sections_frame = QFrame()
        sections_frame.setStyleSheet("background-color: transparent; border:none;")
        sections_layout = QVBoxLayout(sections_frame)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(15)  # 섹션간 간격

        # 기능 섹션
        features_section = HelpSectionComponent(
            number=1,
            title="Features",
            description="The pre-assigned result page provides several key functions:"
        )

        # 기능 항목 추가
        features_section.add_list_item("Results Verification: Check the pre-assigned tasks in the table.")
        features_section.add_list_item("Filtering: Click on headers to filter data by specific conditions.")
        features_section.add_list_item("Sorting: Click on headers to apply ascending/descending sorting.")
        features_section.add_list_item("Exporting: Click 'Export Excel' button to save results as an Excel file.")
        features_section.add_list_item("Reset: Click 'Reset' button to revert any changes.")

        # 팁 섹션
        tips_section = HelpSectionComponent(
            number=2,
            title="Tips",
            description="Providing accurate information during the data input stage is essential for obtaining optimal results."
        )

        # 섹션 프레임에 모든 섹션 추가
        sections_layout.addWidget(features_section)
        sections_layout.addWidget(tips_section)

        # 메모 레이블
        note_label = QLabel(
            "Review the pre-assigned results carefully before proceeding to the final optimization step.")
        note_label.setStyleSheet(
            "font-style: italic; color: #666; margin-top: 20px; background-color: transparent; border:none;")

        # 프레임 레이아웃에 위젯 추가
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(desc_label)
        frame_layout.addWidget(sections_frame)
        frame_layout.addWidget(note_label)
        frame_layout.addStretch(1)  # 하단 여백용 스트레치 추가

        # 메인 레이아웃에 콘텐츠 프레임 추가
        self.content_layout.addWidget(self.content_frame)