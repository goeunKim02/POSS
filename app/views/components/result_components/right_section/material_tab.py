from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QHeaderView)
from PyQt5.QtCore import Qt


class MaterialTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self.shortage_items_table = None
        self.material_analyzer = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 자재 부족 테이블 생성
        self.create_shortage_table()
        layout.addWidget(self.shortage_items_table)
        
        # 부모의 테이블 참조 설정 (호환성)
        self.parent_page.shortage_items_table = self.shortage_items_table
    
    """
    자재 부족 테이블 생성
    """
    def create_shortage_table(self):
        self.shortage_items_table = QTableWidget()
        self.shortage_items_table.setColumnCount(4)
        self.shortage_items_table.setHorizontalHeaderLabels(["Material", "Model", "Shortage", "Shift"])
        self.shortage_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 행 번호 스타일 설정
        self.shortage_items_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.shortage_items_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 4px;
                font-weight: normal;
                border: 1px solid #e0e0e0;
                text-align: center;
            }
        """)
        
        # 테이블 스타일 적용
        self.shortage_items_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #f0f0f0;
                background-color: white;
                border-radius: 0;
                margin-top: 0px;
                outline: none;
            }
            QHeaderView {
                border: none;
                outline: none;
            }                                       
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #1428A0;
                border-radius: 0;
                outline: none;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 0;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
                border-radius: 0;
                outline: none;
            }
            QTableWidget::focus {
                outline: none;
                border: none;
            }
        """)
        
        # 마우스 트래킹 및 이벤트 연결
        self.shortage_items_table.setMouseTracking(True)
        self.shortage_items_table.cellEntered.connect(self.show_shortage_tooltip)
    
    """
    콘텐츠 업데이트
    """
    def update_content(self, data=None):
        # 부모의 update_material_shortage_analysis 호출
        if hasattr(self.parent_page, 'update_material_shortage_analysis'):
            self.parent_page.update_material_shortage_analysis()
    
    """
    테이블 셀에 마우스 올릴 때 상세 정보 툴팁 표시
    """
    def show_shortage_tooltip(self, row, column):
        # 부모의 show_shortage_tooltip 호출
        if hasattr(self.parent_page, 'show_shortage_tooltip'):
            self.parent_page.show_shortage_tooltip(row, column)
    
    """
    테이블 반환
    """
    def get_table(self):
        return self.shortage_items_table
