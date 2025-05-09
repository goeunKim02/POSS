from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QLabel, QFrame
)

"""
좌측 파라미터 영역에 프로젝트 분석 결과 표시
"""
class LeftParameterComponent(QWidget):
    
    def __init__(self):
        super().__init__()
        self.project_analysis_data = None
        self._init_ui()
        
    """
    UI 초기화
    """
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #1428A0; border-radius: 4px;")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel("프로젝트 그룹 분석")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        layout.addWidget(title_frame)
        
        self.project_analysis_table = QTreeWidget()
        self.project_analysis_table.setRootIsDecorated(False)
        self.project_analysis_table.setSortingEnabled(True)
        self.project_analysis_table.setStyleSheet("""
            QTreeWidget { border: none; outline: none; }
            QTreeView::branch { background: none; }
            QTreeView::header { background-color: #1428A0; color: white; font-weight: bold; }
            QHeaderView::section { background-color: #1428A0; color: white; border: none; padding: 6px; }
        """)
        
        layout.addWidget(self.project_analysis_table, 1)
        
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("background-color: #F5F5F5; border-radius: 4px;")
        summary_layout = QVBoxLayout(self.summary_frame)
        
        self.summary_label = QLabel("분석 요약")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        summary_layout.addWidget(self.summary_label)
        
        layout.addWidget(self.summary_frame)
    
    """
    프로젝트 분석 데이터 설정
    """
    def set_project_analysis_data(self, data) :
        self.project_analysis_data = data
        self._populate_project_analysis_table()
        self._update_summary()
    
    """
    프로젝트 분석 테이블 채우기
    """
    def _populate_project_analysis_table(self):
        if not self.project_analysis_data :
            return
        
        display_df = self.project_analysis_data.get('display_df')
        
        if display_df is None or display_df.empty :
            return
        
        headers = ["PJT Group", "PJT", "MFG", "SOP", "CAPA", "MFG/CAPA", "SOP/CAPA"]
        
        if 'status' in display_df.columns:
            headers.append('Status')
        
        self.project_analysis_table.clear()
        self.project_analysis_table.setColumnCount(len(headers))
        self.project_analysis_table.setHeaderLabels(headers)
        
        red_brush = QBrush(QColor('#e74c3c'))
        bold_font = QFont()
        bold_font.setBold(True)
        
        group_items = {}
        
        for _, row in display_df.iterrows() :
            pjt_group = str(row.get('PJT Group', ''))
            pjt = str(row.get('PJT', ''))
            
            row_data = []

            for col in headers :
                if col == 'Status' :
                    row_data.append(str(row.get('status', '')))
                else :
                    row_data.append(str(row.get(col, '')))
            
            item = QTreeWidgetItem(row_data)
            
            if pjt == 'Total' :
                for col in range(len(headers)) :
                    item.setFont(col, bold_font)
                
                if row.get('status', '') == '이상' :
                    for col in range(len(headers)) :
                        item.setForeground(col, red_brush)
            
            self.project_analysis_table.addTopLevelItem(item)
            
            if pjt_group not in group_items:
                group_items[pjt_group] = []

            group_items[pjt_group].append(item)
        
        for i in range(len(headers)):
            self.project_analysis_table.resizeColumnToContents(i)
    
    """
    요약 정보 업데이트
    """
    def _update_summary(self):
        if not self.project_analysis_data:
            return
        
        summary = self.project_analysis_data.get('summary')
        
        if summary is None or summary.empty :
            return
        
        summary_text = "<b>분석 요약:</b><br>"
        summary_text += f"총 그룹 수: {summary.get('총 그룹 수', 0)}<br>"
        summary_text += f"이상 그룹 수: {summary.get('이상 그룹 수', 0)}<br>"
        summary_text += f"전체 MFG: {summary.get('전체 MFG', 0):,}<br>"
        summary_text += f"전체 SOP: {summary.get('전체 SOP', 0):,}<br>"
        summary_text += f"전체 CAPA: {summary.get('전체 CAPA', 0):,}<br>"
        summary_text += f"전체 MFG/CAPA 비율: {summary.get('전체 MFG/CAPA 비율', '0%')}<br>"
        summary_text += f"전체 SOP/CAPA 비율: {summary.get('전체 SOP/CAPA 비율', '0%')}"
        
        self.summary_label.setText(summary_text)