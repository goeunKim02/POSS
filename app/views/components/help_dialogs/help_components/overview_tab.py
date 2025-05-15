from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from .base_tab import BaseTabComponent


"""
개요 탭 컴포넌트
"""
class OverviewTabComponent(BaseTabComponent):

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
        title_label = QLabel("Samsung Production Planning Optimization System")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("This system is a tool designed to optimize Samsung Electronics' production planning.")
        desc_label.setWordWrap(True)
        desc_font = QFont("Arial", 11)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("margin-bottom: 15px; background-color: transparent; border:none;")

        # 부제목 레이블
        subtitle_label = QLabel("Main Function:")
        subtitle_font = QFont("Arial", 10)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #1428A0; margin-top: 15px; background-color: transparent; border:none;")

        # 기능 목록을 담을 프레임
        feature_frame = QFrame()
        feature_frame.setStyleSheet("background-color: transparent; border:none; margin-top: 0px;")
        feature_layout = QVBoxLayout(feature_frame)
        feature_layout.setContentsMargins(10, 0, 0, 0)
        feature_layout.setSpacing(1)

        # 기능 항목
        features = [
            "Production Data Analysis",
            "Optimal Production Planning",
            "Real-time Modification and Update of the Production Plan",
            "Data visualization and result analysis"
        ]

        for feature in features:
            feature_label = QLabel("• " + feature)
            feature_label.setStyleSheet("font-family: Arial; font-size: 20px; line-height: 1.4; background-color: transparent; border:none;")
            feature_layout.addWidget(feature_label)

        # 메모 레이블
        note_label = QLabel("Please refer to the respective tabs for detailed information.")
        note_label.setStyleSheet("font-family:Arial; color: #666; margin-top: 20px; background-color: transparent; border:none;")

        # 프레임 레이아웃
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(desc_label)
        frame_layout.addWidget(subtitle_label)
        frame_layout.addWidget(feature_frame)
        frame_layout.addWidget(note_label)
        frame_layout.addStretch(1)

        self.content_layout.addWidget(self.content_frame)