from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
                             QLineEdit, QPushButton, QFrame, QTableWidget)
from PyQt5.QtGui import QFont, QCursor


class TableFilterComponent(QWidget):
    """
    테이블 필터 컴포넌트
    열 선택 및 필터 조건을 설정하여 테이블 데이터를 필터링하는 기능 제공
    """
    filter_applied = pyqtSignal()  # 필터가 적용되었을 때 발생하는 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_widget = None
        self.original_data = []  # 원본 데이터 저장용
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 프레임
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("""
            background-color: #F5F5F5;
            border: none;
        """)
        title_frame.setFixedHeight(40)

        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 0, 0, 0)

        # 제목 레이블
        title_label = QLabel("데이터 필터링")
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        # 컨트롤 프레임
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            background-color: white;
            border: none;
            border-radius: 5px;
        """)

        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(10, 10, 10, 10)

        # 열 선택 콤보박스
        column_label = QLabel("열:")
        column_label.setFont(QFont("Arial"))
        self.column_combo = QComboBox()
        self.column_combo.setMinimumWidth(150)
        self.column_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 3px 5px;
            }
        """)

        # 필터 조건 콤보박스
        condition_label = QLabel("조건:")
        condition_label.setFont(QFont("Arial"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(["포함", "같음", "시작", "끝남", "초과", "미만"])
        self.condition_combo.setMinimumWidth(120)
        self.condition_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 3px 5px;
            }
        """)

        # 필터 값 입력
        value_label = QLabel("값:")
        value_label.setFont(QFont("Arial"))
        self.value_edit = QLineEdit()
        self.value_edit.setMinimumWidth(150)
        self.value_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 3px 5px;
            }
        """)

        # 버튼들
        self.apply_btn = QPushButton("필터 적용")
        self.apply_btn.setFont(QFont("Arial"))
        self.apply_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                border-radius: 10px;
                padding: 5px 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #004C99;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_filter)

        self.reset_btn = QPushButton("초기화")
        self.reset_btn.setFont(QFont("Arial"))
        self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #808080; 
                color: white; 
                border-radius: 10px;
                padding: 5px 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_filter)

        # 컨트롤 레이아웃에 위젯 추가
        control_layout.addWidget(column_label)
        control_layout.addWidget(self.column_combo)
        control_layout.addSpacing(10)
        control_layout.addWidget(condition_label)
        control_layout.addWidget(self.condition_combo)
        control_layout.addSpacing(10)
        control_layout.addWidget(value_label)
        control_layout.addWidget(self.value_edit)
        control_layout.addSpacing(20)
        control_layout.addWidget(self.apply_btn)
        control_layout.addWidget(self.reset_btn)
        control_layout.addStretch(1)

        # 메인 레이아웃에 추가
        main_layout.addWidget(title_frame)
        main_layout.addWidget(control_frame)

    def set_table(self, table_widget):
        """연결할 테이블 위젯 설정"""
        self.table_widget = table_widget

        # 열 이름 가져오기
        self.column_combo.clear()
        if table_widget and table_widget.columnCount() > 0:
            for col in range(table_widget.columnCount()):
                header_item = table_widget.horizontalHeaderItem(col)
                if header_item:
                    self.column_combo.addItem(header_item.text())

        # 원본 데이터 저장
        self.save_original_data()

    def save_original_data(self):
        """테이블의 원본 데이터 저장"""
        self.original_data = []
        if not self.table_widget:
            return

        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                row_data.append(item.text() if item else "")
            self.original_data.append(row_data)

    def apply_filter(self):
        """필터 적용"""
        if not self.table_widget or not self.original_data:
            return

        column_idx = self.column_combo.currentIndex()
        condition = self.condition_combo.currentText()
        filter_value = self.value_edit.text()

        # 모든 행 숨기기
        for row in range(self.table_widget.rowCount()):
            self.table_widget.hideRow(row)

        # 필터링 조건에 맞는 행만 표시
        for row_idx, row_data in enumerate(self.original_data):
            if column_idx < len(row_data):
                cell_value = row_data[column_idx]

                # 필터 조건 확인
                show_row = False
                if condition == "포함":
                    show_row = filter_value.lower() in cell_value.lower()
                elif condition == "같음":
                    show_row = filter_value.lower() == cell_value.lower()
                elif condition == "시작":
                    show_row = cell_value.lower().startswith(filter_value.lower())
                elif condition == "끝남":
                    show_row = cell_value.lower().endswith(filter_value.lower())
                elif condition == "초과":
                    # 숫자로 변환 가능한지 확인
                    try:
                        show_row = float(cell_value) > float(filter_value)
                    except (ValueError, TypeError):
                        show_row = False
                elif condition == "미만":
                    try:
                        show_row = float(cell_value) < float(filter_value)
                    except (ValueError, TypeError):
                        show_row = False

                if show_row:
                    self.table_widget.showRow(row_idx)

        # 시그널 발생
        self.filter_applied.emit()

    def reset_filter(self):
        """필터 초기화"""
        if not self.table_widget:
            return

        # 모든 행 표시
        for row in range(self.table_widget.rowCount()):
            self.table_widget.showRow(row)

        # 필터 입력란 초기화
        self.value_edit.clear()

        # 시그널 발생
        self.filter_applied.emit()