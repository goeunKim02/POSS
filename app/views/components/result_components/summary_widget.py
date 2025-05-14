
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
import pandas as pd
from app.analysis.output.capa_ratio import CapaRatioAnalyzer
from app.analysis.output.daily_capa_utilization import CapaUtilization
from app.analysis.output.separate_region_and_group import analyze_line_allocation

"""결과 요약 정보 표시 위젯"""
class SummaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10 ,10, 10)
        main_layout.setSpacing(10)

        # 제목
        title_label = QLabel("Producation Plan Summary")
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 요약 테이블
        self.summary_table = QTableWidget()
        self.setup_table_style()
        main_layout.addWidget(self.summary_table)


    """테이블 스타일 설정"""
    def setup_table_style(self):
        self.summary_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #0C1A6B;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
        """)
        
        # 헤더 설정
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)


    """결과 분석 및 테이블 업데이트"""
    def run_analysis(self, result_data):
        if result_data is None or result_data.empty:
            self.clear_table()
            return
        
        try:
            # 1. 제조동별 비율 계산
            capa_ratios = CapaRatioAnalyzer.analyze_capa_ratio(data_df=result_data, is_initial=True)

            # 2. 가동률 계산
            utilization_rates = CapaUtilization.analyze_utilization(result_data)

            # 3. 상세 정보 추출
            summary_data = self.create_summary(result_data, capa_ratios, utilization_rates)
            
            # 4. 테이블 업데이트
            self.update_table(summary_data)

        except Exception as e:
            print(f"summary 요약 중 에러 : {e}")


    """요약 데이터 생성"""
    def create_summary(self, result_data, capa_ratios, utilization_rates):
        # 제조동별 데이터 추출
        result_data = result_data.copy()
        result_data['Building'] = result_data['Line'].str.split('_').str[0]
        print(f"제조동 추출: {result_data['Building']}")

        # 제조동별 생산량 집계
        building_qty = result_data.groupby('Building')['Qty'].sum()

        # 제조동별 라인 정보
        building_lines = result_data.groupby('Building')['Line'].nunique()