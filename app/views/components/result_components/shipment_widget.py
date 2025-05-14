from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QProgressBar, QSplitter, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QFont, QPainter, QPen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from app.analysis.output.this_week_shipment import analyze_and_get_results

"""당주 출하 분석 위젯"""
class ShipmentWidget(QWidget):
    
    
    # 출하 실패 정보 전달용 시그널
    shipment_status_updated = pyqtSignal(dict)  # 실패 아이템 정보 전달
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_df = None
        self.summary = None
        self.analysis_df = None
        self.failure_items = {}  # 아이템별 실패 정보 저장
        self.init_ui()
        
    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 스플리터 생성 (상하 분할)
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        
        # 테두리와 배경색 제거
        splitter.setStyleSheet("""
            QSplitter {
                border: none;
                background-color: transparent;
            }
            QSplitter::handle {
                background-color: #F0F0F0;
            }
        """)
        
        # 상단 섹션 - 차트와 통계
        self.top_section = QWidget()
        top_layout = QVBoxLayout(self.top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        
        # 배경색 및 테두리 제거
        self.top_section.setStyleSheet("background-color: transparent; border: none;")
        
        top_title = QLabel("Shipment Satisfaction Rate")
        top_title.setFont(QFont("Arial", 12, QFont.Bold))
        top_layout.addWidget(top_title)
        
        # 만족률 카드 컨테이너
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        
        # 카드 컨테이너 배경색 및 테두리 제거
        cards_container.setStyleSheet("background-color: transparent; border: none;")
        
        # 수량 기준 만족률 카드
        qty_card = QFrame()
        qty_card.setFrameShape(QFrame.NoFrame)  # 프레임 테두리 제거
        qty_card.setStyleSheet("background-color: transparent; border: none;")  # 배경색 및 테두리 제거
        qty_card_layout = QVBoxLayout(qty_card)
        
        qty_title = QLabel("Qty-based Satisfaction Rate")
        qty_title.setFont(QFont("Arial", 10, QFont.Bold))
        qty_card_layout.addWidget(qty_title)
        
        self.qty_progress = QProgressBar()
        self.qty_progress.setTextVisible(True)
        self.qty_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #F0F0F0;
            }
            QProgressBar::chunk {
                background-color: #1428A0;
                border-radius: 5px;
            }
        """)
        qty_card_layout.addWidget(self.qty_progress)
        
        self.qty_detail = QLabel("0 / 0 (0.0%)")  # 소수점 1자리 표시
        self.qty_detail.setAlignment(Qt.AlignCenter)
        qty_card_layout.addWidget(self.qty_detail)
        
        # 모델 기준 만족률 카드
        model_card = QFrame()
        model_card.setFrameShape(QFrame.NoFrame)  # 프레임 테두리 제거
        model_card.setStyleSheet("background-color: transparent; border: none;")  # 배경색 및 테두리 제거
        model_card_layout = QVBoxLayout(model_card)
        
        model_title = QLabel("Model-based Satisfaction Rate")
        model_title.setFont(QFont("Arial", 10, QFont.Bold))
        model_card_layout.addWidget(model_title)
        
        self.model_progress = QProgressBar()
        self.model_progress.setTextVisible(True)
        self.model_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #F0F0F0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        model_card_layout.addWidget(self.model_progress)
        
        self.model_detail = QLabel("0 / 0 (0.0%)")  # 소수점 1자리 표시
        self.model_detail.setAlignment(Qt.AlignCenter)
        model_card_layout.addWidget(self.model_detail)
        
        # 카드 추가
        cards_layout.addWidget(qty_card)
        cards_layout.addWidget(model_card)
        top_layout.addWidget(cards_container)
        
        # 그래프 영역
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        # 캔버스에도 배경색 및 테두리 제거
        self.canvas.setStyleSheet("background-color: transparent; border: none;")
        top_layout.addWidget(self.canvas, 1)  # 나머지 공간을 차지하도록 stretch factor 1 설정
        
        # 통계 테이블
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Category", "Total", "Success", "Success Rate"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: transparent;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 4px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #F0F0F0;
            }
        """)
        
        # 기본 통계 행 추가
        self.stats_table.setRowCount(2)
        self.stats_table.setItem(0, 0, QTableWidgetItem("Quantity (Qty)"))
        self.stats_table.setItem(1, 0, QTableWidgetItem("Model"))
        
        top_layout.addWidget(self.stats_table)
        
        # 하단 섹션 - 출하 실패 모델 테이블
        self.bottom_section = QWidget()
        bottom_layout = QVBoxLayout(self.bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        
        # 배경색 및 테두리 제거
        self.bottom_section.setStyleSheet("background-color: transparent; border: none;")
        
        bottom_title = QLabel("Failed Shipment Models")
        bottom_title.setFont(QFont("Arial", 12, QFont.Bold))
        bottom_layout.addWidget(bottom_title)
        
        self.failed_table = QTableWidget()
        self.failed_table.setColumnCount(5)
        self.failed_table.setHorizontalHeaderLabels(["Item", "To_site", "Failure Reason", "Required(SOP)", "Production(Qty)"])
        self.failed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.failed_table.verticalHeader().setVisible(False)
        self.failed_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.failed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.failed_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: transparent;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 4px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #DEEBF7;
                color: black;
            }
        """)
        
        bottom_layout.addWidget(self.failed_table)
        
        # 스플리터에 위젯 추가
        splitter.addWidget(self.top_section)
        splitter.addWidget(self.bottom_section)
        
        # 초기 비율 설정 (1:1)
        splitter.setSizes([500, 500])
        
        main_layout.addWidget(splitter)
        
    def run_analysis(self, result_data=None):
        """당주 출하 분석 실행"""
        try:
            # 분석 실행 - 외부에서 전달받은 결과 데이터가 있으면 사용
            self.result_df, self.summary, self.analysis_df = analyze_and_get_results(
                use_flexible_matching=True, 
                result_data=result_data
            )
            
            if self.result_df is None or self.summary is None:
                return
            
            # 기본 정보 업데이트
            self.update_summary_info()
            
            # 출하 실패 테이블 업데이트
            self.update_failed_table()
            
            # 그래프 업데이트
            self.update_chart()
            
            # 실패 아이템 정보 전달
            self.detect_and_emit_failures()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    """요약 정보 업데이트"""
    def update_summary_info(self):
        if not self.summary:
            return
        
        # 프로그레스바 업데이트
        qty_rate = round(self.summary.get('qty_success_rate', 0), 1)  # 소수점 1자리로 반올림
        model_rate = round(self.summary.get('model_success_rate', 0), 1)  # 소수점 1자리로 반올림
        
        self.qty_progress.setValue(int(qty_rate))
        self.model_progress.setValue(int(model_rate))
        
        # 상세 정보 업데이트
        success_qty = int(self.summary.get('success_qty', 0))  # 정수형으로 변환
        total_sop = int(self.summary.get('total_sop', 0))  # 정수형으로 변환
        self.qty_detail.setText(f"{success_qty:,} / {total_sop:,} ({qty_rate:.1f}%)")
        
        success_models = int(self.summary.get('success_models', 0))  # 정수형으로 변환
        total_models = int(self.summary.get('total_models', 0))  # 정수형으로 변환
        self.model_detail.setText(f"{success_models} / {total_models} ({model_rate:.1f}%)")
        
        # 통계 테이블 업데이트
        self.stats_table.setItem(0, 1, QTableWidgetItem(f"{total_sop:,}"))
        self.stats_table.setItem(0, 2, QTableWidgetItem(f"{success_qty:,}"))
        self.stats_table.setItem(0, 3, QTableWidgetItem(f"{qty_rate:.1f}%"))
        
        self.stats_table.setItem(1, 1, QTableWidgetItem(f"{total_models}"))
        self.stats_table.setItem(1, 2, QTableWidgetItem(f"{success_models}"))
        self.stats_table.setItem(1, 3, QTableWidgetItem(f"{model_rate:.1f}%"))
        
        # 색상 강조
        for row in range(2):
            success_rate = qty_rate if row == 0 else model_rate
            color = self.get_color_for_rate(success_rate)
            self.stats_table.item(row, 3).setBackground(QBrush(color))
    
    """만족률에 따른 색상 반환"""
    def get_color_for_rate(self, rate):
        if rate >= 90:
            return QColor(200, 255, 200)  # 연한 녹색
        elif rate >= 70:
            return QColor(255, 255, 200)  # 연한 노란색
        else:
            return QColor(255, 200, 200)  # 연한 빨간색
    
    """출하 실패 모델 테이블 업데이트"""
    def update_failed_table(self):
        if self.analysis_df is None or self.result_df is None:
            return
        
        # 실패 항목 필터링
        failed_items = self.analysis_df[~self.analysis_df['IsShippable']]
        
        # 테이블 초기화
        self.failed_table.setRowCount(0)
        
        if failed_items.empty:
            self.failed_table.setRowCount(1)
            empty_message = QTableWidgetItem("No failed shipment models")
            empty_message.setTextAlignment(Qt.AlignCenter)
            self.failed_table.setItem(0, 0, empty_message)
            self.failed_table.setSpan(0, 0, 1, 5)
            return
        
        # Demand에 있는 항목만 필터링 (match_key가 있는 항목)
        demand_failed_items = failed_items[failed_items['MatchKey'].notna()]
        
        # Match_key별 그룹화하여 고유한 실패 모델만 표시
        grouped_failures = {}
        
        for _, row in demand_failed_items.iterrows():
            match_key = row['MatchKey']
            if match_key not in grouped_failures:
                grouped_failures[match_key] = {
                    'Item': row['Item'],
                    'To_site': row['To_site'],
                    'DemandSOP': int(row['DemandSOP']),  # 정수형으로 변환
                    'QualifiedQty': int(row['QualifiedQty']),  # 정수형으로 변환
                    'TimeConditionMet': row['TimeConditionMet'],
                    'QtyConditionMet': row['QtyConditionMet'],
                    'InDemand': row['InDemand']
                }
        
        # 테이블에 데이터 추가
        self.failed_table.setRowCount(len(grouped_failures))
        row_idx = 0
        
        for match_key, data in grouped_failures.items():
            # 실패 이유 결정
            failure_reason = self.get_failure_reason(data)
            
            # 아이템 셀
            item_cell = QTableWidgetItem(data['Item'])
            item_cell.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 0, item_cell)
            
            # To_site 셀
            to_site_cell = QTableWidgetItem(str(data['To_site']))
            to_site_cell.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 1, to_site_cell)
            
            # 실패 이유 셀
            reason_cell = QTableWidgetItem(failure_reason)
            reason_cell.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            reason_cell.setBackground(QBrush(QColor(255, 200, 200)))
            self.failed_table.setItem(row_idx, 2, reason_cell)
            
            # SOP 셀
            sop_cell = QTableWidgetItem(f"{data['DemandSOP']:,}")
            sop_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 3, sop_cell)
            
            # 생산량 셀
            qty_cell = QTableWidgetItem(f"{data['QualifiedQty']:,}")
            qty_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # 수량 부족인 경우 강조
            if data['QualifiedQty'] < data['DemandSOP']:
                qty_cell.setBackground(QBrush(QColor(255, 235, 235)))
                
            self.failed_table.setItem(row_idx, 4, qty_cell)
            
            row_idx += 1
            
        # 행 높이 조정
        for row in range(self.failed_table.rowCount()):
            self.failed_table.setRowHeight(row, 30)
    
    """실패 이유 반환"""
    def get_failure_reason(self, data):
        if not data['InDemand']:
            return "Not in Demand"
        elif not data['TimeConditionMet'] and not data['QtyConditionMet']:
            return "Time>Due_LT & Qty<SOP"
        elif not data['TimeConditionMet']:
            return "Time>Due_LT"
        elif not data['QtyConditionMet']:
            return "Qty<SOP"
        return "Unknown reason"
    
    """차트 업데이트"""
    def update_chart(self):
        if not self.summary:
            return
        
        # 그래프 초기화
        self.figure.clear()
        
        # 그래프 생성
        ax = self.figure.add_subplot(111)
        
        # 데이터 준비 (소수점 1자리로 반올림)
        labels = ['Qty-based', 'Model-based']
        success_rates = [round(self.summary.get('qty_success_rate', 0), 1), 
                        round(self.summary.get('model_success_rate', 0), 1)]
        failure_rates = [round(100 - rate, 1) for rate in success_rates]  # 소수점 1자리로 반올림
        
        # 색상 설정
        colors = ['#1428A0', '#4CAF50']  
        
        # 바 차트 그리기
        bar_width = 0.35
        x = np.arange(len(labels))
        
        # 성공 바 그리기
        success_bars = ax.bar(x, success_rates, bar_width, label='Success', color=colors)
        
        # 실패 바 그리기 (스택)
        failure_bars = ax.bar(x, failure_rates, bar_width, bottom=success_rates, 
                              label='Failure', color='#FFB6B6')
        
        # 차트 설정
        ax.set_ylim(0, 100)
        ax.set_ylabel('Satisfaction Rate (%)')
        ax.set_title('This Week Shipment Satisfaction Rate')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        
        # 바 위에 텍스트 표시 (소수점 1자리로 표시)
        for i, bar in enumerate(success_bars):
            height = bar.get_height()
            if height > 5:  # 5% 이상일 때만 텍스트 표시
                ax.text(bar.get_x() + bar.get_width()/2., height/2,
                        f'{height:.1f}%',
                        ha='center', va='center', color='white', fontweight='bold')
        
        for i, bar in enumerate(failure_bars):
            height = bar.get_height()
            if height > 5:  # 5% 이상일 때만 텍스트 표시
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_y() + height/2,
                        f'{height:.1f}%',
                        ha='center', va='center', color='black', fontweight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    """출하 실패 아이템을 찾아 시그널 발생"""
    def detect_and_emit_failures(self):
        if self.result_df is None:
            return
        
        # 실패 아이템 정보 저장
        failure_items = {}
        
        for _, row in self.result_df.iterrows():
            if 'IsShippable' in row and not row['IsShippable']:
                item = row['Item']
                
                failure_items[item] = {
                    'item': item,
                    'reason': row.get('FailureReason', 'Unknown reason'),
                    'is_shippable': False
                }
        
        # 실패 아이템 정보 저장 및 시그널 발생
        self.failure_items = failure_items
        self.shipment_status_updated.emit(failure_items)

    """위젯 상태 초기화"""   
    def reset_state(self):
        # 데이터 초기화
        self.result_df = None
        self.summary = None
        self.analysis_df = None
        self.failure_items = {}
        
        # 프로그레스바 초기화
        self.qty_progress.setValue(0)
        self.model_progress.setValue(0)
        self.qty_detail.setText("0 / 0 (0.0%)")  # 소수점 1자리 표시
        self.model_detail.setText("0 / 0 (0.0%)")  # 소수점 1자리 표시
        
        # 통계 테이블 초기화
        for row in range(2):
            for col in range(1, 4):
                self.stats_table.setItem(row, col, QTableWidgetItem("0"))
        
        # 실패 테이블 초기화
        self.failed_table.setRowCount(1)
        empty_message = QTableWidgetItem("No analysis data")
        empty_message.setTextAlignment(Qt.AlignCenter)
        self.failed_table.setItem(0, 0, empty_message)
        self.failed_table.setSpan(0, 0, 1, 5)
        
        # 그래프 초기화
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        self.canvas.draw()
        
        # 출하 실패 항목 초기화 시그널 발생
        self.shipment_status_updated.emit({})
    
    """위젯이 표시될 때 호출됨"""    
    def showEvent(self, event):
        super().showEvent(event)
        # 여기에 필요한 초기화 코드 추가
        
    # """위젯이 숨겨질 때 호출됨"""    
    # def hideEvent(self, event):
    #     super().hideEvent(event)
    #     # 다른 탭으로 전환 시 출하 실패 표시 초기화
    #     self.shipment_status_updated.emit({})