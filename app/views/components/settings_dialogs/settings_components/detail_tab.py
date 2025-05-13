# app/views/components/settings_dialogs/settings_components/detail_tab.py - 모던한 Detail 탭
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .settings_section import ModernSettingsSectionComponent
from app.models.common.settings_store import SettingsStore
from app.resources.fonts.font_manager import font_manager


class ModernDetailTabComponent(BaseTabComponent):
    """모던한 디자인의 상세 설정 탭 컴포넌트"""

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
        title_label = QLabel("Detail Settings")
        title_font = font_manager.get_font("SamsungSharpSans-Bold", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; border: none;")

        header_layout.addWidget(title_label)

        # 컨텐츠에 헤더 추가
        self.content_layout.addWidget(header_frame)

        # 저장 경로 섹션
        path_section = ModernSettingsSectionComponent("Save Path")
        path_section.setting_changed.connect(self.on_setting_changed)

        path_section.add_setting_item(
            "Input Route", "op_InputRoute", "filepath",
            default=SettingsStore.get("op_InputRoute", ""),
            dialog_type="directory"
        )

        path_section.add_setting_item(
            "Result Route", "op_SavingRoute", "filepath",
            default=SettingsStore.get("op_SavingRoute", ""),
            dialog_type="directory"
        )

        # 라인 변경 섹션
        line_change_section = ModernSettingsSectionComponent("Line Change")
        line_change_section.setting_changed.connect(self.on_setting_changed)

        line_change_section.add_setting_item(
            "Apply Model Changeover Time", "itemcnt_limit_ox", "checkbox",
            default=bool(SettingsStore.get("itemcnt_limit_ox", 0))
        )

        line_change_section.add_setting_item(
            "Minimum SKU Count", "itemcnt_limit", "spinbox",
            min=1, max=100, default=SettingsStore.get("itemcnt_limit", 1)
        )

        line_change_section.add_setting_item(
            "Apply Max CNT Limit for I", "itemcnt_limit_max_i_ox", "checkbox",
            default=bool(SettingsStore.get("itemcnt_limit_max_i_ox", 0))
        )

        line_change_section.add_setting_item(
            "Max CNT Limit for I", "itemcnt_limit_max_i", "spinbox",
            min=1, max=100, default=SettingsStore.get("itemcnt_limit_max_i", 1)
        )

        line_change_section.add_setting_item(
            "Apply Max CNT Limit for O", "itemcnt_limit_max_o_ox", "checkbox",
            default=bool(SettingsStore.get("itemcnt_limit_max_o_ox", 0))
        )

        line_change_section.add_setting_item(
            "Max CNT Limit for O", "itemcnt_limit_max_o", "spinbox",
            min=1, max=100, default=SettingsStore.get("itemcnt_limit_max_o", 1)
        )

        # 자재 섹션
        material_section = ModernSettingsSectionComponent("Material")
        material_section.setting_changed.connect(self.on_setting_changed)

        material_section.add_setting_item(
            "Material Constraint", "mat_use", "checkbox",
            default=bool(SettingsStore.get("mat_use", 0))
        )

        # 라인 할당 섹션
        line_assign_section = ModernSettingsSectionComponent("Line Assign")
        line_assign_section.setting_changed.connect(self.on_setting_changed)

        line_assign_section.add_setting_item(
            "P999 Constraint", "P999_line_ox", "checkbox",
            default=bool(SettingsStore.get("P999_line_ox", 0))
        )

        line_assign_section.add_setting_item(
            "P999 Assign Line", "P999_line", "input",
            default=SettingsStore.get("P999_line", "")
        )

        # 작업률 섹션
        operation_rate_section = ModernSettingsSectionComponent("Operation Rate")
        operation_rate_section.setting_changed.connect(self.on_setting_changed)

        operation_rate_section.add_setting_item(
            "Apply Shift-Based Weight", "weight_day_ox", "checkbox",
            default=bool(SettingsStore.get("weight_day_ox", 0))
        )

        # shift별 가중치 처리
        weight_day = SettingsStore.get("weight_day", [1.0, 1.0, 1.0])
        weight_day_str = ", ".join(map(str, weight_day))

        operation_rate_section.add_setting_item(
            "Shift-Based Weights(Comma-separated)", "weight_day_str", "input",
            default=weight_day_str
        )

        # 섹션 추가
        self.content_layout.addWidget(path_section)
        self.content_layout.addWidget(line_change_section)
        self.content_layout.addWidget(material_section)
        self.content_layout.addWidget(line_assign_section)
        self.content_layout.addWidget(operation_rate_section)

        # 스트레치 추가
        self.content_layout.addStretch(1)

    def on_setting_changed(self, key, value):
        """설정 변경 시 호출되는 콜백"""
        # weight_day_str의 경우 리스트로 변환하여 저장
        if key == "weight_day_str":
            try:
                # 쉼표로 구분된 문자열을 리스트로 변환
                value_list = [float(item.strip()) for item in value.split(",")]
                SettingsStore.set("weight_day", value_list)
                self.settings_changed.emit("weight_day", value_list)
            except ValueError:
                # 숫자로 변환할 수 없는 경우 기본값 사용
                print("올바른 숫자 형식이 아닙니다. 기본값을 사용합니다.")
                SettingsStore.set("weight_day", [1.0, 1.0, 1.0])
                self.settings_changed.emit("weight_day", [1.0, 1.0, 1.0])
        else:
            # 일반 설정값 저장
            SettingsStore.set(key, value)
            # 상위 위젯에 변경 사항 전파
            self.settings_changed.emit(key, value)