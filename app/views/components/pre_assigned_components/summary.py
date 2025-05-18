from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QAbstractScrollArea
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


"""
데이터를 요약해서 표시하는 테이블 위젯
"""
class SummaryWidget(QWidget):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 데이터 집계
        df_qty = (
            df.groupby('Line', as_index=False)['Qty'].sum()
            .sort_values(by='Qty', ascending=False)
            .reset_index(drop=True)
        )
        grand_total = df_qty['Qty'].sum()

        # 동별 그룹핑
        groups = {}
        for line in df_qty['Line']:
            prefix = line.split('_')[0]
            groups.setdefault(prefix, []).append(line)

        # 그룹별 총합 계산 및 정렬
        group_summaries = []
        for prefix, lines in groups.items():
            group_sum = df_qty[df_qty['Line'].isin(lines)]['Qty'].sum()
            group_summaries.append((prefix, lines, group_sum))
        group_summaries.sort(key=lambda x: x[2], reverse=True)

        # 전체 행 개수 계산
        total_rows = 1 + sum(1 + len(lines) for _, lines, _ in group_summaries)
        table = QTableWidget(total_rows, 4, self)
        table.setHorizontalHeaderLabels(["Building", "Line", "Sum", "Portion"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setAlternatingRowColors(False)
        table.setStyleSheet(
            "QTableWidget { background-color: white; gridline-color: #dddddd; }"
        )

        # 헤더 스타일 및 폰트
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet(
            "QHeaderView::section { background-color: #1428A0; color: white; border: none; }"
        )
        header_font = QFont("Arial", 10, QFont.Bold)
        header.setFont(header_font)
        
        table.verticalHeader().setDefaultSectionSize(35)

        # 폰트 정의
        font_10 = QFont("Arial", 10)
        font_9 = QFont("Arial", 9)
        bold_font_10 = QFont("Arial", 10, QFont.Bold)
        bold_font_9 = QFont("Arial", 9, QFont.Bold)

        # 첫 행: Total
        row = 0
        table.setSpan(row, 0, 1, 2)
        item_tot_label = QTableWidgetItem("Total")
        item_tot_label.setTextAlignment(Qt.AlignCenter)
        item_tot_label.setFont(bold_font_10)
        item_tot_label.setBackground(QColor('#e8f4fc'))
        table.setItem(row, 0, item_tot_label)

        item_tot_sum = QTableWidgetItem(f"{int(grand_total):,}")
        item_tot_sum.setTextAlignment(Qt.AlignCenter)
        item_tot_sum.setFont(font_9)
        item_tot_sum.setBackground(QColor('#e8f4fc'))
        table.setItem(row, 2, item_tot_sum)

        item_tot_portion = QTableWidgetItem("-")
        item_tot_portion.setTextAlignment(Qt.AlignCenter)
        item_tot_portion.setFont(font_10)
        table.setItem(row, 3, item_tot_portion)
        row += 1

        # 그룹별
        for prefix, lines, group_sum in group_summaries:
            start = row
            span_count = 1 + len(lines)
            group_share = round(group_sum / grand_total * 100, 1)

            # Building
            table.setSpan(start, 0, span_count, 1)
            item_building = QTableWidgetItem(prefix)
            item_building.setTextAlignment(Qt.AlignCenter)
            item_building.setFont(bold_font_10)
            item_building.setBackground(QColor('#e8f4fc'))
            table.setItem(start, 0, item_building)

            # Group total (1열)
            item_group = QTableWidgetItem(f"{prefix}_Total")
            item_group.setTextAlignment(Qt.AlignCenter)
            item_group.setFont(bold_font_9)
            item_group.setBackground(QColor('#e8f4fc'))
            table.setItem(start, 1, item_group)

            # Sum (2열)
            item_group_sum = QTableWidgetItem(f"{int(group_sum):,}")
            item_group_sum.setTextAlignment(Qt.AlignCenter)
            item_group_sum.setFont(font_9)
            item_group_sum.setBackground(QColor('#e8f4fc'))
            table.setItem(start, 2, item_group_sum)

            # Portion (3열)
            table.setSpan(start, 3, span_count, 1)
            item_group_portion = QTableWidgetItem(f"{group_share}%")
            item_group_portion.setTextAlignment(Qt.AlignCenter)
            item_group_portion.setFont(font_10)
            item_group_portion.setForeground(QColor('#1428A0'))
            table.setItem(start, 3, item_group_portion)
            row += 1

            # 각 라인
            for ln in lines:
                qty_val = int(df_qty[df_qty['Line'] == ln]['Qty'].iloc[0])
                item_line = QTableWidgetItem(ln)
                item_line.setTextAlignment(Qt.AlignCenter)
                item_line.setData(Qt.DisplayRole, f"    {ln}")
                item_line.setFont(font_9)
                table.setItem(row, 1, item_line)

                item_line_sum = QTableWidgetItem(f"{qty_val:,}")
                item_line_sum.setTextAlignment(Qt.AlignCenter)
                item_line_sum.setFont(font_9)
                table.setItem(row, 2, item_line_sum)

                row += 1

        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(table)
        self.adjustSize()
        self.setFixedHeight(self.sizeHint().height())