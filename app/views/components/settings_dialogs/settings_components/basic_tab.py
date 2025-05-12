# app/views/components/settings_dialogs/settings_components/basic_tab.py
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout
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
        frame_layout.setSpacing(5)

        # 제목 프레임 생성
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: transparent; border: none; border-bottom: 2px solid #1428A0; padding-bottom: 5px;")
        title_frame_layout = QHBoxLayout(title_frame)
        title_frame_layout.setContentsMargins(0, 0, 0, 0)
        title_frame_layout.setSpacing(5)

        # 제목 레이블 생성
        title_label = QLabel("Basic Settings")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; border: none; background-color: transparent;")
        title_label.setMinimumHeight(30)

        # 설명 레이블 - 제목 옆에 작게 표시
        desc_label = QLabel("Set up the default configuration for the optimization process.")
        desc_label.setWordWrap(False)  # 한 줄로 표시
        desc_font = QFont("Arial", 10)  # 폰트 크기 작게
        desc_font.setItalic(True)  # 이탤릭체로 표시
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666666; background-color: transparent; border:none;")
        desc_label.setAlignment(Qt.AlignBottom)  # 하단 정렬

        # 제목 프레임에 레이블들 추가
        title_frame_layout.addWidget(title_label)
        title_frame_layout.addWidget(desc_label)
        title_frame_layout.addStretch()  # 나머지 공간을 채우기 위한 스트레치

        # 섹션들을 담을 프레임
        sections_frame = QFrame()
        sections_frame.setStyleSheet("background-color: transparent; border:none;")
        sections_layout = QVBoxLayout(sections_frame)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(0)  # 섹션간 간격

        # 러닝 타임 섹션
        running_section = SettingsSectionComponent("Running Time")
        running_section.setting_changed.connect(self.on_setting_changed)

        # 러닝 타임 설정 항목 추가
        running_section.add_setting_item(
            "Processing Time(s)", "time_limit", "input",
            min=1, max=86400, default=SettingsStore.get("time_limit", 300),
        )

        # 가중치 섹션
        weight_section = SettingsSectionComponent("Weight")
        weight_section.setting_changed.connect(self.on_setting_changed)

        # 가중치 설정 항목 추가
        weight_section.add_setting_item(
            "SOP Weight", "weight_sop_ox", "input",
            min=0.0, max=10.0, default=SettingsStore.get("weight_sop_ox", 1.0),
            decimals=3, step=0.01
        )

        weight_section.add_setting_item(
            "Weight by Material Quantity", "weight_mat_qty", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_mat_qty", 1.0),
            decimals=3, step=0.01
        )

        weight_section.add_setting_item(
            "Weight Distributed by Project", "weight_linecnt_bypjt", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_linecnt_bypjt", 1.0),
            decimals=3, step=0.01
        )

        weight_section.add_setting_item(
            "Weight Distributed per Item", "weight_linecnt_byitem", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_linecnt_byitem", 1.0),
            decimals=3, step=0.01
        )

        weight_section.add_setting_item(
            "Operation Rate Weight", "weight_operation", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_operation", 1.0),
            decimals=3, step=0.01
        )

        # 섹션 프레임에 모든 섹션 추가
        sections_layout.addWidget(running_section)
        sections_layout.addWidget(weight_section)

        # 메모 레이블
        note_label = QLabel("Weights are utilized by the optimization algorithm to assess the priority of each objective.")
        note_label.setStyleSheet(
            "font-style: italic; color: #666; margin-top: 20px; background-color: transparent; border:none;")

        # 프레임 레이아웃에 위젯 추가
        frame_layout.addWidget(title_frame)  # 제목 프레임 추가
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