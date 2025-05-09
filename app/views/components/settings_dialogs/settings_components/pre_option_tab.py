# app/views/components/settings_dialogs/settings_components/pre_option_tab.py
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .settings_section import SettingsSectionComponent
from app.models.common.settings_store import SettingsStore


class PreOptionTabComponent(BaseTabComponent):
    """사전 옵션 탭 컴포넌트"""

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
        title_label = QLabel("Pre-Option Settings")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("Configure the plan retention rate and pre-assignment settings.")
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

        # 계획 유지율 섹션 1
        plan_retention1_section = SettingsSectionComponent("Plan Retention Rate 1")
        plan_retention1_section.setting_changed.connect(self.on_setting_changed)

        # 날짜 선택 옵션 (1~14일)
        days = [str(i) for i in range(1, 15)]

        # 계획 유지율 1 설정 항목 추가
        plan_retention1_section.add_setting_item(
            "Plan Retention Rate 1", "op_timeset_1", "multiselect",
            items=days, default=SettingsStore.get("op_timeset_1", [])
        )

        plan_retention1_section.add_setting_item(
            "SKU Plan Retention Rate 1", "op_SKU_1", "spinbox",
            min=0, max=100, default=SettingsStore.get("op_SKU_1", 100),
            suffix="%"
        )

        plan_retention1_section.add_setting_item(
            "RMC Plan Retention Rate 1", "op_RMC_1", "spinbox",
            min=0, max=100, default=SettingsStore.get("op_RMC_1", 100),
            suffix="%"
        )

        # 계획 유지율 섹션 2
        plan_retention2_section = SettingsSectionComponent("Plan Retention Rate 2")
        plan_retention2_section.setting_changed.connect(self.on_setting_changed)

        # 계획 유지율 2 설정 항목 추가
        plan_retention2_section.add_setting_item(
            "Plan Retention Rate 2", "op_timeset_2", "multiselect",
            items=days, default=SettingsStore.get("op_timeset_2", [])
        )

        plan_retention2_section.add_setting_item(
            "SKU Plan Retention Rate 2", "op_SKU_2", "spinbox",
            min=0, max=100, default=SettingsStore.get("op_SKU_2", 100),
            suffix="%"
        )

        plan_retention2_section.add_setting_item(
            "RMC Plan Retention Rate 2", "op_RMC_2", "spinbox",
            min=0, max=100, default=SettingsStore.get("op_RMC_2", 100),
            suffix="%"
        )

        # 사전 할당 섹션
        pre_allocation_section = SettingsSectionComponent("Pre-Assignment")
        pre_allocation_section.setting_changed.connect(self.on_setting_changed)

        # 사전 할당 설정 항목 추가
        pre_allocation_section.add_setting_item(
            "Apply Pre-Assignment Ratio", "max_min_ratio_ox", "checkbox",
            default=bool(SettingsStore.get("max_min_ratio_ox", 0))
        )

        # 1~50 범위의 숫자 리스트 생성
        margins = [str(i) for i in range(1, 51)]

        pre_allocation_section.add_setting_item(
            "Pre-Assignment Ratio for Primary Execution", "max_min_margin", "combobox",
            items=margins,
            default_index=SettingsStore.get("max_min_margin", 10) - 1  # 인덱스는 0부터 시작하므로 -1
        )

        # 섹션 프레임에 모든 섹션 추가
        sections_layout.addWidget(plan_retention1_section)
        sections_layout.addWidget(plan_retention2_section)
        sections_layout.addWidget(pre_allocation_section)

        # 메모 레이블
        note_label = QLabel("The plan adherence rate is a configuration that ensures continuity with the prior plan.")
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