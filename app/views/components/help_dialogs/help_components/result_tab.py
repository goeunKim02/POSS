from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .help_section_component import HelpSectionComponent


"""
결과 분석 탭 컴포넌트
"""
class ResultTabComponent(BaseTabComponent):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    """
    콘텐츠 초기화
    """
    def init_content(self):
        # 콘텐츠 프레임
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #F9F9F9;
                border-radius: 10px;
                border: 1px solid #cccccc;
                margin: 10px;
            }
        """)

        # 콘텐츠 프레임 레이아웃
        frame_layout = QVBoxLayout(self.content_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)

        # 제목 레이블
        title_label = QLabel("Results Analysis")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("This page allows you to analyze and visualize the optimization results.")
        desc_label.setWordWrap(True)
        desc_font = QFont("Arial", 11)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("margin-bottom: 15px; background-color: transparent; border:none;")

        # 섹션들을 담을 프레임
        sections_frame = QFrame()
        sections_frame.setStyleSheet("background-color: transparent; border:none;")
        sections_layout = QVBoxLayout(sections_frame)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(15)

        # 주요 기능 섹션
        features_section = HelpSectionComponent(
            number=1,
            title="Main Features",
            description="The Results page offers several function for analysis:"
        )

        # 기능 항목
        features_section.add_list_item("Results Table: View detailed results in the left panel.")
        features_section.add_list_item("Visualization: View results graphically in the right panel.")
        features_section.add_list_item("Modified Data: Dates can be modified via drag-and-drop, and the changes are reflected in real time.")
        features_section.add_list_item("Export Data: Click the 'Export' button to save results as a Excel file.")

        # 시각화 유형 섹션
        viz_section = HelpSectionComponent(
            number=2,
            title="Visualization Types",
            description="You can access different visualization types by clicking the corresponding buttons:"
        )

        # 버튼 컨테이너
        buttons_container = QFrame()
        buttons_container.setStyleSheet("""
            background-color: #F5F5F5; 
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 5px;
        """)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        buttons_layout.setSpacing(15)

        # 버튼 스타일
        button_types = ["Capa", "Utilization", "PortCapa", "Plan"]

        for btn_text in button_types:
            btn_label = QLabel(btn_text)
            btn_label.setAlignment(Qt.AlignCenter)
            btn_label.setMinimumSize(100, 35)
            btn_label.setStyleSheet("""
                background-color: #1428A0;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-family: Arial;
                border: 1px solid #0D1B6D;
            """)
            buttons_layout.addWidget(btn_label)

        buttons_layout.addStretch(1)

        # 버튼 설명
        button_desc = QLabel("Click each button to view different types of visualizations.")
        button_desc.setWordWrap(True)
        button_desc.setStyleSheet("font-size: 9pt; font-family: Arial; margin-top: 5px; border: none;")

        viz_widget = QWidget()
        viz_widget.setObjectName("viz_container")
        viz_widget.setStyleSheet("border: none; background-color: transparent;")
        viz_layout = QVBoxLayout(viz_widget)
        viz_layout.setContentsMargins(20, 5, 5, 5)
        viz_layout.setSpacing(5)

        viz_layout.addWidget(buttons_container)
        viz_layout.addWidget(button_desc)

        viz_section.text_widget.layout().addWidget(viz_widget)

        sections_layout.addWidget(features_section)
        sections_layout.addWidget(viz_section)

        # 메모 레이블
        note_label = QLabel(
            "Switch between visualization types to gain comprehensive insights into your optimization results.")
        note_label.setStyleSheet(
            "font-family: Arial; color: #666; margin-top: 20px; background-color: transparent; border:none;")

        frame_layout.addWidget(title_label)
        frame_layout.addWidget(desc_label)
        frame_layout.addWidget(sections_frame)
        frame_layout.addWidget(note_label)
        frame_layout.addStretch(1)

        self.content_layout.addWidget(self.content_frame)