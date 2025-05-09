# app/views/components/settings_dialogs/settings_components/basic_tab.py
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .settings_section import SettingsSectionComponent
from app.models.common.settings_store import SettingsStore


class BasicTabComponent(BaseTabComponent):
    """기본 설정 탭 컴포넌트"""

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
        title_label = QLabel("기본 설정")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("최적화 프로세스의 기본 설정을 구성하세요.")
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

        # 러닝 타임 섹션
        running_section = SettingsSectionComponent("Running Time")
        running_section.setting_changed.connect(self.on_setting_changed)

        # 러닝 타임 설정 항목 추가
        running_section.add_setting_item(
            "수행시간 (초)", "time_limit", "spinbox",
            min=1, max=86400, default=SettingsStore.get("time_limit", 3600),
            suffix="초"
        )

        # 가중치 섹션
        weight_section = SettingsSectionComponent("Weight")
        weight_section.setting_changed.connect(self.on_setting_changed)

        # 가중치 설정 항목 추가
        weight_section.add_setting_item(
            "SOP 가중치", "weight_sop_ox", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_sop_ox", 1.0),
            decimals=2, step=0.1
        )

        weight_section.add_setting_item(
            "자재 가중치", "weight_mat_qty", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_mat_qty", 1.0),
            decimals=2, step=0.1
        )

        weight_section.add_setting_item(
            "PJT분산 가중치", "weight_linecnt_bypjt", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_linecnt_bypjt", 1.0),
            decimals=2, step=0.1
        )

        weight_section.add_setting_item(
            "Item분산 가중치", "weight_linecnt_byitem", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_linecnt_byitem", 1.0),
            decimals=2, step=0.1
        )

        weight_section.add_setting_item(
            "가동률 가중치", "weight_operation", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_operation", 1.0),
            decimals=2, step=0.1
        )

        # 섹션 프레임에 모든 섹션 추가
        sections_layout.addWidget(running_section)
        sections_layout.addWidget(weight_section)

        # 메모 레이블
        note_label = QLabel("가중치는 최적화 알고리즘이 각 목표의 중요도를 결정하는 데 사용됩니다.")
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

    def on_setting_changed(self, key, value):
        """설정 변경 시 호출되는 콜백"""
        # 설정 저장소에 변경사항 저장
        SettingsStore.set(key, value)
        # 상위 위젯에 변경 사항 전파
        self.settings_changed.emit(key, value)