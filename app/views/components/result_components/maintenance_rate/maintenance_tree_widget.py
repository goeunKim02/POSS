from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
import pandas as pd

"""유지율 표시를 위한 트리 위젯 기본 클래스"""
class MaintenanceTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_appearance()
        
    """트리 위젯의 기본 스타일 설정"""
    def setup_appearance(self):
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #dddddd;
                border: none;
                background-color: white;
                alternate-background-color: #f9f9f9;
                font-size: 24px;  
                outline: none;
                gridline-color: #dddddd;
            }
            QTreeWidget::item {
                height: 48px;  
                border-bottom: 1px solid #f0f0f0;
                padding-left: 8px;
                padding-right: 12px;
                border-right: 1px solid #e0e0e0;
            }
            QTreeWidget::item:selected {
                background-color: #f0f5ff;
                color: #1428A0;
                border: none;
                border-right: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: white;
                padding: 12px; 
                border: none;
                border-bottom: 2px solid #1428A0;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                color: #333333;
                font-size: 24px;  
            }
            QTreeView::branch {
                background-color: transparent;
                border: none;
            }
        """)
        self.setAlternatingRowColors(True)
        
    """헤더 설정"""
    def setup_header(self, header_labels):
        self.setHeaderLabels(header_labels)
        self.setColumnCount(len(header_labels))
        
        # 헤더 설정
        header = self.header()
        for i in range(len(header_labels)):
            if i < 3:  # 텍스트 컬럼은 내용에 맞게
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:  # 숫자 컬럼은 고정 크기
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                header.resizeSection(i, 150)
        
        # 헤더 정렬 설정
        for i in range(len(header_labels)):
            self.headerItem().setTextAlignment(i, Qt.AlignCenter)
        
        header.setStretchLastSection(False)
        
    """그룹 아이템 생성"""
    def create_group_item(self, line, shift, prev_sum, curr_sum, maintenance_sum):
        group_item = QTreeWidgetItem([
            line,
            shift,
            "",  # Item/RMC는 비워둠
            f"{prev_sum:,.0f}",
            f"{curr_sum:,.0f}",
            f"{maintenance_sum:,.0f}"
        ])
        
        # 스타일 설정
        for i in range(6):
            group_item.setBackground(i, QBrush(QColor('#f0f5ff')))
            font = group_item.font(i)
            font.setBold(True)
            group_item.setFont(i, font)
        
        # 데이터 정렬
        group_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        group_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        group_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        return group_item
        
    """자식 아이템 생성"""
    def create_child_item(self, item_text, prev_plan, curr_plan, maintenance, is_modified=False):
        child_item = QTreeWidgetItem([
            "",  # Line은 비워둠
            "",  # Shift는 비워둠
            item_text,
            f"{prev_plan:,.0f}",
            f"{curr_plan:,.0f}",
            f"{maintenance:,.0f}"
        ])
        
        # 데이터 정렬
        child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        # 변경 여부에 따라 스타일 적용
        if is_modified:
            font = child_item.font(4)
            font.setBold(True)
            child_item.setFont(4, font)
            child_item.setForeground(4, QBrush(QColor('#F8AC59')))
            
        return child_item
        
    """총계 아이템 생성"""
    def create_total_item(self, total_prev, total_curr, total_maintenance):
        total_item = QTreeWidgetItem([
            "Total",
            "",
            "",
            f"{total_prev:,.0f}",
            f"{total_curr:,.0f}",
            f"{total_maintenance:,.0f}"
        ])
        
        # 스타일 설정
        for i in range(6):
            total_item.setBackground(i, QBrush(QColor('#1428A0')))
            total_item.setForeground(i, QBrush(QColor('white')))
            font = total_item.font(i)
            font.setBold(True)
            total_item.setFont(i, font)
            
        # 데이터 정렬
        total_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        return total_item


"""Item별 유지율 트리 위젯"""
class ItemMaintenanceTree(MaintenanceTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "Item", "prev_plan", "curr_plan", "maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """아이템별 데이터 표시"""
        self.clear()
        
        if df is None or df.empty:
            return
            
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]
        
        # Line-Shift별 그룹화 및 데이터 표시 로직
        self._populate_tree(df_data, modified_item_keys, item_field='Item')


    """RMC별 유지율 트리 위젯"""
class RMCMaintenanceTree(MaintenanceTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "RMC", "prev_plan", "curr_plan", "maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """RMC별 데이터 표시"""
        self.clear()
        
        if df is None or df.empty:
            return
            
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]
        
        # Line-Shift별 그룹화 및 데이터 표시 로직
        self._populate_tree(df_data, modified_item_keys, item_field='RMC')

