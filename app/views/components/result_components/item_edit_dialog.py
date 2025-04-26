from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QDialogButtonBox, QLabel, QSpinBox,
                             QComboBox, QHBoxLayout, QMessageBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator
import pandas as pd


class ItemEditDialog(QDialog):
    """아이템 정보 수정 다이얼로그"""

    # 아이템 정보가 수정되었을 때 발생하는 시그널 (변경된 데이터, 필드별 변경 정보)
    itemDataChanged = pyqtSignal(dict, dict)

    def __init__(self, item_data=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data or {}
        self.original_data = self.item_data.copy() if item_data else {}
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("아이템 정보 수정")
        self.setMinimumWidth(600)
        self.setMinimumHeight(300)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # 제목 레이블
        title_label = QLabel("Edit Status")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1428A0; margin-bottom: 10px; border:none; ")
        main_layout.addWidget(title_label)

        # 폼 레이아웃 (입력 필드 컨테이너)
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)

        # 중요 필드를 먼저 정의 (Line, Time, Item, MFG)
        self.important_fields = ['Line', 'Time', 'Item', 'MFG']
        self.field_widgets = {}

        # 중요 필드부터 생성
        for field in self.important_fields:
            if field in self.item_data:
                self._create_field_widget(field, form_layout)

        # 나머지 필드 생성
        for field, value in self.item_data.items():
            # 이미 생성된 중요 필드는 건너뛰기
            if field not in self.important_fields:
                self._create_field_widget(field, form_layout)

        main_layout.addLayout(form_layout)

        # 버튼 박스
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet(
            """
            QDialogButtonBox {
            background-color: #1428A0; padding: 4px;
            }
            """
        )
        button_box.accepted.connect(self.accept_changes)
        button_box.rejected.connect(self.reject)

        main_layout.addWidget(button_box)

    def _create_field_widget(self, field, layout):
        """필드에 맞는 위젯 생성"""
        value = self.item_data.get(field)
        value_str = str(value) if pd.notna(value) else ""

        # 필드 타입에 따른 위젯 생성
        widget = None

        # Line 필드인 경우 (콤보박스)
        if field == 'Line':
            widget = QComboBox()
            # 기본값 추가 (1~5 라인 예시)
            for i in range(1, 6):
                widget.addItem(f"Line {i}")
            # 현재 값 설정
            if value_str:
                index = widget.findText(value_str)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    widget.addItem(value_str)
                    widget.setCurrentText(value_str)

        # Time 필드인 경우 (스핀박스)
        elif field == 'Time':
            widget = QSpinBox()
            widget.setMinimum(1)
            widget.setMaximum(14)  # 예: 1~14 시간대
            if value_str.isdigit():
                widget.setValue(int(value_str))

        # MFG 필드인 경우 (직접 입력과 스핀박스 모두 제공)
        elif field == 'MFG':
            # 컨테이너 위젯 생성
            container = QWidget()
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(0, 0, 0, 0)

            # 직접 입력 필드 생성
            line_edit = QLineEdit(value_str)
            line_edit.setPlaceholderText("직접 입력")
            # 숫자만 입력 가능하도록 설정
            validator = QIntValidator(0, 9999999)
            line_edit.setValidator(validator)

            # 스타일 설정
            line_edit.setStyleSheet("""
                QLineEdit {
                    padding: 4px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
            """)

            hbox.addWidget(line_edit)

            # 위젯 저장 및 폼에 추가
            self.field_widgets[field] = line_edit
            layout.addRow(f"{field}:", container)

            return line_edit

        # 기본 텍스트 필드
        else:
            widget = QLineEdit(value_str)

        # 위젯 저장 및 폼에 추가
        self.field_widgets[field] = widget
        layout.addRow(f"{field}:", widget)

        return widget

    def accept_changes(self):
        """변경 사항 적용"""
        try:
            # 수정된 데이터 수집
            updated_data = {}

            for field, widget in self.field_widgets.items():
                # 위젯 타입에 따라 값 가져오기
                if isinstance(widget, QLineEdit):
                    updated_data[field] = widget.text()
                elif isinstance(widget, QSpinBox):
                    updated_data[field] = str(widget.value())
                elif isinstance(widget, QComboBox):
                    updated_data[field] = widget.currentText()

            # 변경 사항이 있는지 확인하고 변경된 필드 정보 수집
            changes_made = False
            changed_fields = {}

            for field, value in updated_data.items():
                original = str(self.original_data.get(field, ''))
                if value != original:
                    changes_made = True
                    # 변경된 필드 정보 저장 (원래 값과 새 값)
                    changed_fields[field] = {'from': original, 'to': value}

            if changes_made:
                # 변경 사항이 있으면 시그널 발생 (변경된 필드 정보 포함)
                self.item_data.update(updated_data)
                self.itemDataChanged.emit(self.item_data, changed_fields)

            # 다이얼로그 닫기
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"데이터 업데이트 중 오류가 발생했습니다: {str(e)}")