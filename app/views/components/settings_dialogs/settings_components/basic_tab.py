# app/views/components/settings_dialogs/settings_components/basic_tab.py - 모던한 Basic 탭
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .settings_section import ModernSettingsSectionComponent
from app.models.common.settings_store import SettingsStore
from app.resources.fonts.font_manager import font_manager


class ModernBasicTabComponent(BaseTabComponent):
    """모던한 디자인의 기본 설정 탭 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 헤더 섹션
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding-bottom: 5px;
                border-bottom: 2px solid #1428A0;
            }
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 레이블
        title_label = QLabel("Basic Settings")
        title_font = font_manager.get_font("SamsungSharpSans-Bold", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; border: none;")
        header_layout.addWidget(title_label)

        # 컨텐츠에 헤더 추가
        self.content_layout.addWidget(header_frame)

        # 러닝 타임 섹션 (모던 스타일)
        running_section = ModernSettingsSectionComponent("Running Time")
        running_section.setting_changed.connect(self.on_setting_changed)

        # 러닝 타임 설정 항목 추가
        running_section.add_setting_item(
            "Processing Time(s)", "time_limit", "input",
            min=1, max=86400, default=SettingsStore.get("time_limit", 300),
        )

        # 가중치 섹션 (모던 스타일)
        weight_section = ModernSettingsSectionComponent("Weight")
        weight_section.setting_changed.connect(self.on_setting_changed)

        # 가중치 설정 항목 추가
        weight_section.add_setting_item(
            "SOP Weight", "weight_sop_ox", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_sop_ox", 1.0),
            decimals=4, step=0.0001
        )

        weight_section.add_setting_item(
            "Weight by Material Quantity", "weight_mat_qty", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_mat_qty", 1.0),
            decimals=4, step=0.0001
        )

        weight_section.add_setting_item(
            "Weight Distributed by Project", "weight_linecnt_bypjt", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_linecnt_bypjt", 1.0),
            decimals=4, step=0.0001
        )

        weight_section.add_setting_item(
            "Weight Distributed per Item", "weight_linecnt_byitem", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_linecnt_byitem", 1.0),
            decimals=4, step=0.0001
        )

        weight_section.add_setting_item(
            "Operation Rate Weight", "weight_operation", "doublespinbox",
            min=0.0, max=10.0, default=SettingsStore.get("weight_operation", 1.0),
            decimals=4, step=0.0001
        )

        # 섹션 추가
        self.content_layout.addWidget(running_section)
        self.content_layout.addWidget(weight_section)

        # 스트레치 추가
        self.content_layout.addStretch(1)

    def on_setting_changed(self, key, value):
        """설정 변경 시 호출되는 콜백"""
        # 설정 저장소에 변경사항 저장
        SettingsStore.set(key, value)
        # 상위 위젯에 변경 사항 전파
        self.settings_changed.emit(key, value)