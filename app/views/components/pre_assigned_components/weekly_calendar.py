import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QFrame, QSizePolicy, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt

from ....resources.styles.pre_assigned_style import (
    LINE_LABEL_STYLE, DAY_LABEL_STYLE, NIGHT_LABEL_STYLE, SEPARATOR_STYLE
)
from .calendar_card import CalendarCard
from .detail_dialog import DetailDialog

class WeeklyCalendar(QWidget):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self.data = data.rename(columns={
            "Line": "line",
            "Time": "time",
            "Qty": "qty",
            "Project": "project",
            "Details": "details",
        })
        self.time_map = {
            1: "Mon-Day", 2: "Mon-Night",
            3: "Tue-Day", 4: "Tue-Night",
            5: "Wed-Day", 6: "Wed-Night",
            7: "Thu-Day", 8: "Thu-Night",
            9: "Fri-Day",10: "Fri-Night",
           11: "Sat-Day",12: "Sat-Night",
           13: "Sun-Day",14: "Sun-Night"
        }
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        total_cols = 9
        layout.setColumnMinimumWidth(0, 60)
        layout.setColumnMinimumWidth(1, 80)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        for c in range(2, total_cols):
            layout.setColumnStretch(c, 1)

        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(6)

        lines = sorted(self.data['line'].unique())
        row_index = 0

        for line in lines:
            line_label = QLabel(f"<b>{line}</b>")
            line_label.setAlignment(Qt.AlignCenter)
            line_label.setStyleSheet(LINE_LABEL_STYLE)
            line_label.setMaximumWidth(60)
            line_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            layout.addWidget(line_label, row_index, 0, 3, 1)

            # Day 레이블
            day_label = QLabel("Day")
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setStyleSheet(DAY_LABEL_STYLE)
            day_label.setMaximumWidth(80)
            day_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            layout.addWidget(day_label, row_index, 1)

            layout.setRowMinimumHeight(row_index, 80)

            # Day 카드들
            for time in range(1, 15, 2):
                col_idx = (time - 1) // 2 + 2
                cell = QWidget()
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(4)

                subset = self.data[(self.data['line'] == line) & (self.data['time'] == time)]
                for _, r in subset.iterrows():
                    card = CalendarCard(r.to_dict(), is_day=True, parent=cell)
                    card.row = r.to_dict()
                    card.clicked.connect(self.show_detail_card)
                    cell_layout.addWidget(card)

                cell_layout.addStretch()
                layout.addWidget(cell, row_index, col_idx)

            # Day/Night 구분선
            mid_sep = QFrame()
            mid_sep.setFrameShape(QFrame.HLine)
            mid_sep.setFrameShadow(QFrame.Plain)
            mid_sep.setStyleSheet(SEPARATOR_STYLE)
            mid_sep.setFixedHeight(1)
            mid_sep.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(mid_sep, row_index + 1, 1, 1, total_cols - 1)

            # Night 레이블
            night_label = QLabel("Night")
            night_label.setAlignment(Qt.AlignCenter)
            night_label.setStyleSheet(NIGHT_LABEL_STYLE)
            night_label.setMaximumWidth(80)
            night_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            layout.addWidget(night_label, row_index + 2, 1)

            layout.setRowMinimumHeight(row_index + 2, 80)

            # Night 카드들
            for time in range(2, 15, 2):
                col_idx = (time - 1) // 2 + 2
                cell = QWidget()
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(4)

                subset = self.data[(self.data['line'] == line) & (self.data['time'] == time)]
                for _, r in subset.iterrows():
                    card = CalendarCard(r.to_dict(), is_day=False, parent=cell)
                    card.row = r.to_dict()
                    card.clicked.connect(self.show_detail_card)
                    cell_layout.addWidget(card)

                cell_layout.addStretch()
                layout.addWidget(cell, row_index + 2, col_idx)

            # 라인 끝 구분선
            end_sep = QFrame()
            end_sep.setFrameShape(QFrame.HLine)
            end_sep.setFrameShadow(QFrame.Plain)
            end_sep.setStyleSheet(SEPARATOR_STYLE)
            layout.addWidget(end_sep, row_index + 3, 0, 1, total_cols)

            row_index += 4

        self.setLayout(layout)

    def show_detail_card(self, row: dict):
        card = self.sender()

        row  = getattr(card, 'row', {})
        dlg  = DetailDialog(row, self.time_map, parent=self)
        dlg.exec_()

        card._is_selected = False
        card.setStyleSheet(card.base_style)