from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDateEdit, QFileDialog, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QDate


class DateRangeSelector(QWidget):
    """날짜 범위 선택 컴포넌트"""
    date_range_changed = pyqtSignal(QDate, QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 시작 날짜
        start_date_label = QLabel("Start Date:")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setFixedWidth(180)
        self.start_date_edit.dateChanged.connect(self.on_date_changed)

        # 종료 날짜
        end_date_label = QLabel("End Date:")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setFixedWidth(180)
        self.end_date_edit.dateChanged.connect(self.on_date_changed)

        # 레이아웃에 위젯 추가
        layout.addWidget(start_date_label)
        layout.addWidget(self.start_date_edit)
        layout.addSpacing(20)
        layout.addWidget(end_date_label)
        layout.addWidget(self.end_date_edit)

    def on_date_changed(self):
        """날짜가 변경되면 시그널 발생"""
        self.date_range_changed.emit(
            self.start_date_edit.date(),
            self.end_date_edit.date()
        )

    def get_date_range(self):
        """현재 선택된 날짜 범위 반환"""
        return self.start_date_edit.date(), self.end_date_edit.date()
