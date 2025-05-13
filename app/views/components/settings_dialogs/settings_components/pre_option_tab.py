# app/views/components/settings_dialogs/settings_components/pre_option_tab.py - 모던한 Pre-Option 탭
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .settings_section import ModernSettingsSectionComponent
from app.models.common.settings_store import SettingsStore
from app.resources.fonts.font_manager import font_manager


class ModernPreOptionTabComponent(BaseTabComponent):
    """모던한 디자인의 사전 옵션 탭 컴포넌트"""

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
        header_layout.setSpacing(8)

        # 제목 레이블
        title_label = QLabel("Pre-Option Settings")
        title_font = font_manager.get_font("SamsungSharpSans-Bold", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; border: none;")
        header_layout.addWidget(title_label)

        # 컨텐츠에 헤더 추가
        self.content_layout.addWidget(header_frame)

        # 날짜 선택 옵션 (1~14일)
        days = [str(i) for i in range(1, 15)]

        # 계획 유지율 섹션 1
        plan_retention1_section = ModernSettingsSectionComponent("Plan Retention Rate 1")
        plan_retention1_section.setting_changed.connect(self.on_setting_changed)

        # 버튼 그룹으로 변경
        plan_retention1_section.add_setting_item(
            "Plan Retention Rate 1", "op_timeset_1", "button_group",
            items=days, default=SettingsStore.get("op_timeset_1", []),
            columns=7  # 7열로 표시
        )

        plan_retention1_section.add_setting_item(
            "SKU Plan Retention Rate 1", "op_SKU_1", "input",
            min=0, max=100, default=SettingsStore.get("op_SKU_1", 100),
            suffix="%"
        )

        plan_retention1_section.add_setting_item(
            "RMC Plan Retention Rate 1", "op_RMC_1", "input",
            min=0, max=100, default=SettingsStore.get("op_RMC_1", 100),
            suffix="%"
        )

        # 계획 유지율 섹션 2
        plan_retention2_section = ModernSettingsSectionComponent("Plan Retention Rate 2")
        plan_retention2_section.setting_changed.connect(self.on_setting_changed)

        # 버튼 그룹으로 변경
        plan_retention2_section.add_setting_item(
            "Plan Retention Rate 2", "op_timeset_2", "button_group",
            items=days, default=SettingsStore.get("op_timeset_2", []),
            columns=7  # 7열로 표시
        )

        plan_retention2_section.add_setting_item(
            "SKU Plan Retention Rate 2", "op_SKU_2", "input",
            min=0, max=100, default=SettingsStore.get("op_SKU_2", 100),
            suffix="%"
        )

        plan_retention2_section.add_setting_item(
            "RMC Plan Retention Rate 2", "op_RMC_2", "input",
            min=0, max=100, default=SettingsStore.get("op_RMC_2", 100),
            suffix="%"
        )

        # 사전 할당 섹션
        pre_allocation_section = ModernSettingsSectionComponent("Pre-Assignment")
        pre_allocation_section.setting_changed.connect(self.on_setting_changed)

        pre_allocation_section.add_setting_item(
            "Apply Pre-Assignment Ratio", "max_min_ratio_ox", "checkbox",
            default=bool(SettingsStore.get("max_min_ratio_ox", 0))
        )

        # 1~50 범위의 숫자 리스트 생성
        margins = [str(i) for i in range(1, 51)]

        pre_allocation_section.add_setting_item(
            "Pre-Assignment Ratio for Primary Execution", "max_min_margin", "combobox",
            items=margins,
            default_index=SettingsStore.get("max_min_margin", 10) - 1
        )

        # 섹션 추가
        self.content_layout.addWidget(plan_retention1_section)
        self.content_layout.addWidget(plan_retention2_section)
        self.content_layout.addWidget(pre_allocation_section)

        # 스트레치 추가
        self.content_layout.addStretch(1)

    def on_setting_changed(self, key, value):
        """설정 변경 시 호출되는 콜백"""
        # 설정 저장소에 변경사항 저장
        SettingsStore.set(key, value)
        # 상위 위젯에 변경 사항 전파
        self.settings_changed.emit(key, value)