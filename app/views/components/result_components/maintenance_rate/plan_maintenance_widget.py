from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                          QTabWidget, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor, QFontMetrics
from app.views.components.result_components.maintenance_rate.plan_data_manager import PlanDataManager
from app.views.components.result_components.maintenance_rate.maintenance_table_widget import ItemMaintenanceTable, RMCMaintenanceTable
from app.views.components.common.enhanced_message_box import EnhancedMessageBox

"""계획 유지율 표시 위젯"""
class PlanMaintenanceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 데이터 매니저 생성
        self.data_manager = PlanDataManager()
        
        # UI 초기화
        self.setup_ui()
        
    """UI 초기화"""
    def setup_ui(self):
        # 메인 레이아웃
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 데이터 없음 메시지
        self.no_data_message = QLabel("Please Load to Data")
        self.no_data_message.setAlignment(Qt.AlignCenter)
        self.no_data_message.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            background-color: transparent;
            border: none;
        """)
        
        # 데이터 있을 때 표시할 컨테이너
        self.content_container = QWidget()
        self.content_container.setStyleSheet("border: none;")  
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        # 초기 상태 설정
        self.main_layout.addWidget(self.no_data_message)
        self.main_layout.addWidget(self.content_container)
        self.content_container.hide()
        
        # UI 컴포넌트 생성
        self.create_toolbar()
        self.create_info_section()
        self.create_tabs()
        
    """툴바 영역 생성"""
    def create_toolbar(self):
        # 버튼 위젯 생성
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 10)
        
        # 이전 계획 선택 버튼
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
        
        # 계획 상태 레이블
        self.plan_status_label = QLabel("No previous plan loaded")
        self.plan_status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        
        # 레이아웃에 추가
        button_layout.addWidget(self.select_plan_btn)
        button_layout.addStretch(1)
        button_layout.addWidget(self.plan_status_label)
        
        # 컨텐츠 레이아웃에 추가
        self.content_layout.addWidget(button_widget)
        
    """정보 섹션 생성"""
    def create_info_section(self):
        # 상단 정보 위젯
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: white; border-radius: 8px; border: none;")
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(15, 10, 15, 10)
        
        # 유지율 제목과 값
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(13)
        
        value_font = QFont()
        value_font.setFamily("Arial")
        value_font.setPointSize(13)
        value_font.setBold(True)
        
        self.rate_title_label = QLabel("Item Maintenance Rate :")
        self.rate_title_label.setFont(title_font)
        self.rate_title_label.setStyleSheet("color: #333333;")
        
        self.item_rate_label = QLabel("100%")
        self.item_rate_label.setFont(value_font)
        self.item_rate_label.setStyleSheet("color: #1428A0;")
        
        info_layout.addWidget(self.rate_title_label)
        info_layout.addWidget(self.item_rate_label)
        info_layout.addStretch(1)
        
        # 컨텐츠 레이아웃에 추가
        self.content_layout.addWidget(info_widget)
        
    """탭 생성"""
    def create_tabs(self):
        # 컨텐츠 위젯
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent; border: none;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(400)  # 최소 높이 설정
        self.tab_widget.setMaximumHeight(600)  # 최대 높이 제한
        self.tab_widget.tabBar().setCursor(QCursor(Qt.PointingHandCursor))
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: black;
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 16px; 
            }
            QTabBar::tab:!selected {
                background-color: #E4E3E3;  
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 16px;  
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-left: 7px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-family: Arial, sans-serif;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-bottom: none;
                font-size: 16px;  
            }
            QTabBar::tab::first { margin-left: 10px; }
        """)


        tab_bar = self.tab_widget.tabBar()
        tab_bar.setElideMode(Qt.ElideNone)  # 텍스트 생략 방지
        tab_bar.setExpanding(True)  # 탭이 전체 너비를 차지하지 않도록

        # Item별 탭
        self.item_tab = QWidget()
        item_layout = QVBoxLayout(self.item_tab)
        item_layout.setContentsMargins(10, 10, 10, 10)
        
        # Item별 테이블 위젯
        self.item_table = ItemMaintenanceTable()
        item_layout.addWidget(self.item_table)
        
        # RMC별 탭
        self.rmc_tab = QWidget()
        rmc_layout = QVBoxLayout(self.rmc_tab)
        rmc_layout.setContentsMargins(10, 10, 10, 10)
        
        # RMC별 테이블 위젯
        self.rmc_table = RMCMaintenanceTable()
        rmc_layout.addWidget(self.rmc_table)
        
        # 탭 추가
        self.tab_widget.addTab(self.item_tab, "Item Maintenance Rate")
        self.tab_widget.addTab(self.rmc_tab, "RMC Maintenance Rate")

        # 탭 바 설정 - 자동 크기 조정을 위한 커스텀 탭바 설정
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setExpanding(False)
        
        # 폰트 설정
        font = tab_bar.font()
        font.setPointSize(16)
        tab_bar.setFont(font)
        
        # 동적으로 탭 크기 조정
        font_metrics = QFontMetrics(font)
        
        # 각 탭의 너비를 텍스트에 맞게 조정
        tab_bar.setTabSizeHint = lambda index: self.get_tab_size_hint(index, font_metrics)
        
        content_layout.addWidget(self.tab_widget)
        
        # 컨텐츠 레이아웃에 추가
        self.content_layout.addWidget(content_widget, 1)
        
        # 탭 변경 시 유지율 레이블 업데이트
        self.tab_widget.currentChanged.connect(self.update_rate_label)

    def get_tab_size_hint(self, index, font_metrics):
        """탭 크기 힌트 계산"""
        from PyQt5.QtCore import QSize
        tab_text = self.tab_widget.tabText(index)
        text_width = font_metrics.width(tab_text)
        return QSize(text_width + 40, 40)  # 여백 추가
        
    
    """이전 계획 선택"""
    def select_previous_plan(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Plan File", 
            "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)",
            options=options
        )
        
        if file_path:
            success, message = self.data_manager.load_previous_plan(file_path)
            
            if success:
                # 상태 레이블 업데이트
                self.plan_status_label.setText(f"Previous plan: {message}")
                self.plan_status_label.setStyleSheet("color: #1428A0; font-weight: bold;")
                
                # 유지율 다시 계산
                self.refresh_maintenance_rate()
                
                EnhancedMessageBox.show_validation_success(
                    self, 
                    "Previous Plan Loaded Successfully", 
                    f"Previous plan has been loaded successfully:\n{message}"
                )
            else:
                EnhancedMessageBox.show_validation_error(
                    self, 
                    "Load Failed", 
                    f"Failed to load previous plan: {message}"
                )
                
    """탭 인덱스에 따라 유지율 레이블 업데이트"""
    def update_rate_label(self, index):
        if index == 0:  # Item별 탭
            self.rate_title_label.setText("Item Maintenance Rate :")
            rate_value = getattr(self, 'item_maintenance_rate', None)
        else:  # RMC별 탭
            self.rate_title_label.setText("RMC Maintenance Rate :")
            rate_value = getattr(self, 'rmc_maintenance_rate', None)
            
        if rate_value is not None:
            # 정수로 표시
            rate_int = int(rate_value)
            self.item_rate_label.setText(f"{rate_int}%")
            
            # 색상 설정
            if rate_int >= 90:
                self.item_rate_label.setStyleSheet("color: #1AB394;")  # 녹색
            elif rate_int >= 70:
                self.item_rate_label.setStyleSheet("color: #1428A0;")  # 파란색
            else:
                self.item_rate_label.setStyleSheet("color: #F8AC59;")  # 주황색
        else:
            self.item_rate_label.setText("None")
            
    def set_data(self, result_data, start_date=None, end_date=None):
        """결과 데이터 설정"""
        if result_data is None or result_data.empty:
            # 데이터가 없는 경우
            self.no_data_message.show()
            self.content_container.hide()
            return False
            
        # 데이터가 있는 경우 UI 요소 표시
        self.no_data_message.hide()
        self.content_container.show()
        
        print(f"PlanMaintenanceWidget: 데이터 설정 - 행 수: {len(result_data)}")
        
        # 현재 계획 설정
        self.data_manager.set_current_plan(result_data)
        
        # 이전 계획 자동 탐색
        if start_date is not None and end_date is not None:
            success, message = self.data_manager.detect_previous_plan(start_date, end_date)
            print(f"이전 계획 감지 결과: success={success}, message={message}")


            # 이전 계획 감지 상태 확인
            print(f"plan_manager.is_first_plan: {self.data_manager.is_first_plan}")
            print(f"plan_manager.previous_plan_path: {self.data_manager.previous_plan_path}")
            
            # 상태 레이블 업데이트
            if success:
                self.plan_status_label.setText(f"Previous plan: {message}")
                self.plan_status_label.setStyleSheet("color: #1428A0; font-weight: bold;")
            else:
                self.plan_status_label.setText(message)
                self.plan_status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        
        # 유지율 계산 및 UI 업데이트
        self.refresh_maintenance_rate()
        
        return True
        
    def refresh_maintenance_rate(self):
        """유지율 다시 계산하고 UI 업데이트"""
        # 유지율 계산
        item_df, item_rate, rmc_df, rmc_rate = self.data_manager.calculate_maintenance_rates()

        # 계산된 유지율 저장
        self.item_maintenance_rate = item_rate if item_rate is not None else 0.0
        self.rmc_maintenance_rate = rmc_rate if rmc_rate is not None else 0.0
        
        # 테이블 위젯 데이터 설정
        if item_df is not None and not item_df.empty:
            self.item_table.populate_data(item_df, self.data_manager.modified_item_keys)
        else:
            print("Item별 유지율 데이터가 없습니다.")
            
        if rmc_df is not None and not rmc_df.empty:
            self.rmc_table.populate_data(rmc_df, self.data_manager.modified_item_keys)
        else:
            print("RMC별 유지율 데이터가 없습니다.")
            
        # 선택된 탭에 따라 유지율 레이블 업데이트
        self.update_rate_label(self.tab_widget.currentIndex())
        

    """수량 업데이트 및 UI 갱신"""
    def update_quantity(self, line, time, item, new_qty):
        # print(f"PlanMaintenanceWidget - 수량 업데이트 시도: line={line}, time={time}, item={item}, new_qty={new_qty}")

        # 명시적 타입 변환 추가
        try:
            if isinstance(time, str) and time.strip().isdigit():
                time = int(time.strip())
            if isinstance(new_qty, str) and new_qty.strip().isdigit():
                new_qty = int(new_qty.strip())
            
            print(f"PlanMaintenanceWidget - 변환 후: time={time} ({type(time)}), new_qty={new_qty} ({type(new_qty)})")
        except (ValueError, TypeError) as e:
            print(f"타입 변환 실패: {e}")
            
        success = self.data_manager.update_quantity(line, time, item, new_qty)
        
        if success:
            print("수량 업데이트 성공, 유지율 재계산 중...")
            self.refresh_maintenance_rate()
            return True
        else:
            print(f"수량 업데이트 실패: {line}, {time}, {item}, {new_qty}")
            return False
        

    """조정된 계획 데이터 반환"""
    def get_adjusted_plan(self):
        if hasattr(self, 'data_manager') and self.data_manager is not None:
            if hasattr(self.data_manager, 'plan_analyzer') and self.data_manager.plan_analyzer is not None:
                return self.data_manager.plan_analyzer.get_adjusted_plan()
        return None