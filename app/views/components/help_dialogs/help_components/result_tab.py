# help_components/result_tab.py - 수정된 결과 분석 탭 컴포넌트
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent


class ResultTabComponent(BaseTabComponent):
    """결과 분석 탭 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 제목 레이블 생성
        title_label = QLabel("결과 분석 사용법")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; padding-bottom: 10px; border-bottom: 2px solid #1428A0;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("이 페이지에서는 최적화 결과를 분석하고 시각화할 수 있습니다.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 15px; margin-bottom: 15px;")

        # 부제목 레이블
        subtitle_label = QLabel("주요 기능:")
        subtitle_font = QFont("Arial", 10)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #1428A0; margin-top: 15px;")

        # 기능 목록을 담을 프레임
        feature_frame = QFrame()
        feature_layout = QVBoxLayout(feature_frame)
        feature_layout.setContentsMargins(20, 5, 5, 5)
        feature_layout.setSpacing(8)

        # 기능 항목 추가
        features = [
            "결과 테이블: 왼쪽 패널에서 상세 결과를 확인합니다.",
            "시각화: 오른쪽 패널에서 다양한 그래프를 통해 결과를 시각적으로 확인합니다.",
            "데이터 내보내기: 'Export' 버튼을 클릭하여 결과를 CSV 파일로 저장합니다.",
            "보고서 생성: 'Report' 버튼을 클릭하여 보고서를 생성합니다."
        ]

        for feature in features:
            feature_content = feature.split(": ")
            feature_label = QLabel()
            feature_label.setText(
                f"• <span style='background-color: #FFFFCC; padding: 2px 4px; border-radius: 3px;'>{feature_content[0]}</span>: {feature_content[1]}")
            feature_label.setTextFormat(Qt.RichText)
            feature_label.setWordWrap(True)
            feature_label.setStyleSheet("font-size: 15px; line-height: 1.4;")
            feature_layout.addWidget(feature_label)

        # 시각화 유형 박스
        viz_frame = QFrame()
        viz_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        viz_layout = QVBoxLayout(viz_frame)

        viz_title = QLabel("시각화 유형:")
        viz_title.setFont(QFont("Arial", 10, QFont.Bold))
        viz_title.setStyleSheet("color: #1428A0;")

        # 버튼 컨테이너
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 5, 0, 5)
        buttons_layout.setSpacing(10)

        # 버튼 스타일 시각화
        button_types = ["Capa", "Utilization", "PortCapa", "Plan"]
        for btn_text in button_types:
            btn_label = QLabel(btn_text)
            btn_label.setAlignment(Qt.AlignCenter)
            btn_label.setStyleSheet("""
                background-color: #1428A0;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            """)
            btn_label.setFixedHeight(30)
            buttons_layout.addWidget(btn_label)

        buttons_layout.addStretch(1)  # 오른쪽 정렬

        viz_desc = QLabel("각 버튼을 클릭하여 해당 유형의 시각화를 확인할 수 있습니다.")
        viz_desc.setWordWrap(True)
        viz_desc.setStyleSheet("font-size: 15px; margin-top: 5px;")

        viz_layout.addWidget(viz_title)
        viz_layout.addWidget(buttons_frame)
        viz_layout.addWidget(viz_desc)

        # 참고 사항
        note_label = QLabel("시각화 패널에서 각 버튼을 클릭하여 다른 유형의 데이터를 확인할 수 있습니다.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-style: italic; color: #666; margin-top: 20px;")

        # 메인 레이아웃에 위젯 추가
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(desc_label)
        self.content_layout.addWidget(subtitle_label)
        self.content_layout.addWidget(feature_frame)
        self.content_layout.addWidget(viz_frame)
        self.content_layout.addWidget(note_label)
        self.content_layout.addStretch(1)  # 하단 여백용 스트레치 추가