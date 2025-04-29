from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDateEdit, QFileDialog, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from .custom_calendar import CustomCalendarWidget


class DateRangeSelector(QWidget):
    """날짜 범위 선택 컴포넌트"""
    date_range_changed = pyqtSignal(QDate, QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        main_container = QFrame()
        main_container.setStyleSheet("background-color: white;  border-radius: 5px; border:none")

        main_container_layout = QHBoxLayout(main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)

        # 시작 날짜
        start_date_label = QLabel("Start Date:")
        start_date_font = QFont("Arial")
        start_date_label.setFont(start_date_font)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet("border: 2px solid #cccccc; border-radius: 5px;")

        # 커스텀 캘린더 위젯 적용
        start_calendar = CustomCalendarWidget()
        self.start_date_edit.setCalendarWidget(start_calendar)

        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setFixedWidth(180)
        self.start_date_edit.dateChanged.connect(self.on_date_changed)
        self.start_date_edit.setFont(start_date_font)

        # 종료 날짜
        end_date_label = QLabel("End Date:")
        end_date_font = QFont("Arial")
        end_date_label.setFont(end_date_font)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet("border: 2px solid #cccccc; border-radius: 5px;")

        # 커스텀 캘린더 위젯 적용
        end_calendar = CustomCalendarWidget()
        self.end_date_edit.setCalendarWidget(end_calendar)

        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setFixedWidth(180)
        self.end_date_edit.dateChanged.connect(self.on_date_changed)
        self.end_date_edit.setFont(end_date_font)

        # 위젯 추가
        main_container_layout.addWidget(start_date_label)
        main_container_layout.addWidget(self.start_date_edit)
        main_container_layout.addSpacing(20)
        main_container_layout.addWidget(end_date_label)
        main_container_layout.addWidget(self.end_date_edit)
        main_container_layout.addStretch(1)  # 오른쪽 공간 채우기

        # 메인 레이아웃에 컨테이너 추가
        layout.addWidget(main_container)

    def on_date_changed(self):
        """날짜가 변경되면 시그널 발생"""
        self.date_range_changed.emit(
            self.start_date_edit.date(),
            self.end_date_edit.date()
        )

    def get_date_range(self):
        """현재 선택된 날짜 범위 반환"""
        return self.start_date_edit.date(), self.end_date_edit.date()