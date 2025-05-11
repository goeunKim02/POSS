from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtCore import Qt

from ....resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE

class SummaryDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pre-Assignment Summary")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("QDialog { background-color: #f5f5f5; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 라인별 합산 값 계산
        df_qty = df.groupby('Line', as_index=False)['Qty'].sum()

        # 동 기준 그룹핑
        groups = {}
        for line in df_qty['Line']:
            prefix = line.split('_')[0]
            groups.setdefault(prefix, []).append(line)

        total_rows = sum(len(lines) for lines in groups.values())
        table = QTableWidget(total_rows, 4, self)
        table.setHorizontalHeaderLabels(["Building", "Line", "Sum", "Total"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)

        table.setAlternatingRowColors(True)
        table.setStyleSheet(
            "QTableWidget { background-color: white; gridline-color: #dddddd; alternate-background-color: #e8f4fc; }"
        )

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet(
            "QHeaderView::section { background-color: #1428A0; color: white; font-weight: bold; border: none; }"
        )

        row = 0
        for prefix, lines in groups.items():
            start_row = row
            if len(lines) > 1:
                table.setSpan(start_row, 0, len(lines), 1)
            item_prefix = QTableWidgetItem(prefix)
            item_prefix.setTextAlignment(Qt.AlignCenter)
            item_prefix.setBackground(QColor('#d0e7fb'))
            table.setItem(start_row, 0, item_prefix)
            for line in lines:
                qty_val = int(df_qty[df_qty['Line'] == line]['Qty'].iloc[0])
                item_line = QTableWidgetItem(line)
                item_sum = QTableWidgetItem(str(qty_val))
                item_line.setTextAlignment(Qt.AlignCenter)
                item_sum.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 1, item_line)
                table.setItem(row, 2, item_sum)
                row += 1
            group_sum = int(df_qty[df_qty['Line'].isin(lines)]['Qty'].sum())
            if len(lines) > 1:
                table.setSpan(start_row, 3, len(lines), 1)
            item_total = QTableWidgetItem(str(group_sum))
            item_total.setTextAlignment(Qt.AlignCenter)
            item_total.setBackground(QColor('#d0e7fb'))
            table.setItem(start_row, 3, item_total)

        layout.addWidget(table)

        btn_close = QPushButton("Close", self)
        btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        btn_close.setStyleSheet(PRIMARY_BUTTON_STYLE)
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(btn_close, alignment=Qt.AlignCenter)
        layout.addLayout(btn_layout)