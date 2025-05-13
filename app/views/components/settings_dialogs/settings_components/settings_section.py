# app/views/components/settings_dialogs/settings_components/settings_section.py - 모던한 설정 섹션
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QComboBox, QPushButton, QFileDialog, QWidget, QHBoxLayout,
                             QGraphicsDropShadowEffect, QGridLayout)
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt, pyqtSignal


class ModernSettingsSectionComponent(QFrame):
    """모던하게 디자인된 설정 섹션 컴포넌트"""
    # 설정 변경 시그널 정의
    setting_changed = pyqtSignal(str, object)  # 키, 값

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        # 모던한 카드 스타일
        self.setStyleSheet("""
            ModernSettingsSectionComponent {
                background-color: white;
                border: none;
                border-left: 4px solid #1428A0;
                border-radius: 0 8px 8px 0;

            }
        """)

        # 그림자 효과 추가
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 12, 24, 12)
        main_layout.setSpacing(0)

        # 제목 레이블 생성
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet(
            "color: #1428A0; border: none; margin-bottom: 10px; background: rgba(20, 40, 160, 0.05);")

        # 설정 항목들을 담을 위젯
        self.settings_widget = QWidget()
        self.settings_widget.setStyleSheet("border: none; background-color: transparent;")

        # QFormLayout 사용
        self.settings_layout = QFormLayout(self.settings_widget)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(20)
        self.settings_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.settings_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.settings_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 레이아웃에 위젯 추가
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.settings_widget)

    def add_setting_item(self, label_text, setting_key, widget_type, **kwargs):
        """모던한 스타일의 설정 항목 추가"""

        # 라벨 생성
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 11, QFont.Medium))
        label.setStyleSheet("color: #333; padding: 0px; margin: 0px; font-weight: 500; ")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setMinimumWidth(250)

        # 위젯 생성
        widget = None

        # 텍스트 입력
        if widget_type == 'input':
            widget = QLineEdit()
            widget.setStyleSheet("""
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px 14px;
                    font-size: 14px;
                    font-family: Arial;
                    transition: all 0.3s ease;
                }
                QLineEdit:focus {
                    border-color: #1428A0;
                    box-shadow: 0 0 0 3px rgba(20, 40, 160, 0.1);
                }
                QLineEdit:hover {
                    border-color: #adb5bd;
                }
            """)
            widget.setMinimumWidth(300)
            widget.setMaximumWidth(400)
            widget.setFixedHeight(40)
            if 'default' in kwargs:
                widget.setText(str(kwargs['default']))
            widget.textChanged.connect(lambda text: self.setting_changed.emit(setting_key, text))

        # 정수 스핀박스
        elif widget_type == 'spinbox':
            widget = QSpinBox()
            widget.setStyleSheet("""
                QSpinBox {
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px 14px;
                    font-size: 14px;
                    font-family: Arial;
                }
                QSpinBox:focus {
                    border-color: #1428A0;
                    box-shadow: 0 0 0 3px rgba(20, 40, 160, 0.1);
                }
                QSpinBox:hover {
                    border-color: #adb5bd;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    height: 16px;
                    background-color: #f8f9fa;
                    border: none;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #e9ecef;
                }
                QSpinBox::up-arrow {
                    image: url(none);
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 4px solid #666;
                }
                QSpinBox::down-arrow {
                    image: url(none);
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #666;
                }
            """)
            widget.setMinimumWidth(150)
            widget.setMaximumWidth(200)
            widget.setFixedHeight(40)
            widget.wheelEvent = lambda event: event.ignore()
            if 'min' in kwargs:
                widget.setMinimum(kwargs['min'])
            if 'max' in kwargs:
                widget.setMaximum(kwargs['max'])
            if 'default' in kwargs:
                widget.setValue(kwargs['default'])
            if 'suffix' in kwargs:
                widget.setSuffix(kwargs['suffix'])
            widget.valueChanged.connect(lambda value: self.setting_changed.emit(setting_key, value))

        # 실수 스핀박스
        elif widget_type == 'doublespinbox':
            widget = QDoubleSpinBox()
            widget.setStyleSheet("""
                QDoubleSpinBox {
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px 14px;
                    font-size: 14px;
                    font-family: Arial;
                }
                QDoubleSpinBox:focus {
                    border-color: #1428A0;
                    box-shadow: 0 0 0 3px rgba(20, 40, 160, 0.1);
                }
                QDoubleSpinBox:hover {
                    border-color: #adb5bd;
                }
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 16px;
                    height: 16px;
                    background-color: #f8f9fa;
                    border: none;
                }
                QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                    background-color: #e9ecef;
                }
            """)
            widget.setMinimumWidth(150)
            widget.setMaximumWidth(200)
            widget.setFixedHeight(40)
            widget.wheelEvent = lambda event: event.ignore()
            if 'min' in kwargs:
                widget.setMinimum(kwargs['min'])
            if 'max' in kwargs:
                widget.setMaximum(kwargs['max'])
            if 'default' in kwargs:
                widget.setValue(kwargs['default'])
            if 'decimals' in kwargs:
                widget.setDecimals(kwargs['decimals'])
            if 'step' in kwargs:
                widget.setSingleStep(kwargs['step'])
            if 'suffix' in kwargs:
                widget.setSuffix(kwargs['suffix'])
            widget.valueChanged.connect(lambda value: self.setting_changed.emit(setting_key, value))

        # 체크박스
        elif widget_type == 'checkbox':
            widget = QCheckBox()
            widget.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    spacing: 10px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #dee2e6;
                    border-radius: 4px;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #1428A0;
                    border-color: #1428A0;
                }
                QCheckBox::indicator:hover {
                    border-color: #adb5bd;
                }
                QCheckBox::indicator:checked:hover {
                    background-color: #1a35cc;
                    border-color: #1a35cc;
                }
            """)
            widget.setFixedHeight(30)
            if 'default' in kwargs and kwargs['default']:
                widget.setChecked(True)
            widget.stateChanged.connect(lambda state: self.setting_changed.emit(setting_key, bool(state)))

        # 콤보박스
        elif widget_type == 'combobox':
            widget = QComboBox()
            widget.setStyleSheet("""
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px 14px;
                    font-size: 14px;
                    font-family: Arial;
                }
                QComboBox:focus {
                    border-color: #1428A0;
                    box-shadow: 0 0 0 3px rgba(20, 40, 160, 0.1);
                }
                QComboBox:hover {
                    border-color: #adb5bd;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: url(none);
                    width: 0;
                    height: 0;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #666;
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #dee2e6;
                    background-color: white;
                    selection-background-color: #e9ecef;
                    selection-color: #1428A0;
                }
            """)
            widget.setMinimumWidth(200)
            widget.setMaximumWidth(300)
            widget.setFixedHeight(40)
            if 'items' in kwargs:
                widget.addItems(kwargs['items'])
            if 'default_index' in kwargs:
                widget.setCurrentIndex(kwargs['default_index'])
            widget.currentIndexChanged.connect(
                lambda index: self.setting_changed.emit(setting_key, widget.currentText() if kwargs.get('return_text',
                                                                                                        False) else index)
            )

        # 파일 경로 선택
        elif widget_type == 'filepath':
            container_file = QWidget()
            container_file.setStyleSheet("background-color: transparent; border: none;")
            container_file_layout = QHBoxLayout(container_file)
            container_file_layout.setContentsMargins(0, 0, 0, 0)
            container_file_layout.setSpacing(12)

            # 경로 표시 입력창
            path_input = QLineEdit()
            path_input.setStyleSheet("""
                QLineEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px 14px;
                    font-size: 14px;
                    font-family: Arial;
                }
                QLineEdit:focus {
                    border-color: #1428A0;
                    box-shadow: 0 0 0 3px rgba(20, 40, 160, 0.1);
                }
            """)
            path_input.setMinimumWidth(300)
            path_input.setMaximumWidth(400)
            path_input.setFixedHeight(40)
            if 'default' in kwargs:
                path_input.setText(kwargs['default'])
            path_input.setReadOnly(kwargs.get('readonly', True))

            # 찾아보기 버튼
            browse_button = QPushButton("Browse")
            browse_button.setStyleSheet("""
                QPushButton {
                    background-color: #1428A0;
                    color: white;
                    border-radius: 6px;
                    padding: 10px 20px;
                    border: none;
                    font-family: Arial;
                    font-weight: 500;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1a35cc;
                }
                QPushButton:pressed {
                    background-color: #1e429f;
                }
            """)
            browse_button.setFixedHeight(40)
            browse_button.setCursor(QCursor(Qt.PointingHandCursor))

            # 버튼 클릭 이벤트
            def browse_file():
                dialog_type = kwargs.get('dialog_type', 'file')
                if dialog_type == 'file':
                    if kwargs.get('save_mode', False):
                        file_path, _ = QFileDialog.getSaveFileName(
                            self, "Save File", "", kwargs.get('filter', "All Files (*.*)"))
                    else:
                        file_path, _ = QFileDialog.getOpenFileName(
                            self, "Open File", "", kwargs.get('filter', "All Files (*.*)"))
                else:  # dialog_type == 'directory'
                    file_path = QFileDialog.getExistingDirectory(
                        self, "Select Directory", "")

                if file_path:
                    path_input.setText(file_path)
                    self.setting_changed.emit(setting_key, file_path)

            browse_button.clicked.connect(browse_file)
            path_input.textChanged.connect(lambda text: self.setting_changed.emit(setting_key, text))

            container_file_layout.addWidget(path_input)
            container_file_layout.addWidget(browse_button)

            widget = container_file

        # 버튼 그룹으로 다중 선택 (새로 추가)
        elif widget_type == 'button_group':
            container = QWidget()
            container.setStyleSheet("background-color: transparent; border: none;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(12)

            # 선택된 항목들 표시 레이블
            selected_label = QLabel("Selected items: ")
            selected_label.setFont(QFont("Arial", 10))
            selected_label.setStyleSheet("""
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 8px;
                color: #333;
            """)
            selected_label.setMinimumWidth(400)
            selected_label.setMaximumWidth(500)
            selected_label.setWordWrap(True)

            # 버튼들을 담을 위젯
            button_container = QWidget()
            button_container.setStyleSheet("background-color: transparent; border: none;")
            grid_layout = QGridLayout(button_container)
            grid_layout.setContentsMargins(0, 0, 0, 0)
            grid_layout.setSpacing(8)

            # 선택된 항목들 저장할 리스트
            selected_items = []
            if 'default' in kwargs and isinstance(kwargs['default'], list):
                selected_items = kwargs['default'].copy()

            # 버튼들을 저장할 딕셔너리
            buttons = {}

            # 토글 버튼 스타일
            button_style_normal = """
                QPushButton {
                    background-color: #ffffff;
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 14px;
                    font-family: Arial;
                    font-weight: 500;
                    min-width: 30px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                    border-color: #adb5bd;
                }
            """

            button_style_selected = """
                QPushButton {
                    background-color: #1428A0;
                    border: 2px solid #1428A0;
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 14px;
                    font-family: Arial;
                    font-weight: 600;
                    color: white;
                    min-width: 30px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #1a35cc;
                    border-color: #1a35cc;
                }
            """

            # 선택된 항목 표시 업데이트 함수
            def update_selected_text():
                if selected_items:
                    # 문자열로 변환하고 숫자로 정렬
                    sorted_items = sorted([int(item) for item in selected_items])
                    selected_label.setText("Selected Items: " + ", ".join(map(str, sorted_items)))
                else:
                    selected_label.setText("Selected Items: No items selected")
                # 선택 항목 변경 이벤트 발생
                self.setting_changed.emit(setting_key, [str(item) for item in selected_items])

            # 버튼 클릭 이벤트 처리 함수
            def toggle_button(item):
                if item in selected_items:
                    selected_items.remove(item)
                    buttons[item].setStyleSheet(button_style_normal)
                else:
                    selected_items.append(item)
                    buttons[item].setStyleSheet(button_style_selected)
                update_selected_text()

            # 버튼 생성
            if 'items' in kwargs:
                items = kwargs['items']
                cols = kwargs.get('columns', 7)  # 기본 7열

                for i, item in enumerate(items):
                    button = QPushButton(str(item))
                    button.setCursor(QCursor(Qt.PointingHandCursor))

                    # 기본 상태 또는 선택된 상태 설정
                    if item in selected_items:
                        button.setStyleSheet(button_style_selected)
                    else:
                        button.setStyleSheet(button_style_normal)

                    # 클릭 이벤트 연결
                    button.clicked.connect(lambda checked, val=item: toggle_button(val))

                    # 그리드에 버튼 추가
                    row = i // cols
                    col = i % cols
                    grid_layout.addWidget(button, row, col)

                    # 버튼 딕셔너리에 저장
                    buttons[item] = button

            # 초기 선택 항목 표시
            update_selected_text()

            # 레이아웃에 위젯 추가
            container_layout.addWidget(selected_label)
            container_layout.addWidget(button_container)

            widget = container

        # 다중 선택 콤보박스
        elif widget_type == 'multiselect':
            container_multi = QWidget()
            container_multi.setStyleSheet("background-color: transparent; border: none;")
            container_multi_layout = QVBoxLayout(container_multi)
            container_multi_layout.setContentsMargins(0, 0, 0, 0)
            container_multi_layout.setSpacing(8)

            # 현재 선택된 항목들 표시
            selected_label = QLabel("Selected items: ")
            selected_label.setFont(QFont("Arial", 10))
            selected_label.setStyleSheet("""
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 12px 16px;
                color: #333;
            """)
            selected_label.setMinimumWidth(400)
            selected_label.setMaximumWidth(500)
            selected_label.setWordWrap(True)

            # 콤보박스와 버튼 컨테이너
            combo_container = QWidget()
            combo_container.setStyleSheet("background-color: transparent; border: none;")
            combo_layout = QHBoxLayout(combo_container)
            combo_layout.setContentsMargins(0, 0, 0, 0)
            combo_layout.setSpacing(8)

            # 콤보박스
            combo = QComboBox()
            combo.setStyleSheet("""
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px 14px;
                    font-size: 14px;
                    font-family: Arial;
                }
                QComboBox:focus {
                    border-color: #1428A0;
                    box-shadow: 0 0 0 3px rgba(20, 40, 160, 0.1);
                }
                QComboBox:hover {
                    border-color: #adb5bd;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: url(none);
                    width: 0;
                    height: 0;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #666;
                }
            """)
            combo.setMinimumWidth(150)
            combo.setFixedHeight(40)
            if 'items' in kwargs:
                combo.addItems(kwargs['items'])

            # 선택 버튼
            add_button = QPushButton("Add")
            add_button.setStyleSheet("""
                QPushButton {
                    background-color: #1428A0;
                    color: white;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-family: Arial;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1a35cc;
                }
                QPushButton:pressed {
                    background-color: #1e429f;
                }
            """)
            add_button.setFixedHeight(40)
            add_button.setCursor(QCursor(Qt.PointingHandCursor))

            # 선택된 항목들
            selected_items = []
            if 'default' in kwargs and isinstance(kwargs['default'], list):
                selected_items = kwargs['default'].copy()

            # 선택된 항목 표시 업데이트
            def update_selected_text():
                if selected_items:
                    selected_label.setText("Selected Items: " + ", ".join(map(str, selected_items)))
                else:
                    selected_label.setText("Selected Items: No items selected")
                # 선택 항목 변경 이벤트 발생
                self.setting_changed.emit(setting_key, selected_items.copy())

            # 초기 선택 항목 표시
            update_selected_text()

            # 항목 추가 버튼 클릭 이벤트
            def add_selected_item():
                current_item = combo.currentText()
                if current_item and current_item not in selected_items:
                    selected_items.append(current_item)
                    update_selected_text()

            add_button.clicked.connect(add_selected_item)

            # 삭제 버튼
            remove_button = QPushButton("Remove")
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-family: Arial;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            remove_button.setFixedHeight(40)
            remove_button.setCursor(QCursor(Qt.PointingHandCursor))

            # 항목 제거 버튼 클릭 이벤트
            def remove_selected_item():
                current_item = combo.currentText()
                if current_item in selected_items:
                    selected_items.remove(current_item)
                    update_selected_text()

            remove_button.clicked.connect(remove_selected_item)

            # 위젯 추가
            combo_layout.addWidget(combo)
            combo_layout.addWidget(add_button)
            combo_layout.addWidget(remove_button)
            combo_layout.addStretch(1)

            container_multi_layout.addWidget(selected_label)
            container_multi_layout.addWidget(combo_container)

            widget = container_multi

        # 위젯이 생성되었을 경우에만 폼 레이아웃에 추가
        if widget:
            # QFormLayout에 라벨과 위젯 쌍으로 추가
            self.settings_layout.addRow(label, widget)
            return widget

        return None