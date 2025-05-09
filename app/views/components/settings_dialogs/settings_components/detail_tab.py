# app/views/components/settings_dialogs/settings_components/detail_tab.py
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .settings_section import SettingsSectionComponent
from app.models.common.settings_store import SettingsStore


class DetailTabComponent(BaseTabComponent):
    """상세 설정 탭 컴포넌트"""

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
        title_label = QLabel("Detail Settings")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("Set up the detailed configuration for the optimization process.")
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

        # 저장 경로 섹션
        path_section = SettingsSectionComponent("Save Path")
        path_section.setting_changed.connect(self.on_setting_changed)

        # 저장 경로 설정 항목 추가
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
        line_change_section = SettingsSectionComponent("Line Change")
        line_change_section.setting_changed.connect(self.on_setting_changed)

        # 라인 변경 설정 항목 추가
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
        material_section = SettingsSectionComponent("Material")
        material_section.setting_changed.connect(self.on_setting_changed)

        # 자재 설정 항목 추가
        material_section.add_setting_item(
            "Material Constraint", "mat_use", "checkbox",
            default=bool(SettingsStore.get("mat_use", 0))
        )

        # 라인 할당 섹션
        line_assign_section = SettingsSectionComponent("Line Assign")
        line_assign_section.setting_changed.connect(self.on_setting_changed)

        # 라인 할당 설정 항목 추가
        line_assign_section.add_setting_item(
            "P999 Constraint", "P999_line_ox", "checkbox",
            default=bool(SettingsStore.get("P999_line_ox", 0))
        )

        line_assign_section.add_setting_item(
            "P999 Assign Line", "P999_line", "input",
            default=SettingsStore.get("P999_line", "")
        )

        # 작업률 섹션
        operation_rate_section = SettingsSectionComponent("Operation Rate")
        operation_rate_section.setting_changed.connect(self.on_setting_changed)

        # 작업률 설정 항목 추가
        operation_rate_section.add_setting_item(
            "Apply Shift-Based Weight", "weight_day_ox", "checkbox",
            default=bool(SettingsStore.get("weight_day_ox", 0))
        )

        # shift별 가중치는 리스트 형태로 저장되지만, UI에서 간편하게 보여주기 위해 문자열로 처리
        weight_day = SettingsStore.get("weight_day", [1.0, 1.0, 1.0])
        weight_day_str = ", ".join(map(str, weight_day))

        operation_rate_section.add_setting_item(
            "Shift-Based Weights(Comma-separated)", "weight_day_str", "input",
            default=weight_day_str
        )

        # 섹션 프레임에 모든 섹션 추가
        sections_layout.addWidget(path_section)
        sections_layout.addWidget(line_change_section)
        sections_layout.addWidget(material_section)
        sections_layout.addWidget(line_assign_section)
        sections_layout.addWidget(operation_rate_section)

        # 메모 레이블
        note_label = QLabel("The detailed configuration influences the accurate execution of the optimization algorithm.")
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