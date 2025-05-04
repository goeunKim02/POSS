# help_components/overview_tab.py - 수정된 개요 탭 컴포넌트
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent


class OverviewTabComponent(BaseTabComponent):
    """개요 탭 컴포넌트"""

    def __init__(self, parent=None):
        # 부모 클래스에 css_path 전달 (더 이상 사용하지 않지만 호환성 유지)
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 제목 레이블 생성
        title_label = QLabel("Samsung Production Planning Optimization System")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; padding-bottom: 10px; border-bottom: 2px solid #1428A0;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("이 시스템은 삼성전자의 생산 계획을 최적화하기 위한 도구입니다.")
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
            "생산 데이터 분석",
            "최적 생산 계획 수립",
            "리소스 할당 최적화",
            "결과 시각화 및 분석"
        ]

        for feature in features:
            feature_label = QLabel("• " + feature)
            feature_label.setStyleSheet("font-size: 15px; line-height: 1.4;")
            feature_layout.addWidget(feature_label)

        # 메모 레이블
        note_label = QLabel("자세한 내용은 각 탭을 참조하세요.")
        note_label.setStyleSheet("font-style: italic; color: #666; margin-top: 20px;")

        # 메인 레이아웃에 위젯 추가
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(desc_label)
        self.content_layout.addWidget(subtitle_label)
        self.content_layout.addWidget(feature_frame)
        self.content_layout.addWidget(note_label)
        self.content_layout.addStretch(1)  # 하단 여백용 스트레치 추가