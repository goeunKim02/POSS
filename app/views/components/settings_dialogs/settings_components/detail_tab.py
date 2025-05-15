# app/views/components/settings_dialogs/settings_components/detail_tab.py - 모던한 Detail 탭
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QLineEdit, QCheckBox
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

        # Apply Model Changeover Time 체크박스
        apply_changeover_checkbox = line_change_section.add_setting_item(
            "Apply Model Changeover Time", "itemcnt_limit_ox", "checkbox",
            default=bool(SettingsStore.get("itemcnt_limit_ox", 0))
        )

        # Minimum SKU Count 입력 필드
        default_min_sku = SettingsStore.get("itemcnt_limit", 1)
        min_sku_input = line_change_section.add_setting_item(
            "Minimum SKU Count", "itemcnt_limit", "input",
            min=1, max=100, default=default_min_sku
        )

        # Apply Max CNT Limit for I 체크박스
        apply_max_i_checkbox = line_change_section.add_setting_item(
            "Apply Max CNT Limit for I", "itemcnt_limit_max_i_ox", "checkbox",
            default=bool(SettingsStore.get("itemcnt_limit_max_i_ox", 0))
        )

        # Max CNT Limit for I 입력 필드
        default_max_i = SettingsStore.get("itemcnt_limit_max_i", 1)
        max_i_input = line_change_section.add_setting_item(
            "Max CNT Limit for I", "itemcnt_limit_max_i", "input",
            min=1, max=100, default=default_max_i
        )

        # Apply Max CNT Limit for O 체크박스
        apply_max_o_checkbox = line_change_section.add_setting_item(
            "Apply Max CNT Limit for O", "itemcnt_limit_max_o_ox", "checkbox",
            default=bool(SettingsStore.get("itemcnt_limit_max_o_ox", 0))
        )

        # Max CNT Limit for O 입력 필드
        default_max_o = SettingsStore.get("itemcnt_limit_max_o", 1)
        max_o_input = line_change_section.add_setting_item(
            "Max CNT Limit for O", "itemcnt_limit_max_o", "input",
            min=1, max=100, default=default_max_o
        )

        # 체크박스와 입력 필드 연결 (Line Change)
        self._connect_checkbox_to_input(apply_changeover_checkbox, min_sku_input,
                                        default_value=str(default_min_sku))
        self._connect_checkbox_to_input(apply_max_i_checkbox, max_i_input,
                                        default_value=str(default_max_i))
        self._connect_checkbox_to_input(apply_max_o_checkbox, max_o_input,
                                        default_value=str(default_max_o))

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

        # P999 Constraint 체크박스
        p999_checkbox = line_assign_section.add_setting_item(
            "P999 Constraint", "P999_line_ox", "checkbox",
            default=bool(SettingsStore.get("P999_line_ox", 0))
        )

        # P999 Assign Line 입력 필드
        default_p999 = SettingsStore.get("P999_line", "")
        p999_input = line_assign_section.add_setting_item(
            "P999 Assign Line", "P999_line", "input",
            default=default_p999
        )

        # 체크박스와 입력 필드 연결 (Line Assign)
        self._connect_checkbox_to_input(p999_checkbox, p999_input,
                                        default_value=default_p999)

        # 작업률 섹션
        operation_rate_section = ModernSettingsSectionComponent("Operation Rate")
        operation_rate_section.setting_changed.connect(self.on_setting_changed)

        # Apply Shift-Based Weight 체크박스
        shift_weight_checkbox = operation_rate_section.add_setting_item(
            "Apply Shift-Based Weight", "weight_day_ox", "checkbox",
            default=bool(SettingsStore.get("weight_day_ox", 0))
        )

        # shift별 가중치 처리
        weight_day = SettingsStore.get("weight_day", [1.0, 1.0, 1.0])
        weight_day_str = ", ".join(map(str, weight_day))

        # Shift-Based Weights 입력 필드
        shift_weights_input = operation_rate_section.add_setting_item(
            "Shift-Based Weights(Comma-separated)", "weight_day_str", "input",
            default=weight_day_str
        )

        # 체크박스와 입력 필드 연결 (Operation Rate)
        self._connect_checkbox_to_input(shift_weight_checkbox, shift_weights_input,
                                        default_value="1.0, 1.0, 1.0")

        # 섹션 추가
        self.content_layout.addWidget(path_section)
        self.content_layout.addWidget(line_change_section)
        self.content_layout.addWidget(material_section)
        self.content_layout.addWidget(line_assign_section)
        self.content_layout.addWidget(operation_rate_section)

        # 스트레치 추가
        self.content_layout.addStretch(1)

    def _connect_checkbox_to_input(self, checkbox_widget, input_widget, default_value=""):
        """체크박스와 입력 필드를 연결하는 헬퍼 메서드"""
        if isinstance(checkbox_widget, QCheckBox) and isinstance(input_widget, QLineEdit):
            # 초기 상태 설정
            input_widget.setEnabled(checkbox_widget.isChecked())

            # 비활성화 시 스타일 적용
            if not checkbox_widget.isChecked():
                input_widget.setStyleSheet(self._get_disabled_input_style())

            # 기본값 저장
            input_widget.setProperty('default_value', default_value)

            # 체크박스 상태 변경 시 입력 필드 활성/비활성화
            # 체크박스 상태 변경 시 입력 필드 활성/비활성화
            def on_checkbox_state_changed(state):
                is_checked = bool(state)
                input_widget.setEnabled(is_checked)

                # 활성화/비활성화에 따른 스타일 변경
                if is_checked:
                    input_widget.setStyleSheet(self._get_enabled_input_style())
                else:
                    input_widget.setStyleSheet(self._get_disabled_input_style())
                    # 비활성화되어도 값은 그대로 유지

            checkbox_widget.stateChanged.connect(on_checkbox_state_changed)

    def _get_enabled_input_style(self):
        """활성화된 입력 필드 스타일"""
        return """
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: Arial;
            }
            QLineEdit:focus {
                border-color: #1428A0;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
        """

    def _get_disabled_input_style(self):
        """비활성화된 입력 필드 스타일"""
        return """
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                color: #888;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: Arial;
            }
        """

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