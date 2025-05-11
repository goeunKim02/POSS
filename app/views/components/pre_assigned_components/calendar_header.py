from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt

from ....resources.styles.pre_assigned_style import WEEKDAY_HEADER_STYLE, SEPARATOR_STYLE

class CalendarHeader(QWidget):
    def __init__(self, present_times:set, parent=None):
        super().__init__(parent)
        self.present = present_times

        layout = QGridLayout(self)

        layout.setColumnMinimumWidth(0, 60)
        layout.setColumnMinimumWidth(1, 80)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        for c in range(2, 9):
            layout.setColumnStretch(c, 1)

        # 주말 헤더 칼럼은 비어있으면
        present = set(self.present)
        if not any(t in present for t in (11, 12, 13, 14)):
            layout.setColumnStretch(7, 0)
            layout.setColumnMinimumWidth(7, 80)
            layout.setColumnStretch(8, 0)
            layout.setColumnMinimumWidth(8, 80)    

        layout.setSpacing(6)

        blank0 = QWidget(self)
        blank0.setFixedWidth(60)
        layout.addWidget(blank0, 0, 0, 2, 1)
        blank1 = QWidget(self)
        blank1.setFixedWidth(80)
        layout.addWidget(blank1, 0, 1, 2, 1)

        # 요일 레이블
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(weekdays, start=2):
            header = QLabel(f"<b>{day}</b>")
            header.setAlignment(Qt.AlignCenter)
            header.setFixedHeight(40)
            header.setStyleSheet(WEEKDAY_HEADER_STYLE)
            layout.addWidget(header, 0, col)

        # 헤더 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(SEPARATOR_STYLE)
        separator.setFixedHeight(3)
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(separator, 1, 0, 1, 9)