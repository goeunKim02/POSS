from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                          QTabWidget, QTreeWidget, QTreeWidgetItem, QHeaderView,
                          QFrame, QSplitter, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush, QCursor
import pandas as pd
import numpy as np
from app.analysis.output.plan_maintenance import PlanMaintenanceRate

class PlanMaintenanceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plan_analyzer = PlanMaintenanceRate()
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border: none;
            }
            QWidget > QFrame, QWidget > QWidget {
                border: none;
            }
        """)
        self.init_ui()

        # 개발 모드에서만 자동 테스트 데이터 로드 (옵션)
        import os
        if os.environ.get('DEV_MODE') == '1':
            self.load_excel_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        from PyQt5.QtWidgets import QPushButton
        

        # 상단 버튼 영역 추가
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 10)

        # 파일 로드 버튼
        load_btn = QPushButton("엑셀 파일 로드")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2A3DB2;
            }
        """)
        load_btn.clicked.connect(self.load_excel_data)
        button_layout.addWidget(load_btn)
        button_layout.addStretch(1)

        # 메인 레이아웃에 버튼 위젯 추가 (info_widget 앞에)
        main_layout.addWidget(button_widget)

        # 상단 정보 위젯
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: white; border-radius: 8px; border: none;")
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(15, 10, 15, 10)
        
        # 유지율 제목과 값을 한 줄에 표시
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(13)
        
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(13)
        value_font.setBold(True)
        
        self.rate_title_label = QLabel("Item별 유지율 :")
        self.rate_title_label.setFont(title_font)
        self.rate_title_label.setStyleSheet("color: #333333;")
        
        self.item_rate_label = QLabel("100%")
        self.item_rate_label.setFont(value_font)
        self.item_rate_label.setStyleSheet("color: #1428A0;")
        
        info_layout.addWidget(self.rate_title_label)
        info_layout.addWidget(self.item_rate_label)
        info_layout.addStretch(1)  # 오른쪽 여백
        
        # 컨텐츠 위젯 (흰색 배경)
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white; border-radius: 8px; ")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setCursor(QCursor(Qt.PointingHandCursor))
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #F5F5F5;
                color: black;
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 20px; 
            }
            QTabBar::tab:!selected {
                background-color: #E4E3E3;  
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 20px;  
            }
            QTabBar::tab {
                padding: 8px 16px;
                min-width: 150px;
                margin-left: 7px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-family: Arial, sans-serif;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-bottom: none;
                font-size: 20px;  
            }
            QTabBar::tab::first { margin-left: 10px; }
        """)

        # Item별 탭
        self.item_tab = QWidget()
        item_layout = QVBoxLayout(self.item_tab)
        item_layout.setContentsMargins(10, 10, 10, 10)
        
        # 트리 위젯
        self.item_tree = QTreeWidget()
        self.item_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #dddddd;  /* 테이블 전체에 테두리 추가 */
                border: none;
                background-color: white;
                alternate-background-color: #f9f9f9;
                font-size: 20px;  
                outline: none;
                gridline-color: #dddddd;  /* 그리드 라인 색상 설정 */
            }
            QTreeWidget::item {
                height: 48px;  
                border-bottom: 1px solid #f0f0f0;
                padding-left: 8px;
                padding-right: 12px;
                border-right: 1px solid #e0e0e0;  /* 수직 구분선 추가 */
            }
            QTreeWidget::item:selected {
                background-color: #f0f5ff;
                color: #1428A0;
                border: none;
                border-right: 1px solid #e0e0e0;  /* 선택 시에도 구분선 유지 */
            }
            QHeaderView::section {
                background-color: white;
                padding: 12px; 
                border: none;
                border-bottom: 2px solid #1428A0;  /* 헤더 밑줄 강화 및 색상 변경 */
                border-right: 1px solid #e0e0e0;  /* 헤더 수직 구분선 추가 */
                font-weight: bold;
                color: #333333;
                font-size: 20px;  
            }
            QTreeView::branch {
                background-color: transparent;
                border: none;
            }
        """)

        self.item_tree.setAlternatingRowColors(True)  # 행 배경색 교차 적용
        item_layout.addWidget(self.item_tree)
        
        # RMC별 탭
        self.rmc_tab = QWidget()
        rmc_layout = QVBoxLayout(self.rmc_tab)
        rmc_layout.setContentsMargins(10, 10, 10, 10)
        
        # RMC별 트리 위젯
        self.rmc_tree = QTreeWidget()
        self.rmc_tree.setStyleSheet(self.item_tree.styleSheet())  # 같은 스타일 적용
        self.rmc_tree.setAlternatingRowColors(True)  # 행 배경색 교차 적용
        rmc_layout.addWidget(self.rmc_tree)
                
        # 탭 추가
        self.tab_widget.addTab(self.item_tab, "Item별 유지율")
        self.tab_widget.addTab(self.rmc_tab, "RMC별 유지율")
        
        content_layout.addWidget(self.tab_widget)
        
        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(info_widget)
        main_layout.addWidget(content_widget, 1)  # 1의 stretch 값으로 나머지 공간 채우기
        
        # 탭 변경 시 유지율 레이블 업데이트
        self.tab_widget.currentChanged.connect(self.update_rate_label)


    # 레이블 업데이트 함수
    def update_rate_label(self, index):
        if index == 0:  # Item별 탭
            self.rate_title_label.setText("Item별 유지율 :")
            if hasattr(self, 'item_maintenance_rate'):
                if self.item_maintenance_rate is not None:
                    # 정수로 표시
                    rate_value = int(self.item_maintenance_rate)
                    self.item_rate_label.setText(f"{rate_value}%")
                    
                    # 색상 설정
                    if rate_value >= 90:
                        self.item_rate_label.setStyleSheet("color: #1AB394;") # 녹색
                    elif rate_value >= 70:
                        self.item_rate_label.setStyleSheet("color: #1428A0;") # 파란색
                    else:
                        self.item_rate_label.setStyleSheet("color: #F8AC59;") # 주황색
                else:
                    self.item_rate_label.setText("N/A")
                    self.rate_progress.setValue(0)
        else:  # RMC별 탭
            self.rate_title_label.setText("RMC별 유지율 :")
            if hasattr(self, 'rmc_maintenance_rate'):
                if self.rmc_maintenance_rate is not None:
                    # 정수로 표시
                    rate_value = int(self.rmc_maintenance_rate)
                    self.item_rate_label.setText(f"{rate_value}%")
                    
                    # 색상 설정
                    if rate_value >= 90:
                        self.item_rate_label.setStyleSheet("color: #1AB394;") # 녹색
                    elif rate_value >= 70:
                        self.item_rate_label.setStyleSheet("color: #1428A0;") # 파란색
                    else:
                        self.item_rate_label.setStyleSheet("color: #F8AC59;") # 주황색
                else:
                    self.item_rate_label.setText("N/A")
                    self.rate_progress.setValue(0)


    # 트리 위젯 설정 - Item별
    def setup_item_tree(self, df):
        if df is None or df.empty:
            return
            
        # 헤더 설정
        header_labels = ["Line", "Shift", "Item", "이전 계획", "현재 계획", "유지 수량"]
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
        
        # 헤더 정렬 설정
        self.item_tree.headerItem().setTextAlignment(0, Qt.AlignCenter)  # Line - 중앙 정렬
        self.item_tree.headerItem().setTextAlignment(1, Qt.AlignCenter)  # Shift - 중앙 정렬
        self.item_tree.headerItem().setTextAlignment(2, Qt.AlignCenter)  # Item/RMC - 중앙 정렬
        self.item_tree.headerItem().setTextAlignment(3, Qt.AlignCenter)  # 이전 계획 - 중앙 정렬
        self.item_tree.headerItem().setTextAlignment(4, Qt.AlignCenter)  # 현재 계획 - 중앙 정렬
        self.item_tree.headerItem().setTextAlignment(5, Qt.AlignCenter)  # 유지 수량 - 중앙 정렬
        
        
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
                f"{group_data['pre_sum']:,.0f}",
                f"{group_data['post_sum']:,.0f}",
                f"{group_data['maintenance_sum']:,.0f}"
            ])
            
            # 상위 아이템 스타일 설정
            for i in range(6):
                group_item.setBackground(i, QBrush(QColor('#f0f5ff')))  # 연한 푸른색 배경
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
                    f"{item_data['pre_plan']:,.0f}",
                    f"{item_data['post_plan']:,.0f}",
                    f"{item_data['maintenance']:,.0f}"
                ])

                # 자식 아이템 폰트 크기 증가
                for i in range(6):
                    font = child_item.font(i)
                    child_item.setFont(i, font)
                
                # 데이터 정렬 (수량은 오른쪽 정렬)
                child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
                
                # 변경 여부에 따라 스타일 적용
                if item_data['pre_plan'] != item_data['post_plan']:
                    # 변경된 경우 볼드체로 표시
                    font = child_item.font(4)
                    font.setBold(True)
                    child_item.setFont(4, font)
                    child_item.setForeground(4, QBrush(QColor('#F8AC59')))  # 변경된 값 하이라이트
                
                group_item.addChild(child_item)
            
            # 기본적으로 그룹 확장
            group_item.setExpanded(True)
        
        # 총계 항목 추가
        total_item = QTreeWidgetItem([
            "Total",
            "",
            "",
            f"{total_pre:,.0f}",
            f"{total_post:,.0f}",
            f"{total_maintenance:,.0f}"
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
        header_labels = ["Line", "Shift", "RMC", "이전 계획", "현재 계획", "유지 수량"]
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
                f"{group_data['pre_sum']:,.0f}",
                f"{group_data['post_sum']:,.0f}",
                f"{group_data['maintenance_sum']:,.0f}"
            ])
            
            # 상위 아이템 스타일 설정
            for i in range(6):
                group_item.setBackground(i, QBrush(QColor('#f0f5ff')))  # 연한 푸른색 배경
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
                    f"{item_data['pre_plan']:,.0f}",
                    f"{item_data['post_plan']:,.0f}",
                    f"{item_data['maintenance']:,.0f}"
                ])

                # 자식 아이템 폰트 크기 증가
                for i in range(6):
                    font = child_item.font(i)
                    child_item.setFont(i, font)
                
                # 데이터 정렬 (수량은 오른쪽 정렬)
                child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
                
                # 변경 여부에 따라 스타일 적용
                if item_data['pre_plan'] != item_data['post_plan']:
                    # 변경된 경우 볼드체로 표시
                    font = child_item.font(4)
                    font.setBold(True)
                    child_item.setFont(4, font)
                    child_item.setForeground(4, QBrush(QColor('#F8AC59')))  # 변경된 값 하이라이트
                
                group_item.addChild(child_item)
            
            # 기본적으로 그룹 확장
            group_item.setExpanded(True)
        
        # 총계 항목 추가
        total_item = QTreeWidgetItem([
            "Total",
            "",
            "",
            f"{total_pre:,.0f}",
            f"{total_post:,.0f}",
            f"{total_maintenance:,.0f}"
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
        self.item_maintenance_rate = item_rate if item_rate is not None else 0.0
        
        # RMC별 유지율 계산
        rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate()
        self.rmc_maintenance_rate = rmc_rate if rmc_rate is not None else 0.0

        # None 값 체크 후 출력
        item_rate_str = f"{self.item_maintenance_rate:.2f}%" if self.item_maintenance_rate is not None else "N/A"
        rmc_rate_str = f"{self.rmc_maintenance_rate:.2f}%" if self.rmc_maintenance_rate is not None else "N/A"
        
        print(f"계산된 유지율 - Item: {item_rate_str}, RMC: {rmc_rate_str}")
        
        # 트리 위젯 초기화
        self.item_tree.clear()
        self.rmc_tree.clear()
        
        # 트리 위젯 설정 (item_df 또는 rmc_df가 None인 경우 고려)
        if item_df is not None and not item_df.empty:
            self.setup_item_tree(item_df)
        else:
            print("Item별 유지율 데이터가 없습니다.")
        
        if rmc_df is not None and not rmc_df.empty:
            self.setup_rmc_tree(rmc_df)
        else:
            print("RMC별 유지율 데이터가 없습니다.")
        
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
            self.item_maintenance_rate = item_rate if item_rate is not None else 0.0
            
            # RMC별 유지율 재계산
            rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate()
            self.rmc_maintenance_rate = rmc_rate if rmc_rate is not None else 0.0
            
            # None 값 체크 후 출력
            item_rate_str = f"{self.item_maintenance_rate:.2f}%" if self.item_maintenance_rate is not None else "N/A"
            rmc_rate_str = f"{self.rmc_maintenance_rate:.2f}%" if self.rmc_maintenance_rate is not None else "N/A"
            print(f"새로운 유지율 - Item: {item_rate_str}, RMC: {rmc_rate_str}")
            
            # 트리 위젯 초기화
            self.item_tree.clear()
            self.rmc_tree.clear()
            
            # 트리 위젯 설정 (item_df 또는 rmc_df가 None인 경우 고려)
            if item_df is not None and not item_df.empty:
                self.setup_item_tree(item_df)
            else:
                print("Item별 유지율 데이터가 없습니다.")
            
            if rmc_df is not None and not rmc_df.empty:
                self.setup_rmc_tree(rmc_df)
            else:
                print("RMC별 유지율 데이터가 없습니다.")
            
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
    
    def load_excel_data(self, file_path=None):
        """
        테스트 함수
        엑셀 파일을 로드하여 '이전 계획'으로 설정
        
        Parameters:
            file_path (str): 엑셀 파일 경로. None이면 파일 선택 대화상자 표시
        """
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            import os
            
            # 디버깅 메시지 추가
            print("파일 로드 함수 시작")
            
            # 파일 경로가 없으면 선택 대화상자 표시
            if file_path is None or not isinstance(file_path, str):
                print("파일 선택 대화상자 표시 시도")
                
                # 대화상자 옵션 설정
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog  # 네이티브 대화상자 사용 안 함
                
                # 절대 경로 사용
                initial_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
                
                # 대화상자 실행
                file_path, _ = QFileDialog.getOpenFileName(
                    self,                  # 부모 위젯
                    "엑셀 파일 선택",       # 제목
                    initial_dir,           # 초기 디렉토리
                    "Excel Files (*.xlsx *.xls);;All Files (*)",  # 필터
                    options=options
                )
                
                print(f"선택된 파일 경로: {file_path}")
                
                # 파일이 선택되지 않았으면 함수 종료
                if not file_path:
                    print("파일 선택 취소됨")
                    return False
            
            # 파일 경로가 문자열이 아니면 오류 처리
            if not isinstance(file_path, str):
                print(f"유효하지 않은 파일 경로 타입: {type(file_path)}")
                QMessageBox.warning(self, "오류", "유효하지 않은 파일 경로입니다.")
                return False
            
            # 파일 경로 검증
            if not os.path.exists(file_path):
                print(f"파일이 존재하지 않습니다: {file_path}")
                QMessageBox.warning(self, "오류", f"파일이 존재하지 않습니다: {file_path}")
                return False
                
            print(f"파일 로드 시도: {file_path}")
            
            # 엑셀 파일 로드
            df = pd.read_excel(file_path)
            print(f"엑셀 파일 로드 완료: {file_path}")
            print(f"데이터 행 수: {len(df)}")
            
            # 필수 컬럼 확인
            required_columns = ['Line', 'Time', 'Item', 'Qty']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"필수 컬럼이 없습니다: {', '.join(missing_columns)}")
                QMessageBox.warning(self, "오류", f"필수 컬럼이 없습니다: {', '.join(missing_columns)}")
                return False
            
            # RMC 컬럼이 없는 경우 추가
            if 'RMC' not in df.columns:
                print("RMC 컬럼이 없습니다. Item에서 추출합니다.")
                try:
                    # RMC 추출 (예: 'AB-P973U2DU952' -> 'P973U2')
                    df['RMC'] = df['Item'].str.extract(r'([A-Z]\d{3,4}[A-Z]\d)')
                except Exception as e:
                    print(f"RMC 추출 실패: {e}")
                    # 실패한 경우 임시 RMC 컬럼 추가
                    df['RMC'] = df['Item'].apply(lambda x: x[:6] if len(str(x)) >= 6 else x)
            
            # 원본 데이터 설정 (중요 수정 부분)
            self.plan_analyzer.set_first_plan(False)  # 유지율 계산 활성화
            
            # 직접 original_plan만 설정 (current_plan은 설정하지 않음)
            self.plan_analyzer.original_plan = df.copy()
            
            # 현재 계획이 이미 있는지 확인
            current_plan_exists = (hasattr(self.plan_analyzer, 'current_plan') and 
                                self.plan_analyzer.current_plan is not None and 
                                not self.plan_analyzer.current_plan.empty)
            
            if current_plan_exists:
                print("기존 현재 계획이 있음, 유지율 계산 시작")
                
                # item별 유지율 계산
                item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate()
                self.item_maintenance_rate = item_rate if item_rate is not None else 0.0
                
                # RMC별 유지율 계산
                rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate()
                self.rmc_maintenance_rate = rmc_rate if rmc_rate is not None else 0.0
                
                # 트리 위젯 업데이트
                self.item_tree.clear()
                self.rmc_tree.clear()
                
                if item_df is not None and not item_df.empty:
                    self.setup_item_tree(item_df)
                    print(f"Item별 유지율: {self.item_maintenance_rate:.2f}%")
                else:
                    print("Item별 유지율 데이터가 없습니다.")
                
                if rmc_df is not None and not rmc_df.empty:
                    self.setup_rmc_tree(rmc_df)
                    print(f"RMC별 유지율: {self.rmc_maintenance_rate:.2f}%")
                else:
                    print("RMC별 유지율 데이터가 없습니다.")
                
                # 선택된 탭에 따라 유지율 레이블 업데이트
                self.update_rate_label(self.tab_widget.currentIndex())
                
            else:
                # 현재 계획이 없는 경우, 사용자에게 알림
                print("현재 계획이 없습니다. 왼쪽 패널의 데이터가 필요합니다.")
                QMessageBox.information(self, "알림", "이전 계획이 설정되었습니다. 왼쪽 패널의 데이터가 현재 계획으로 설정되면 유지율이 계산됩니다.")
            
            # 로드 성공 메시지
            QMessageBox.information(self, "성공", "이전 계획 데이터가 성공적으로 로드되었습니다.")
            return True
            
        except Exception as e:
            import traceback
            print(f"엑셀 파일 로드 중 오류 발생: {e}")
            traceback.print_exc()
            
            # 사용자에게 오류 표시
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "오류", f"엑셀 파일 로드 중 오류가 발생했습니다:\n{str(e)}")
            return False