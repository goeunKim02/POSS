from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                          QTabWidget, QTreeWidget, QTreeWidgetItem, QHeaderView,
                          QFrame, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush
import pandas as pd
import numpy as np
from app.analysis.output.plan_maintenance import PlanMaintenanceRate

class PlanMaintenanceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plan_analyzer = PlanMaintenanceRate()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 카드 프레임
        card_frame = QFrame()
        card_frame.setObjectName("cardFrame")
        card_frame.setStyleSheet("""
            #cardFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 10px 10px 20px 10px;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 15, 20, 15)

        # 유지율 제목 레이블
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(18)
        title_font.setBold(True)
        
        self.rate_title_label = QLabel("Item별 계획 유지율:")
        self.rate_title_label.setFont(title_font)
        self.rate_title_label.setStyleSheet("color: #333333;")
        self.rate_title_label.setAlignment(Qt.AlignCenter)
        
        # 유지율 값 레이블
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(18)
        value_font.setBold(True)
        
        self.item_rate_label = QLabel("100.00%")
        self.item_rate_label.setFont(value_font)
        self.item_rate_label.setStyleSheet("color: #1428A0;")
        self.item_rate_label.setAlignment(Qt.AlignCenter)
        
        # 레이블 레이아웃에 추가
        card_layout.addWidget(self.rate_title_label)
        card_layout.addWidget(self.item_rate_label)
        
        # 메인 레이아웃에 카드 추가
        main_layout.addWidget(card_frame)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # 탭을 더 모던하게 표시
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 0px;
                background: white;
                padding: 0px;
                margin: 0px 10px 10px 10px;
            }
            QTabBar::tab {
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 25px;
            }
            QTabBar::tab:selected {
                background: #1428A0;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                color: #555555;
            }
            QTabBar::tab:hover:!selected {
                background: #e0e0e0;
            }
        """)

        # Item별 탭
        self.item_tab = QWidget()
        item_layout = QVBoxLayout(self.item_tab)
        item_layout.setContentsMargins(0, 0, 0, 0)
        
        # 트리 위젯으로 변경
        self.item_tree = QTreeWidget()
        self.item_tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: white;
                alternate-background-color: #f9f9f9;
                font-size: 25px;
            }
            QTreeWidget::item {
                height: 45px;
                border-bottom: 1px solid #f0f0f0;
                padding-left: 5px;
                padding-right: 10px;
            }
            QTreeWidget::item:selected {
                background-color: #e8f0fe;
                color: #1428A0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 10px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 2px solid #1428A0;
                font-weight: bold;
                color: #333333;
                font-size: 25px;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(:/images/branch-closed.png);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(:/images/branch-open.png);
            }
        """)
        self.item_tree.setAlternatingRowColors(True)  # 행 배경색 교차 적용
        item_layout.addWidget(self.item_tree)
        
        # RMC별 탭
        self.rmc_tab = QWidget()
        rmc_layout = QVBoxLayout(self.rmc_tab)
        rmc_layout.setContentsMargins(0, 0, 0, 0)
        
        # RMC별 트리 위젯
        self.rmc_tree = QTreeWidget()
        self.rmc_tree.setStyleSheet(self.item_tree.styleSheet())  # 같은 스타일 적용
        self.rmc_tree.setAlternatingRowColors(True)  # 행 배경색 교차 적용
        rmc_layout.addWidget(self.rmc_tree)
        
        # 탭 추가
        self.tab_widget.addTab(self.item_tab, "Item")
        self.tab_widget.addTab(self.rmc_tab, "RMC")
        
        main_layout.addWidget(self.tab_widget)
        
        # 탭 변경 시 유지율 레이블 업데이트
        self.tab_widget.currentChanged.connect(self.update_rate_label)

    # 레이블 업데이트 함수
    def update_rate_label(self, index):
        if index == 0:  # Item별 탭
            self.rate_title_label.setText("Item별 계획 유지율:")
            if hasattr(self, 'item_maintenance_rate'):
                self.item_rate_label.setText(f"{self.item_maintenance_rate:.2f}%")
        else:  # RMC별 탭
            self.rate_title_label.setText("RMC별 계획 유지율:")
            if hasattr(self, 'rmc_maintenance_rate'):
                self.item_rate_label.setText(f"{self.rmc_maintenance_rate:.2f}%")

    # 트리 위젯 설정 - Item별
    def setup_item_tree(self, df):
        if df is None or df.empty:
            return
            
        # 헤더 설정
        header_labels = ["Line", "Shift", "Item", "Pre Plan", "Post Plan", "Maintenance"]
        self.item_tree.setHeaderLabels(header_labels)
        self.item_tree.setColumnCount(len(header_labels))
        
        # 헤더 설정
        header = self.item_tree.header()
        for i in range(len(header_labels)):
            if i < 3:  # 텍스트 컬럼은 내용에 맞게
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:  # 숫자 컬럼은 고정 크기
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                header.resizeSection(i, 150)
        
        header.setStretchLastSection(False)
        
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]  # 비어있는 행과 총계 행 제외
        
        # Line-Shift별 그룹화
        groups = {}
        total_pre = 0
        total_post = 0
        total_maintenance = 0
        
        for idx, row in df_data.iterrows():
            line = str(row['Line'])
            shift = str(row['Shift'])
            item = str(row['Item'])
            pre_plan = row['pre_plan'] if not pd.isna(row['pre_plan']) else 0
            post_plan = row['post_plan'] if not pd.isna(row['post_plan']) else 0
            maintenance = row['maintenance'] if not pd.isna(row['maintenance']) else 0
            
            # 그룹 키 생성 (Line-Shift)
            group_key = f"{line}_{shift}" if shift else line
            
            if group_key not in groups:
                groups[group_key] = {
                    'line': line,
                    'shift': shift,
                    'items': [],
                    'pre_sum': 0,
                    'post_sum': 0,
                    'maintenance_sum': 0
                }
            
            # 항목 추가
            groups[group_key]['items'].append({
                'item': item,
                'pre_plan': pre_plan,
                'post_plan': post_plan, 
                'maintenance': maintenance
            })
            
            # 그룹 합계 업데이트
            groups[group_key]['pre_sum'] += pre_plan
            groups[group_key]['post_sum'] += post_plan
            groups[group_key]['maintenance_sum'] += maintenance
            
            # 전체 합계 업데이트
            total_pre += pre_plan
            total_post += post_plan
            total_maintenance += maintenance
        
        # 트리 아이템 추가
        for group_key, group_data in sorted(groups.items()):
            # 상위 아이템 생성 - Line과 Shift를 함께 표시
            group_label = f"{group_data['line']} {group_data['shift']}"
            
            group_item = QTreeWidgetItem([
                group_data['line'],
                group_data['shift'],
                "",  # Item은 비워둠
                f"{group_data['pre_sum']:,.1f}",
                f"{group_data['post_sum']:,.1f}",
                f"{group_data['maintenance_sum']:,.1f}"
            ])
            
            # 상위 아이템 스타일 설정
            for i in range(6):
                group_item.setBackground(i, QBrush(QColor('#e6e6ff')))  # 연한 푸른색 배경
                font = group_item.font(i)
                font.setBold(True)
                group_item.setFont(i, font)
            
            # 데이터 정렬 (수량은 오른쪽 정렬)
            group_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
            group_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
            group_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
            
            self.item_tree.addTopLevelItem(group_item)
            
            # 자식 아이템 추가
            for item_data in sorted(group_data['items'], key=lambda x: x['item']):
                child_item = QTreeWidgetItem([
                    "",  # Line은 비워둠
                    "",  # Shift는 비워둠
                    item_data['item'],
                    f"{item_data['pre_plan']:,.1f}",
                    f"{item_data['post_plan']:,.1f}",
                    f"{item_data['maintenance']:,.1f}"
                ])
                
                # 데이터 정렬 (수량은 오른쪽 정렬)
                child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
                
                # 짝수/홀수 행 색상
                if len(group_data['items']) % 2 == 1:
                    child_item.setBackground(0, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(1, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(2, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(3, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(4, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(5, QBrush(QColor('#f9f9f9')))
                
                group_item.addChild(child_item)
            
            # 기본적으로 그룹 확장
            group_item.setExpanded(True)
        
        # 총계 항목 추가
        total_item = QTreeWidgetItem([
            "Total",
            "",
            "",
            f"{total_pre:,.1f}",
            f"{total_post:,.1f}",
            f"{total_maintenance:,.1f}"
        ])
        
        # 총계 스타일 설정
        for i in range(6):
            total_item.setBackground(i, QBrush(QColor('#1428A0')))
            total_item.setForeground(i, QBrush(QColor('white')))
            font = total_item.font(i)
            font.setBold(True)
            total_item.setFont(i, font)
            
        # 데이터 정렬 (수량은 오른쪽 정렬)
        total_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        self.item_tree.addTopLevelItem(total_item)

    # 트리 위젯 설정 - RMC별
    def setup_rmc_tree(self, df):
        if df is None or df.empty:
            return
            
        # 헤더 설정
        header_labels = ["Line", "Shift", "RMC", "Pre Plan", "Post Plan", "Maintenance"]
        self.rmc_tree.setHeaderLabels(header_labels)
        self.rmc_tree.setColumnCount(len(header_labels))
        
        # 헤더 설정
        header = self.rmc_tree.header()
        for i in range(len(header_labels)):
            if i < 3:  # 텍스트 컬럼은 내용에 맞게
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:  # 숫자 컬럼은 고정 크기
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                header.resizeSection(i, 150)
        
        header.setStretchLastSection(False)
        
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]  # 비어있는 행과 총계 행 제외
        
        # Line-Shift별 그룹화
        groups = {}
        total_pre = 0
        total_post = 0
        total_maintenance = 0
        
        for idx, row in df_data.iterrows():
            line = str(row['Line'])
            shift = str(row['Shift'])
            rmc = str(row['RMC'])
            pre_plan = row['pre_plan'] if not pd.isna(row['pre_plan']) else 0
            post_plan = row['post_plan'] if not pd.isna(row['post_plan']) else 0
            maintenance = row['maintenance'] if not pd.isna(row['maintenance']) else 0
            
            # 그룹 키 생성 (Line-Shift)
            group_key = f"{line}_{shift}" if shift else line
            
            if group_key not in groups:
                groups[group_key] = {
                    'line': line,
                    'shift': shift,
                    'items': [],
                    'pre_sum': 0,
                    'post_sum': 0,
                    'maintenance_sum': 0
                }
            
            # 항목 추가
            groups[group_key]['items'].append({
                'rmc': rmc,
                'pre_plan': pre_plan,
                'post_plan': post_plan, 
                'maintenance': maintenance
            })
            
            # 그룹 합계 업데이트
            groups[group_key]['pre_sum'] += pre_plan
            groups[group_key]['post_sum'] += post_plan
            groups[group_key]['maintenance_sum'] += maintenance
            
            # 전체 합계 업데이트
            total_pre += pre_plan
            total_post += post_plan
            total_maintenance += maintenance
        
        # 트리 아이템 추가
        for group_key, group_data in sorted(groups.items()):
            # 상위 아이템 생성 - Line과 Shift를 함께 표시
            group_label = f"{group_data['line']} {group_data['shift']}"
            
            group_item = QTreeWidgetItem([
                group_data['line'],
                group_data['shift'],
                "",  # RMC는 비워둠
                f"{group_data['pre_sum']:,.1f}",
                f"{group_data['post_sum']:,.1f}",
                f"{group_data['maintenance_sum']:,.1f}"
            ])
            
            # 상위 아이템 스타일 설정
            for i in range(6):
                group_item.setBackground(i, QBrush(QColor('#e6e6ff')))  # 연한 푸른색 배경
                font = group_item.font(i)
                font.setBold(True)
                group_item.setFont(i, font)
            
            # 데이터 정렬 (수량은 오른쪽 정렬)
            group_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
            group_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
            group_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
            
            self.rmc_tree.addTopLevelItem(group_item)
            
            # 자식 아이템 추가
            for item_data in sorted(group_data['items'], key=lambda x: x['rmc']):
                child_item = QTreeWidgetItem([
                    "",  # Line은 비워둠
                    "",  # Shift는 비워둠
                    item_data['rmc'],
                    f"{item_data['pre_plan']:,.1f}",
                    f"{item_data['post_plan']:,.1f}",
                    f"{item_data['maintenance']:,.1f}"
                ])
                
                # 데이터 정렬 (수량은 오른쪽 정렬)
                child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
                
                # 짝수/홀수 행 색상
                if len(group_data['items']) % 2 == 1:
                    child_item.setBackground(0, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(1, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(2, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(3, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(4, QBrush(QColor('#f9f9f9')))
                    child_item.setBackground(5, QBrush(QColor('#f9f9f9')))
                
                group_item.addChild(child_item)
            
            # 기본적으로 그룹 확장
            group_item.setExpanded(True)
        
        # 총계 항목 추가
        total_item = QTreeWidgetItem([
            "Total",
            "",
            "",
            f"{total_pre:,.1f}",
            f"{total_post:,.1f}",
            f"{total_maintenance:,.1f}"
        ])
        
        # 총계 스타일 설정
        for i in range(6):
            total_item.setBackground(i, QBrush(QColor('#1428A0')))
            total_item.setForeground(i, QBrush(QColor('white')))
            font = total_item.font(i)
            font.setBold(True)
            total_item.setFont(i, font)
            
        # 데이터 정렬 (수량은 오른쪽 정렬)
        total_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        self.rmc_tree.addTopLevelItem(total_item)

    # 결과 데이터로 분석기 초기화 및 테이블 업데이트
    def set_data(self, result_data):
        if result_data is None or result_data.empty:
            return False
        
        print(f"PlanMaintenanceWidget: 데이터 설정 - 행 수: {len(result_data)}")
        
        # 계획 유지율 분석
        self.plan_analyzer.set_original_plan(result_data)
        
        # Item별 유지율 계산
        item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate()
        self.item_maintenance_rate = item_rate
        
        # RMC별 유지율 계산
        rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate()
        self.rmc_maintenance_rate = rmc_rate
        
        print(f"계산된 유지율 - Item: {item_rate:.2f}%, RMC: {rmc_rate:.2f}%")
        
        # 트리 위젯 초기화
        self.item_tree.clear()
        self.rmc_tree.clear()
        
        # 트리 위젯 설정
        self.setup_item_tree(item_df)
        self.setup_rmc_tree(rmc_df)
        
        # 선택된 탭에 따라 유지율 레이블 업데이트
        self.update_rate_label(self.tab_widget.currentIndex())
        
        return True
    
    # 수량 업데이트 및 테이블 갱신 함수
    def update_quantity(self, line, time, item, new_qty, demand=None):
        if self.plan_analyzer is None:
            return False
        
        print(f"PlanMaintenanceWidget: 수량 업데이트 - {line}, {time}, {item}, {new_qty}, {demand}")
        
        # 수량 업데이트 
        success = self.plan_analyzer.update_quantity(line, time, item, new_qty, demand)
        
        if success:
            print("수량 업데이트 성공, 유지율 재계산 중...")
            
            # item별 유지율 재계산
            item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate()
            self.item_maintenance_rate = item_rate
            
            # RMC별 유지율 재계산
            rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate()
            self.rmc_maintenance_rate = rmc_rate
            
            print(f"새로운 유지율 - Item: {item_rate:.2f}%, RMC: {rmc_rate:.2f}%")
            
            # 트리 위젯 초기화
            self.item_tree.clear()
            self.rmc_tree.clear()
            
            # 트리 위젯 설정
            self.setup_item_tree(item_df)
            self.setup_rmc_tree(rmc_df)
            
            # 선택된 탭에 따라 유지율 업데이트
            self.update_rate_label(self.tab_widget.currentIndex())
            
            return True
        else:
            print(f"수량 업데이트 실패: {line}, {time}, {item}, {new_qty}")
            return False
    
    # 원본 계획으로 reset
    def reset_to_original(self):
        if self.plan_analyzer is None:
            return False
        
        success = self.plan_analyzer.reset_to_original()
        
        if success:
            self.set_data(self.plan_analyzer.get_current_plan())
            
        return success