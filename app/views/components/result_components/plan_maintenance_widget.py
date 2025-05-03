from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                          QTabWidget, QTreeWidget, QTreeWidgetItem, QHeaderView,
                          QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush, QCursor
import pandas as pd
import numpy as np
import os
from app.analysis.output.plan_maintenance import PlanMaintenanceRate
from app.utils.week_plan_manager import WeeklyPlanManager

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

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 상단 버튼 영역 추가
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 10)

        # 이전 계획 선택 버튼 추가
        self.select_plan_btn = QPushButton("Select Previous Plan")
        self.select_plan_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.select_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)
        self.select_plan_btn.clicked.connect(self.select_previous_plan)

        # 원래 계획으로 초기화 버튼
        self.reset_btn = QPushButton("Reset to Original")
        self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d; 
                color: white; 
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_to_original)

         # 이전 계획 상태 레이블
        self.plan_status_label = QLabel("No previous plan loaded")
        self.plan_status_label.setStyleSheet("color: #6c757d; font-style: italic;")

        # 버튼 레이아웃에 추가
        button_layout.addWidget(self.select_plan_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch(1)
        button_layout.addWidget(self.plan_status_label)

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
                font-size: 22px;  
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
                font-size: 22px;  
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

    
    """이전 계획 선택 함수"""
    def select_previous_plan(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "이전 계획 파일 선택", 
            "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                # 파일 로드
                previous_plan_df = pd.read_excel(file_path, sheet_name='result')

                if not previous_plan_df.empty:
                    # 이전 계획으로 설정
                    self.previous_plan_path = file_path
                    success = self.plan_analyzer.set_prev_plan(previous_plan_df)
                    self.plan_analyzer.set_first_plan(False)
                    self.is_first_plan = False

                    # 현재 계획이 있으면 유지율 계산
                    if hasattr(self, 'current_plan') and self.current_plan is not None:
                        self.plan_analyzer.set_current_plan(self.current_plan)
                        self.refresh_maintenance_rate()

                    # 상태 레이블 업데이트
                    file_name = os.path.basename(file_path)
                    self.plan_status_label.setText(f"Previous plan: {file_name}")
                    self.plan_status_label.setStyleSheet("color: #1428A0; font-weight: bold;")
                    
                    QMessageBox.information(
                        self, 
                        "이전 계획 로드 성공", 
                        f"이전 계획이 성공적으로 로드되었습니다:\n{file_name}"
                    )
                else:
                    QMessageBox.warning(
                        self, 
                        "로드 실패", 
                        "선택한 파일에 유효한 데이터가 없습니다."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "로드 오류", 
                    f"파일 로드 중 오류가 발생했습니다:\n{str(e)}"
                )


    """레이블 업데이트 함수"""
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


    """트리 위젯 설정 - Item별"""
    def setup_item_tree(self, df):
        if df is None or df.empty:
            return
            
        # 헤더 설정
        header_labels = ["Line", "Shift", "Item", "prev_plan", "curr_plan", "maintenance"]
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
        total_prev = 0
        total_curr = 0
        total_maintenance = 0
        
        for idx, row in df_data.iterrows():
            line = str(row['Line'])
            shift = str(row['Shift'])
            item = str(row['Item'])
            prev_plan = row['prev_plan'] if not pd.isna(row['prev_plan']) else 0
            curr_plan = row['curr_plan'] if not pd.isna(row['curr_plan']) else 0
            maintenance = row['maintenance'] if not pd.isna(row['maintenance']) else 0
            
            # 그룹 키 생성 (Line-Shift)
            group_key = f"{line}_{shift}" if shift else line
            
            if group_key not in groups:
                groups[group_key] = {
                    'line': line,
                    'shift': shift,
                    'items': [],
                    'prev_sum': 0,
                    'curr_sum': 0,
                    'maintenance_sum': 0
                }
            
            # 항목 추가
            groups[group_key]['items'].append({
                'item': item,
                'prev_plan': prev_plan,
                'curr_plan': curr_plan, 
                'maintenance': maintenance
            })
            
            # 그룹 합계 업데이트
            groups[group_key]['prev_sum'] += prev_plan
            groups[group_key]['curr_sum'] += curr_plan
            groups[group_key]['maintenance_sum'] += maintenance
            
            # 전체 합계 업데이트
            total_prev += prev_plan
            total_curr += curr_plan
            total_maintenance += maintenance
        
        """트리 아이템 추가"""
        for group_key, group_data in sorted(groups.items()):
            # 상위 아이템 생성 - Line과 Shift를 함께 표시
            group_label = f"{group_data['line']} {group_data['shift']}"
            
            group_item = QTreeWidgetItem([
                group_data['line'],
                group_data['shift'],
                "",  # Item은 비워둠
                f"{group_data['prev_sum']:,.0f}",
                f"{group_data['curr_sum']:,.0f}",
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
                    f"{item_data['prev_plan']:,.0f}",
                    f"{item_data['curr_plan']:,.0f}",
                    f"{item_data['maintenance']:,.0f}"
                ])
                
                # 데이터 정렬 (수량은 오른쪽 정렬)
                child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
                
                # 변경 여부에 따라 스타일 적용
                if item_data['prev_plan'] != item_data['curr_plan']:
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
            f"{total_prev:,.0f}",
            f"{total_curr:,.0f}",
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

    """트리 위젯 설정 - RMC별"""
    def setup_rmc_tree(self, df):
        if df is None or df.empty:
            return
            
        # 헤더 설정
        header_labels = ["Line", "Shift", "RMC", "prev_plan", "curr_plan", "maintenance"]
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

        # 헤더 정렬 설정
        self.rmc_tree.headerItem().setTextAlignment(0, Qt.AlignCenter)  # Line - 중앙 정렬
        self.rmc_tree.headerItem().setTextAlignment(1, Qt.AlignCenter)  # Shift - 중앙 정렬
        self.rmc_tree.headerItem().setTextAlignment(2, Qt.AlignCenter)  # Item/RMC - 중앙 정렬
        self.rmc_tree.headerItem().setTextAlignment(3, Qt.AlignCenter)  # 이전 계획 - 중앙 정렬
        self.rmc_tree.headerItem().setTextAlignment(4, Qt.AlignCenter)  # 현재 계획 - 중앙 정렬
        self.rmc_tree.headerItem().setTextAlignment(5, Qt.AlignCenter)  # 유지 수량 - 중앙 정렬
        
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]  # 비어있는 행과 총계 행 제외
        
        # Line-Shift별 그룹화
        groups = {}
        total_prev = 0
        total_curr = 0
        total_maintenance = 0
        
        for idx, row in df_data.iterrows():
            line = str(row['Line'])
            shift = str(row['Shift'])
            rmc = str(row['RMC'])
            prev_plan = row['prev_plan'] if not pd.isna(row['prev_plan']) else 0
            curr_plan = row['curr_plan'] if not pd.isna(row['curr_plan']) else 0
            maintenance = row['maintenance'] if not pd.isna(row['maintenance']) else 0
            
            # 그룹 키 생성 (Line-Shift)
            group_key = f"{line}_{shift}" if shift else line
            
            if group_key not in groups:
                groups[group_key] = {
                    'line': line,
                    'shift': shift,
                    'items': [],
                    'prev_sum': 0,
                    'curr_sum': 0,
                    'maintenance_sum': 0
                }
            
            # 항목 추가
            groups[group_key]['items'].append({
                'rmc': rmc,
                'prev_plan': prev_plan,
                'curr_plan': curr_plan, 
                'maintenance': maintenance
            })
            
            # 그룹 합계 업데이트
            groups[group_key]['prev_sum'] += prev_plan
            groups[group_key]['curr_sum'] += curr_plan
            groups[group_key]['maintenance_sum'] += maintenance
            
            # 전체 합계 업데이트
            total_prev += prev_plan
            total_curr += curr_plan
            total_maintenance += maintenance
        
        # 트리 아이템 추가
        for group_key, group_data in sorted(groups.items()):
            # 상위 아이템 생성 - Line과 Shift를 함께 표시
            group_label = f"{group_data['line']} {group_data['shift']}"
            
            group_item = QTreeWidgetItem([
                group_data['line'],
                group_data['shift'],
                "",  # RMC는 비워둠
                f"{group_data['prev_sum']:,.0f}",
                f"{group_data['curr_sum']:,.0f}",
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
                    f"{item_data['prev_plan']:,.0f}",
                    f"{item_data['curr_plan']:,.0f}",
                    f"{item_data['maintenance']:,.0f}"
                ])
                
                # 데이터 정렬 (수량은 오른쪽 정렬)
                child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
                
                # 변경 여부에 따라 스타일 적용
                if item_data['prev_plan'] != item_data['curr_plan']:
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
            f"{total_prev:,.0f}",
            f"{total_curr:,.0f}",
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


    """결과 데이터 설정(이전 계획 자동 탐색)"""
    def set_data(self, result_data, start_date=None, end_date=None):
        if result_data is None or result_data.empty:
            return False
        
        print(f"PlanMaintenanceWidget: 데이터 설정 - 행 수: {len(result_data)}")

        # 현재 계획 저장
        self.current_plan = result_data.copy()

        # 이전 계획 자동 탐색
        if start_date is not None and end_date is not None:
            try:
                plan_manager = WeeklyPlanManager()
                is_first_plan, previous_plan_path, message = plan_manager.detect_previous_plan(
                    start_date, end_date
                )

                # 이전 계획 저장
                self.is_first_plan = is_first_plan
                self.previous_plan_path = previous_plan_path

                # 첫 번째 계획 여부 설정
                self.plan_analyzer.set_first_plan(is_first_plan)
                
                # 메시지 표시
                print(message)
                
                if not is_first_plan and previous_plan_path and os.path.exists(previous_plan_path):
                    try:
                        # 이전 계획 로드
                        previous_df = pd.read_excel(previous_plan_path, sheet_name='result')
                        
                        if not previous_df.empty:
                            # 이전 계획 설정
                            success = self.plan_analyzer.set_prev_plan(previous_df)
                            if success:
                                # 상태 레이블 업데이트
                                file_name = os.path.basename(previous_plan_path)
                                self.plan_status_label.setText(f"Previous plan: {file_name}")
                                self.plan_status_label.setStyleSheet("color: #1428A0; font-weight: bold;")
                                print(f"이전 계획 로드됨: {file_name}")
                        else:
                            print("이전 계획 파일이 비어있습니다.")
                            self.plan_analyzer.set_prev_plan(result_data)
                            self.plan_status_label.setText("First plan (no previous data)")
                            self.plan_status_label.setStyleSheet("color: #6c757d; font-style: italic;")
                    except Exception as e:
                        print(f"이전 계획 로드 중 오류: {str(e)}")
                        self.plan_analyzer.set_prev_plan(result_data)
                        self.plan_status_label.setText("Error loading previous plan")
                        self.plan_status_label.setStyleSheet("color: #dc3545; font-style: italic;")
                else:
                    # 첫 번째 계획이거나 이전 계획 없음
                    self.plan_analyzer.set_prev_plan(result_data)
                    self.plan_status_label.setText(f"First plan - {message}")
                    self.plan_status_label.setStyleSheet("color: #6c757d; font-style: italic;")
            except Exception as e:
                print(f"이전 계획 감지 중 오류: {str(e)}")
                self.plan_analyzer.set_prev_plan(result_data)
                self.plan_status_label.setText("Error detecting previous plan")
                self.plan_status_label.setStyleSheet("color: #dc3545; font-style: italic;")
        else:
            # 날짜가 없는 경우 현재 데이터를 원본으로 설정
            self.plan_analyzer.set_prev_plan(result_data)
            self.plan_status_label.setText("No date information")
            self.plan_status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        
        # 현재 계획 설정
        self.plan_analyzer.set_current_plan(result_data)
        
        # 유지율 계산 및 UI 업데이트
        self.refresh_maintenance_rate()
        
        return True
    

    """유지율을 다시 계산하고 UI 업데이트"""
    def refresh_maintenance_rate(self):
        # item별 유지율 계산
        item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate()
        self.item_maintenance_rate = item_rate if item_rate is not None else 0.0
        
        # RMC별 유지율 계산
        rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate()
        self.rmc_maintenance_rate = rmc_rate if rmc_rate is not None else 0.0

        # 로그 출력
        item_rate_str = f"{self.item_maintenance_rate:.2f}%" if self.item_maintenance_rate is not None else "N/A"
        rmc_rate_str = f"{self.rmc_maintenance_rate:.2f}%" if self.rmc_maintenance_rate is not None else "N/A"
        print(f"계산된 유지율 - Item: {item_rate_str}, RMC: {rmc_rate_str}")
        
        # 트리 위젯 초기화
        self.item_tree.clear()
        self.rmc_tree.clear()
        
        # 트리 위젯 설정
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

    
    """수량 업데이트 및 테이블 갱신 함수"""
    def update_quantity(self, line, time, item, new_qty, demand=None):
        if self.plan_analyzer is None:
            return False
        
        print(f"PlanMaintenanceWidget: 수량 업데이트 - {line}, {time}, {item}, {new_qty}, {demand}")
        
        # 수량 업데이트 
        success = self.plan_analyzer.update_quantity(line, time, item, new_qty, demand)
        
        if success:
            print("수량 업데이트 성공, 유지율 재계산 중...")
            # 트리 위젯 초기화
            self.item_tree.clear()
            self.rmc_tree.clear()
            
            # 조정된 계획과 비교하여 유지율 계산
            item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate(compare_with_adjusted=True)
            rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate(compare_with_adjusted=True)
            
            # 계산된 유지율 저장
            self.item_maintenance_rate = item_rate if item_rate is not None else 0.0
            self.rmc_maintenance_rate = rmc_rate if rmc_rate is not None else 0.0
            
            # 트리 위젯 재구성
            if item_df is not None and not item_df.empty:
                self.setup_item_tree(item_df)
            
            if rmc_df is not None and not rmc_df.empty:
                self.setup_rmc_tree(rmc_df)
            
            # 선택된 탭에 따라 유지율 레이블 업데이트
            self.update_rate_label(self.tab_widget.currentIndex())
            
            # 트리 위젯 갱신 강제
            self.item_tree.update()
            self.rmc_tree.update()
            self.update()
            
            return True
        else:
            print(f"수량 업데이트 실패: {line}, {time}, {item}, {new_qty}")
            return False
        

    """현재 데이터 반환"""
    def get_current_plan(self):
        """현재 계획 데이터 반환"""
        if self.plan_analyzer is None:
            return None
        return self.plan_analyzer.get_current_plan()
    

    """조정된 계획 데이터 반환"""
    def get_adjusted_plan(self):
        """조정된 계획 데이터 반환"""
        if self.plan_analyzer is None:
            return None
        return self.plan_analyzer.get_adjusted_plan()
    
    
    """원본 계획으로 초기화"""
    def reset_to_original(self):
        if self.plan_analyzer is None:
            return False
        
        success = self.plan_analyzer.reset_to_prev()
        
        if success:
            self.refresh_maintenance_rate()
            QMessageBox.information(
                self, 
                "초기화 성공", 
                "계획이 원본 상태로 초기화되었습니다."
            )

            return True
        else:
            QMessageBox.warning(
                self, 
                "초기화 실패", 
                "원본 계획이 없어 초기화할 수 없습니다."
            )
            return False