from PyQt5.QtWidgets import (QTableWidget, QHeaderView, QTableWidgetItem)
from PyQt5.QtCore import Qt
import pandas as pd

class CustomTable(QTableWidget):
    def __init__(self, headers=[], parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setFrameShape(QTableWidget.NoFrame)

        self.setup_appearance()
        self.make_read_only()
        if headers:
            self.setup_header(headers)

        
    """테이블 위젯의 기본 스타일 설정"""
    def setup_appearance(self):
        self.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #E0E0E0;
                background-color: white;
                selection-background-color: #0078D7;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #0c1a6b;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #d0d0d0;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)

        self.setAlternatingRowColors(False)

    """테이블을 읽기 전용으로 설정"""
    def make_read_only(self):
        # 테이블 전체를 읽기 전용으로 설정
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 선택 모드 설정 (행 단위 선택)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        # 포커스 정책 설정
        self.setFocusPolicy(Qt.StrongFocus)
        
    """
    헤더 설정
    header_labels: 헤더 라벨 리스트
    fixed_columns: {index: width} 형태의 dict. 고정하고 싶은 열의 인덱스와 너비
    """
    def setup_header(self, header_labels, fixed_columns=None):
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        
        # 열 너비 설정
        header = self.horizontalHeader()

        # 헤더 클릭/호버/선택 비활성화
        header.setSectionsClickable(True)  # 정렬 가능
        header.setSectionsClickable(False)  # 클릭 불가
        header.setHighlightSections(False)  # 선택 시 강조 표시 비활성화
    
        header.setSortIndicatorShown(True)  # 정렬 화살표 표시
        self.setSortingEnabled(True)        # 정렬 활성화
        
        fixed_columns = fixed_columns or {}
        for i in range(len(header_labels)):
            if i in fixed_columns:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                header.resizeSection(i, fixed_columns[i])
            else:
                header.setSectionResizeMode(i, QHeaderView.Stretch)

        # 가운데 정렬
        for i in range(len(header_labels)):
            item = self.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

        self.verticalHeader().setVisible(False)

    def set_message(self, message: str):
        self.clear()
        self.setRowCount(1)
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Message"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(0, 0, item)

    def set_data(self, df: pd.DataFrame):
        if df is None or df.empty:
            self.set_message("No data to display.")
            return

        self.clear()
        self.setRowCount(len(df))
        self.setColumnCount(len(df.columns))
        self.setHorizontalHeaderLabels(df.columns.tolist())

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row_idx, col_idx, item)

        for i in range(len(df.columns)):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # 가운데 정렬
        for i in range(len(df.columns)):
            item = self.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

    def on_cell_clicked(self, row, column):
        value = self.item(row, column).text()
        print(f"Clicked on cell ({row}, {column}): {value}")