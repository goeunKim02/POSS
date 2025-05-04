# help_components/planning_tab.py - 수정된 계획 수립 탭 컴포넌트
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent


class PlanningTabComponent(BaseTabComponent):
    """계획 수립 탭 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 제목 레이블 생성
        title_label = QLabel("사전 할당 결과 사용법")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; padding-bottom: 10px; border-bottom: 2px solid #1428A0;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("이 페이지에서는 초기 계획 결과를 확인하고 조정할 수 있습니다.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 15px; margin-bottom: 15px;")

        # 부제목 레이블
        subtitle_label = QLabel("기능:")
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
            "결과 확인: 테이블에서 사전 할당된 작업들을 확인합니다.",
            "필터링: 헤더를 클릭하여 특정 조건으로 데이터를 필터링합니다.",
            "정렬: 헤더를 클릭하여 오름차순/내림차순 정렬을 적용합니다.",
            "내보내기: 'Export Excel' 버튼을 클릭하여 결과를 엑셀 파일로 저장합니다.",
            "초기화: 'Reset' 버튼을 클릭하여 변경 사항을 초기화합니다."
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

        # 팁 박스
        tip_frame = QFrame()
        tip_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        tip_layout = QVBoxLayout(tip_frame)

        tip_title = QLabel("팁:")
        tip_title.setFont(QFont("Arial", 10, QFont.Bold))
        tip_title.setStyleSheet("color: #1428A0;")

        tip_desc = QLabel("최적의 결과를 얻기 위해 데이터 입력 단계에서 정확한 정보를 제공하는 것이 중요합니다.")
        tip_desc.setWordWrap(True)
        tip_desc.setStyleSheet("font-size: 15px;")

        tip_layout.addWidget(tip_title)
        tip_layout.addWidget(tip_desc)

        # 메인 레이아웃에 위젯 추가
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(desc_label)
        self.content_layout.addWidget(subtitle_label)
        self.content_layout.addWidget(feature_frame)
        self.content_layout.addWidget(tip_frame)
        self.content_layout.addStretch(1)  # 하단 여백용 스트레치 추가