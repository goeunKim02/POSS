from PyQt5.QtWidgets import (QTableWidget, QHeaderView)
from PyQt5.QtCore import Qt

class CustomTableWidget(QTableWidget):
    def __init__(self, headers=[], parent=None):
        super().__init__(parent)
        self.setup_appearance()
        self.make_read_only()
        if headers:
            self.setup_header(headers)

    """테이블 위젯의 기본 스타일 설정"""
    def setup_appearance(self):
        self.setStyleSheet("""
        QTableWidget {
            border: none;
            gridline-color: #f0f0f0;
            outline: none;
        }
        QHeaderView::section {
            background-color: #1428A0;
            color: white;
            padding: 8px;
            font-weight: bold;
            font-size: 20px;
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
        header.setSectionsClickable(False)  # 클릭 불가
        header.setHighlightSections(False)  # 선택 시 강조 표시 비활성화
    
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