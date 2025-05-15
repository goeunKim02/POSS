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
        main_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        # 상단 섹션 - 통계 정보
        self.top_section = QWidget()
        top_layout = QVBoxLayout(self.top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 배경색 및 테두리 제거
        self.top_section.setStyleSheet("background-color: transparent; border: none;")
        
        top_title = QLabel("Shipment Satisfaction Rate")
        top_title.setFont(QFont("Arial", 12, QFont.Bold))
        top_layout.addWidget(top_title)
        
        # 만족률 카드 컨테이너
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        cards_container.setStyleSheet("background-color: transparent; border: none;")
        
        # 수량 기준 만족률 카드
        qty_card = QFrame()
        qty_card.setFrameShape(QFrame.NoFrame)
        qty_card.setStyleSheet("background-color: transparent; border: none;")
        qty_card_layout = QVBoxLayout(qty_card)
        
        qty_title = QLabel("Qty-based Satisfaction Rate")
        qty_title.setFont(QFont("Arial", 10, QFont.Bold))
        qty_card_layout.addWidget(qty_title)
        
        # 프로그레스바
        self.qty_progress = QProgressBar()
        self.qty_progress.setTextVisible(True)
        self.qty_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #F0F0F0;
                color: black;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #5D92EB;
                border-radius: 5px;
            }
        """)
        qty_card_layout.addWidget(self.qty_progress)
        
        self.qty_detail = QLabel("0 / 0 (0.0%)")  # 소수점 1자리 표시
        self.qty_detail.setAlignment(Qt.AlignCenter)
        qty_card_layout.addWidget(self.qty_detail)
        
        # 모델 기준 만족률 카드
        model_card = QFrame()
        model_card.setFrameShape(QFrame.NoFrame)
        model_card.setStyleSheet("background-color: transparent; border: none;")
        model_card_layout = QVBoxLayout(model_card)
        
        model_title = QLabel("Model-based Satisfaction Rate")
        model_title.setFont(QFont("Arial", 10, QFont.Bold))
        model_card_layout.addWidget(model_title)
        
        # 프로그레스바 유지
        self.model_progress = QProgressBar()
        self.model_progress.setTextVisible(True)
        self.model_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #F0F0F0;
                color: black; /* 텍스트 색상을 항상 검은색으로 */
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #76C47E; /* 더 밝은 녹색으로 변경 */
                border-radius: 5px;
            }
        """)
        model_card_layout.addWidget(self.model_progress)
        
        self.model_detail = QLabel("0 / 0 (0.0%)")
        self.model_detail.setAlignment(Qt.AlignCenter)
        model_card_layout.addWidget(self.model_detail)
        
        # 카드 추가
        cards_layout.addWidget(qty_card)
        cards_layout.addWidget(model_card)
        top_layout.addWidget(cards_container)
        
        # 통계 테이블
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Category", "Total", "Success", "Success Rate"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 통계 테이블 스타일시트
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
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        
        # 기본 통계 행 추가
        self.stats_table.setRowCount(2)
        self.stats_table.setItem(0, 0, QTableWidgetItem("Quantity (Qty)"))
        self.stats_table.setItem(1, 0, QTableWidgetItem("Model"))
        
        top_layout.addWidget(self.stats_table)
        
        # 여백
        top_layout.addSpacing(5)
        
        # 하단 섹션 - 출하 실패 모델 테이블
        self.bottom_section = QWidget()
        bottom_layout = QVBoxLayout(self.bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # 배경색 및 테두리
        self.bottom_section.setStyleSheet("background-color: transparent; border: none;")
        
        bottom_title = QLabel("Failed Shipment Models")
        bottom_title.setFont(QFont("Arial", 12, QFont.Bold))
        bottom_layout.addWidget(bottom_title)
        
        self.failed_table = QTableWidget()
        self.failed_table.setColumnCount(7)
        
        # 컬럼 이름 잘림 문제 수정 - 더 짧은 이름으로 변경하고 줄바꿈 추가
        self.failed_table.setHorizontalHeaderLabels([
            "Item", "To_site", "Time", "Due_LT", "Required\n(SOP)", "Production\n(Qty)", "Production/Required\n(Qty/SOP)"
        ])
        
        # 헤더 높이 증가 - 줄바꿈된 텍스트가 보이도록
        self.failed_table.horizontalHeader().setMinimumHeight(40)
        
        # 컬럼 너비 개별 설정 (비율로)
        self.failed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # 수직 헤더 숨김
        self.failed_table.verticalHeader().setVisible(False)
        self.failed_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.failed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 테이블 스타일시트 업데이트 - 헤더 높이 문제 해결
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
                min-height: 40px;
                max-height: 40px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        
        bottom_layout.addWidget(self.failed_table)
        
        # 스플리터에 위젯 추가
        splitter.addWidget(self.top_section)
        splitter.addWidget(self.bottom_section)
        
        # 초기 비율 설정 (1:1)
        splitter.setSizes([500, 500])
        
        main_layout.addWidget(splitter)

    """당주 출하 분석 실행"""    
    def run_analysis(self, result_data=None):
        try:
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
            
            # 컬럼 너비 설정
            self.adjust_column_widths()
            
            # 실패 아이템 정보 전달
            self.detect_and_emit_failures()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    """요약 정보 업데이트"""
    def update_summary_info(self):
        if not self.summary:
            return
        
        # 전체 생산량과 성공량 가져오기
        total_produced_qty = int(self.summary.get('total_produced_qty', 0))  # 정수형으로 변환
        success_qty = int(self.summary.get('success_qty', 0))  # 정수형으로 변환
        
        # 수량 기준 성공률 계산 (전체 생산량 기준으로 변경)
        qty_rate = round((success_qty / total_produced_qty * 100) if total_produced_qty > 0 else 0, 1)
        
        # 모델 관련 데이터
        success_models = int(self.summary.get('success_models', 0))  # 정수형으로 변환
        total_models = int(self.summary.get('total_models', 0))  # 정수형으로 변환
        model_rate = round(self.summary.get('model_success_rate', 0), 1)  # 소수점 1자리로 반올림
        
        # 프로그레스바 업데이트
        self.qty_progress.setValue(int(qty_rate))
        self.qty_progress.setFormat(f"{qty_rate:.1f}%")  # 프로그레스바 텍스트 형식 설정
        
        self.model_progress.setValue(int(model_rate))
        self.model_progress.setFormat(f"{model_rate:.1f}%")  # 프로그레스바 텍스트 형식 설정
        
        # 상세 정보 업데이트 - 전체 생산량 기준으로 변경
        self.qty_detail.setText(f"{success_qty:,} / {total_produced_qty:,} ({qty_rate:.1f}%)")
        self.model_detail.setText(f"{success_models} / {total_models} ({model_rate:.1f}%)")
        
        # 통계 테이블 업데이트 - 전체 생산량 표시 및 성공률 변경
        self.stats_table.setItem(0, 1, QTableWidgetItem(f"{total_produced_qty:,}"))
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
    
    """컬럼 너비 조정"""
    def adjust_column_widths(self):
        # 전체 너비 얻기
        total_width = self.failed_table.viewport().width()
        
        # 컬럼별 너비 비율 설정 - 조정
        self.failed_table.setColumnWidth(0, int(total_width * 0.21))  # Item
        self.failed_table.setColumnWidth(1, int(total_width * 0.09))  # To_site
        self.failed_table.setColumnWidth(2, int(total_width * 0.07))  # Time
        self.failed_table.setColumnWidth(3, int(total_width * 0.09))  # Due_LT
        self.failed_table.setColumnWidth(4, int(total_width * 0.13))  # Required(SOP)
        self.failed_table.setColumnWidth(5, int(total_width * 0.13))  # Production(Qty)
        self.failed_table.setColumnWidth(6, int(total_width * 0.25))  # Production/Required
        
        # 헤더 텍스트 정렬 조정 - 컬럼명이 잘리지 않도록
        header = self.failed_table.horizontalHeader()
        for col in range(self.failed_table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
        
        # 자동 크기 조정 후 다시 Interactive로 변경하여 사용자 조정 가능하게
        header.setSectionResizeMode(QHeaderView.Interactive)
    
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
            self.failed_table.setSpan(0, 0, 1, 7)
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
                    'Time': int(row['Time']),  # 정수형으로 변환
                    'Due_LT': int(row['Due_LT']),  # 정수형으로 변환
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
            # 아이템 셀
            item_cell = QTableWidgetItem(data['Item'])
            item_cell.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 0, item_cell)
            
            # To_site 셀
            to_site_cell = QTableWidgetItem(str(data['To_site']))
            to_site_cell.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 1, to_site_cell)
            
            # Time 셀
            time_cell = QTableWidgetItem(str(data['Time']))
            time_cell.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            # Time이 Due_LT보다 큰 경우 강조표시
            if data['Time'] > data['Due_LT']:
                time_cell.setBackground(QBrush(QColor(255, 200, 200)))
            self.failed_table.setItem(row_idx, 2, time_cell)
            
            # Due_LT 셀
            due_lt_cell = QTableWidgetItem(str(data['Due_LT']))
            due_lt_cell.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 3, due_lt_cell)
            
            # SOP 셀
            sop_cell = QTableWidgetItem(f"{data['DemandSOP']:,}")
            sop_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.failed_table.setItem(row_idx, 4, sop_cell)
            
            # 생산량 셀
            qty_cell = QTableWidgetItem(f"{data['QualifiedQty']:,}")
            qty_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # 수량 부족인 경우 강조
            if data['QualifiedQty'] < data['DemandSOP']:
                qty_cell.setBackground(QBrush(QColor(255, 235, 235)))
                
            self.failed_table.setItem(row_idx, 5, qty_cell)
            
            # Production/Required 비율 셀
            if data['DemandSOP'] > 0:
                ratio = data['QualifiedQty'] / data['DemandSOP'] * 100
                ratio_str = f"{data['QualifiedQty']:,}/{data['DemandSOP']:,} ({ratio:.1f}%)"
            else:
                ratio = 0
                ratio_str = f"{data['QualifiedQty']:,}/{data['DemandSOP']:,} (0.0%)"
                
            ratio_cell = QTableWidgetItem(ratio_str)
            ratio_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # 비율에 따른 색상 설정
            if ratio < 80:
                ratio_cell.setBackground(QBrush(QColor(255, 200, 200)))  # 빨간색
            elif ratio < 100:
                ratio_cell.setBackground(QBrush(QColor(255, 235, 200)))  # 주황색
                
            self.failed_table.setItem(row_idx, 6, ratio_cell)
            
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
        self.qty_progress.setFormat("0.0%")  # 초기 텍스트 형식 설정
        
        self.model_progress.setValue(0)
        self.model_progress.setFormat("0.0%")  # 초기 텍스트 형식 설정
        
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
        self.failed_table.setSpan(0, 0, 1, 7)  # 컬럼 수에 맞게 스팬 조정
        
        # 컬럼 너비 재설정
        self.adjust_column_widths()
        
        # 출하 실패 항목 초기화 시그널 발생
        self.shipment_status_updated.emit({})
    
    """위젯이 표시될 때 호출됨"""    
    def showEvent(self, event):
        super().showEvent(event)
        # 컬럼 너비 조정
        self.adjust_column_widths()
        
    """위젯 크기가 변경될 때 호출됨"""
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 테이블 컬럼 너비 재조정
        self.adjust_column_widths()
        
    """위젯이 숨겨질 때 호출됨"""    
    def hideEvent(self, event):
        super().hideEvent(event)
        # 다른 탭으로 전환 시 출하 실패 표시 초기화
        self.shipment_status_updated.emit({})