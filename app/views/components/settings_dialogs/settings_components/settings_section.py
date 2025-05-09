# app/views/components/settings_dialogs/settings_components/settings_section.py
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QComboBox, QPushButton, QFileDialog, QWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal


class SettingsSectionComponent(QFrame):
    """설정 섹션 컴포넌트 - 제목과 설정 항목들을 포함할 수 있는 섹션"""
    # 설정 변경 시그널 정의
    setting_changed = pyqtSignal(str, object)  # 키, 값

    def __init__(self, title, parent=None):
        """
        설정 섹션 초기화

        Args:
            title (str): 섹션 제목
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        self.title = title
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        # 기본 스타일 설정
        self.setStyleSheet(
            "background-color: white; border:none; border-left: 4px solid #1428A0; padding: 5px; border-radius: 0 5px 5px 0;")

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 제목 레이블 생성
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #1428A0; border:none; margin-bottom: 5px;")

        # 설정 항목들을 담을 위젯
        self.settings_widget = QWidget()
        self.settings_widget.setStyleSheet("border: none; background-color: transparent;")
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_layout.setContentsMargins(10, 0, 0, 0)
        self.settings_layout.setSpacing(10)

        # 레이아웃에 위젯 추가
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.settings_widget)

    def add_setting_item(self, label_text, setting_key, widget_type, **kwargs):
        """
        설정 항목 추가

        Args:
            label_text (str): 설정 항목 라벨 텍스트
            setting_key (str): 설정 키
            widget_type (str): 위젯 유형 ('input', 'spinbox', 'doublespinbox', 'checkbox', 'combobox', 'filepath', 'multiselect')
            **kwargs: 위젯별 추가 파라미터
        """
        # 컨테이너 위젯 생성
        container = QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)  # 간격 줄임

        # 라벨 생성
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("color: #333333;")
        label.setAlignment(Qt.AlignLeft)

        # 위젯 생성
        widget = None

        # 텍스트 입력
        if widget_type == 'input':
            widget = QLineEdit()
            widget.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")
            if 'default' in kwargs:
                widget.setText(str(kwargs['default']))
            widget.textChanged.connect(lambda text: self.setting_changed.emit(setting_key, text))

        # 정수 스핀박스
        elif widget_type == 'spinbox':
            widget = QSpinBox()
            widget.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")
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
            widget.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")
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
            if 'default' in kwargs and kwargs['default']:
                widget.setChecked(True)
            widget.stateChanged.connect(lambda state: self.setting_changed.emit(setting_key, bool(state)))

        # 콤보박스
        elif widget_type == 'combobox':
            widget = QComboBox()
            widget.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")
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
            container_file.setStyleSheet("background-color: transparent; border:none;")
            container_file_layout = QHBoxLayout(container_file)
            container_file_layout.setContentsMargins(0, 0, 0, 0)
            container_file_layout.setSpacing(10)

            # 경로 표시 입력창
            path_input = QLineEdit()
            path_input.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc; ")
            if 'default' in kwargs:
                path_input.setText(kwargs['default'])
            path_input.setReadOnly(kwargs.get('readonly', True))

            # 찾아보기 버튼
            browse_button = QPushButton("Browse")
            browse_button.setStyleSheet("""
                QPushButton {
                    background-color: #1428A0;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    border: none;
                    font-family: Arial; 
                }
                QPushButton:hover {
                    background-color: #1e429f;
                }
            """)

            # 버튼 클릭 이벤트
            def browse_file():
                dialog_type = kwargs.get('dialog_type', 'file')
                if dialog_type == 'file':
                    if kwargs.get('save_mode', False):
                        file_path, _ = QFileDialog.getSaveFileName(
                            self, "파일 저장", "", kwargs.get('filter', "모든 파일 (*.*)"))
                    else:
                        file_path, _ = QFileDialog.getOpenFileName(
                            self, "파일 열기", "", kwargs.get('filter', "모든 파일 (*.*)"))
                else:  # dialog_type == 'directory'
                    file_path = QFileDialog.getExistingDirectory(
                        self, "디렉토리 선택", "")

                if file_path:
                    path_input.setText(file_path)
                    self.setting_changed.emit(setting_key, file_path)

            browse_button.clicked.connect(browse_file)

            # 경로 입력창 변경 이벤트
            path_input.textChanged.connect(lambda text: self.setting_changed.emit(setting_key, text))

            # 위젯 추가
            container_file_layout.addWidget(path_input)
            container_file_layout.addWidget(browse_button)
            container_file_layout.setStretch(0, 4)  # 입력창 크기 비율
            container_file_layout.setStretch(1, 1)  # 버튼 크기 비율

            widget = container_file

        # 다중 선택 콤보박스
        elif widget_type == 'multiselect':
            container_multi = QWidget()
            container_multi.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")
            container_multi_layout = QVBoxLayout(container_multi)
            container_multi_layout.setContentsMargins(0, 0, 0, 0)
            container_multi_layout.setSpacing(5)

            # 현재 선택된 항목들 표시
            selected_label = QLabel("Selected items: ")
            selected_label.setFont(QFont("Arial", 9))
            selected_label.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")

            # 콤보박스와 버튼 컨테이너
            combo_container = QWidget()
            combo_container.setStyleSheet("background-color: #F5F5F5; border:none;")
            combo_layout = QHBoxLayout(combo_container)
            combo_layout.setContentsMargins(0, 0, 0, 0)
            combo_layout.setSpacing(5)

            # 콤보박스
            combo = QComboBox()
            combo.setStyleSheet("background-color: #F5F5F5; border: 1px solid #cccccc;")
            if 'items' in kwargs:
                combo.addItems(kwargs['items'])

            # 선택 버튼
            add_button = QPushButton("Add")
            add_button.setStyleSheet("""
                QPushButton {
                    background-color: #1428A0;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                    font-family: Arial;  
                }
                QPushButton:hover {
                    background-color: #1e429f;
                }
            """)

            # 선택된 항목들
            selected_items = []
            if 'default' in kwargs and isinstance(kwargs['default'], list):
                selected_items = kwargs['default'].copy()

            # 선택된 항목 표시 업데이트
            def update_selected_text():
                if selected_items:
                    selected_label.setText("Selected Items: " + ", ".join(map(str, selected_items)))
                else:
                    selected_label.setText("Please select an item. No item selected.")
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
                    background-color: #B22222;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                    font-family: Arial;
                }
                QPushButton:hover {
                    background-color: #DC143C;
                }
            """)

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

            container_multi_layout.addWidget(selected_label)
            container_multi_layout.addWidget(combo_container)

            widget = container_multi

        # 위젯이 생성되었을 경우에만 컨테이너에 추가
        if widget:
            # 라벨 추가
            widget.setMinimumWidth(400)
            container_layout.addWidget(label)

            # 위젯을 담을 컨테이너 생성 - 좌우 여백 적용
            widget_container = QWidget()
            widget_container.setStyleSheet("background-color: transparent; border: none;")
            widget_layout = QHBoxLayout(widget_container)
            widget_layout.setContentsMargins(30, 0, 30, 0)
            widget_layout.addWidget(widget)
            widget_layout.addStretch(1)

            # 위젯 컨테이너 추가
            container_layout.addWidget(widget_container)

            # 설정 레이아웃에 컨테이너 추가
            self.settings_layout.addWidget(container)

            return widget  # 생성된 위젯 반환

        return None