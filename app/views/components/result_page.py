from PyQt5.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, 
                             QFrame, QSplitter, QStackedWidget, QTableWidget, QHeaderView, QToolTip, 
                             QTableWidgetItem, QSizePolicy, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QCursor, QFont, QColor, QBrush
import pandas as pd

from app.views.components.result_components.portcapa_widget import PortCapaWidget
from ..components.result_components.modified_left_section import ModifiedLeftSection
from ..components.visualization.mpl_canvas import MplCanvas
from ..components.visualization.visualization_updater import VisualizationUpdater
from app.analysis.output.daily_capa_utilization import CapaUtilization
from app.analysis.output.capa_ratio import CapaRatioAnalyzer
from ..components.result_components.maintenance_rate.plan_maintenance_widget import PlanMaintenanceWidget
from app.utils.export_manager import ExportManager
from app.core.output.adjustment_validator import PlanAdjustmentValidator
from app.views.components.result_components.shipment_widget import ShipmentWidget
from app.resources.styles.result_style import ResultStyles 
from app.views.components.result_components.split_allocation_widget import SplitAllocationWidget
from app.views.components.result_components.items_container import ItemsContainer


class ResultPage(QWidget):
    export_requested = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.capa_ratio_data = None
        self.data_changed_count = 0
        self.utilization_data = None # 가동률 데이터 저장 변수
        self.result_data = None # 결과 데이터 저장 변수
        self.material_analyzer = None  # 자재 부족량 분석기 추가
        self.pre_assigned_items = set()  # 사전할당된 아이템 저장
        self.shipment_widget = None # 당주 출하 위젯 저장 변수
        self.split_allocation_widget = None # 분산 배치 분석 위젯 저장 변수
        self.validation_errors = {}  # 현재 발생한 검증 에러들
        self.error_items = set()   # 에러가 있는 아이템 목록

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # 레이아웃 설정
        result_layout = QVBoxLayout(self)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(0)

        # 타이틀 프레임
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("QFrame { min-height:61px; max-height:62px; border:none }")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(25, 10, 15, 5)
        title_layout.setSpacing(0)

        # 타이틀 레이블
        title_label = QLabel("Result")

        # QFont를 사용하여 더 두껍게 설정
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(99)
        title_label.setFont(font)

        title_layout.addWidget(title_label, 0, Qt.AlignVCenter)
        title_layout.addStretch(1)

        # 버튼 레이아웃
        export_layout = QHBoxLayout()
        export_layout.setContentsMargins(0, 0, 0, 0)  # 여백 수정
        export_layout.setSpacing(10)

        # Export 버튼
        export_btn = QPushButton()
        export_btn.setText("Export")
        export_btn.setFixedSize(130, 40)
        export_btn.setCursor(QCursor(Qt.PointingHandCursor))
        export_btn.clicked.connect(self.export_results)
        export_btn.setStyleSheet(ResultStyles.EXPORT_BUTTON_STYLE)

        # Report 버튼
        report_btn = QPushButton()
        report_btn.setText("Report")
        report_btn.setFixedSize(140, 40)
        report_btn.setCursor(QCursor(Qt.PointingHandCursor))
        report_btn.setStyleSheet(ResultStyles.EXPORT_BUTTON_STYLE)

        export_layout.addWidget(export_btn)
        export_layout.addWidget(report_btn)

        # 버튼 레이아웃을 타이틀 레이아웃에 추가
        title_layout.addLayout(export_layout)

        # 타이틀 프레임을 메인 레이아웃에 추가
        result_layout.addWidget(title_frame)

        # 수평 스플리터 생성 (왼쪽 | 오른쪽)
        main_horizontal_splitter = QSplitter(Qt.Horizontal)
        main_horizontal_splitter.setHandleWidth(10)
        main_horizontal_splitter.setStyleSheet("QSplitter::handle { background-color: #F5F5F5; }")
        main_horizontal_splitter.setContentsMargins(10, 10, 10, 10)

        # 왼쪽 컨테이너
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 2px solid #cccccc;")

        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # 드래그 가능한 테이블 위젯 추가
        self.left_section = ModifiedLeftSection()
        # 데이터 변경 시그널 연결
        self.left_section.data_changed.connect(self.on_data_changed)
        # 셀 이동 시그널 연결
        self.left_section.cell_moved.connect(self.on_cell_moved)
        # 아이템 데이터 변경 시그널 연결
        self.left_section.item_data_changed.connect(self.on_item_data_changed)

        left_layout.addWidget(self.left_section)\
        
        # 오른쪽 영역을 위아래로 분리하기 위한 수직 스플리터
        right_vertical_splitter = QSplitter(Qt.Vertical)
        right_vertical_splitter.setHandleWidth(10)
        right_vertical_splitter.setStyleSheet("QSplitter::handle { background-color: #F5F5F5; }")

        # 하단 컨테이너
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 2px solid #cccccc;")
        
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # 에러 표시 위젯
        self.error_display_widget = QWidget()
        self.error_display_layout = QVBoxLayout(self.error_display_widget)
        self.error_display_layout.setContentsMargins(5, 5, 5, 5)
        self.error_display_layout.setSpacing(5)
        self.error_display_layout.setAlignment(Qt.AlignTop) 
        
        # # 스크롤 가능한 에러 영역
        self.error_scroll_area = QScrollArea()
        self.error_scroll_area.setWidgetResizable(True)
        self.error_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.error_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.error_scroll_area.setWidget(self.error_display_widget)
        self.error_scroll_area.hide()  # 초기에는 숨김
        
        bottom_layout.addWidget(self.error_scroll_area)

        # 오른쪽 상단 섹션 
        right_top_frame = QFrame()
        right_top_frame.setFrameShape(QFrame.StyledPanel)
        right_top_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 2px solid #cccccc;")

        right_top_layout = QVBoxLayout(right_top_frame)

        # 지표 버튼
        button_group_layout = QHBoxLayout()
        button_group_layout.setSpacing(5)
        button_group_layout.setContentsMargins(10, 10, 10, 5)

        # 버튼들 사이 균등 간격 설정 (필요시)
        button_group_layout.setAlignment(Qt.AlignCenter)  # 중앙 정렬

        self.viz_buttons = []
        viz_types = ["Capa", "Material", "PortCapa", "Plan", "Shipment", "SplitView"]

        # 시각화 콘텐츠를 표시할 스택 위젯
        self.viz_stack = QStackedWidget()

        # 시각화 캔버스 저장
        self.viz_canvases = []

        # 버튼과 콘텐츠 페이지 생성
        for i, btn_text in enumerate(viz_types):
            btn = QPushButton(btn_text)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE if i == 0 else ResultStyles.INACTIVE_BUTTON_STYLE)
            btn.clicked.connect(lambda checked, idx=i: self.switch_viz_page(idx))

             # 균등한 크기로 설정
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFixedHeight(40)  # 높이만 고정
            
            btn.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE if i == 0 else ResultStyles.INACTIVE_BUTTON_STYLE)
            btn.clicked.connect(lambda checked, idx=i: self.switch_viz_page(idx))

            button_group_layout.addWidget(btn)
            self.viz_buttons.append(btn)

            # 해당 버튼에 대응하는 콘텐츠 페이지 생성
            page = QWidget()
            page_layout = QVBoxLayout(page)
            
            # tab 유형 별 처리 
            if btn_text == 'Capa':
                capa_canvas = MplCanvas(width=4, height=5, dpi=100)
                page_layout.addWidget(capa_canvas)
                self.viz_canvases.append(capa_canvas)
                
                # 여백 추가
                page_layout.addSpacing(5)
                
                util_canvas = MplCanvas(width=5, height=5, dpi=100)
                page_layout.addWidget(util_canvas)
                self.viz_canvases.append(util_canvas)
            elif btn_text == 'Plan':
                # 계획 유지율 위젯 생성
                self.plan_maintenance_widget = PlanMaintenanceWidget()
                page_layout.addWidget(self.plan_maintenance_widget)
            elif btn_text == 'Material':
                # 자재 부족량 분석 페이지
                material_page = QWidget()
                material_layout = QVBoxLayout(material_page)
                material_layout.setContentsMargins(0, 0, 0, 0)  # 페이지 여백
                
                # 차트 컨테이너와 여백 추가
                chart_container = QWidget()
                chart_container.setStyleSheet("""
                    QWidget { 
                        border: none;
                        outline: none;
                        background-color: white;
                    }
                """)
                chart_layout = QVBoxLayout(chart_container)
                chart_layout.setContentsMargins(0, 10, 15, 10)  # 여백 다시 정상화
                
                # 자재 부족량 차트 추가
                material_canvas = MplCanvas(width=6, height=3, dpi=100)  # 높이도 다시 정상화
                # 캔버스 자체의 스타일 설정
                material_canvas.setStyleSheet("""
                    QWidget, QFrame { 
                        border: none;
                        outline: none;
                        background-color: white;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
                # 차트 여백 최적화 - 이제 텍스트가 작으므로 여백 줄일 수 있음
                material_canvas.fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)  # 0.15로 줄임
                material_canvas.fig.patch.set_facecolor('white')
                material_canvas.fig.patch.set_visible(True)
                
                chart_layout.addWidget(material_canvas)
                
                # 차트 컨테이너를 메인 레이아웃에 추가
                material_layout.addWidget(chart_container, 2)
                
                # 테이블과 차트 사이에 최소한의 여백만 추가
                material_layout.addSpacing(10)
                
                # 자재 부족 항목 테이블 추가
                self.shortage_items_table = QTableWidget()
                self.shortage_items_table.setColumnCount(4)
                self.shortage_items_table.setHorizontalHeaderLabels(["Model", "Material", "Shortage", "Shortage Rate (%)"])
                self.shortage_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
                # 행 번호(맨 왼쪽 열) 중앙 정렬 설정
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
                
                self.shortage_items_table.setStyleSheet("""
                    QTableWidget {
                        border: 1px solid #ffffff;
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
                
                # 테이블에 툴팁 추가
                self.shortage_items_table.setMouseTracking(True)
                self.shortage_items_table.cellEntered.connect(self.show_shortage_tooltip)
                
                # 테이블 비중 크게 증가
                material_layout.addWidget(self.shortage_items_table, 2) 
                
                # 페이지 자체에도 스타일 적용
                material_page.setStyleSheet("""
                    QWidget { 
                        border: none;
                        outline: none;
                        background-color: white;
                    }
                """)
                page_layout.addWidget(material_page)
                
                # 캔버스 저장
                self.viz_canvases.append(material_canvas)
            elif btn_text == 'PortCapa':
                self.portcapa_widget = PortCapaWidget()
                self.portcapa_widget.setStyleSheet("""
                    QWidget { 
                        border: none;
                        outline: none;
                        background-color: white;
                    }
                """)
                page_layout.addWidget(self.portcapa_widget)
            elif btn_text == 'Shipment':
                # 당주 출하 위젯
                self.shipment_widget = ShipmentWidget()
                self.shipment_widget.shipment_status_updated.connect(self.on_shipment_status_updated)
                page_layout.addWidget(self.shipment_widget)
            elif btn_text =='SplitView':
                self.split_allocation_widget = SplitAllocationWidget()
                page_layout.addWidget(self.split_allocation_widget)
            

            # Performance 탭의 초기 시각화 생성
            if btn_text == 'Capa':
                # Capa 차트 초기화 (첫 번째 캔버스)
                self.create_initial_visualization(self.viz_canvases[0], "Capa")
                # Utilization 차트 초기화 (두 번째 캔버스)
                self.create_initial_visualization(self.viz_canvases[1], "Utilization")
            
            # 스택 위젯에 페이지 추가
            self.viz_stack.addWidget(page)

        # 레이아웃에 버튼 그룹과 스택 위젯 추가
        right_top_layout.addLayout(button_group_layout)
        right_top_layout.addWidget(self.viz_stack)

        # 오른쪽 수직 스플리터에 상단과 하단 프레임 추가
        right_vertical_splitter.addWidget(right_top_frame)
        right_vertical_splitter.addWidget(bottom_frame)
        
        # 상단과 하단의 비율 설정 
        right_vertical_splitter.setSizes([750, 250])
        right_vertical_splitter.setStretchFactor(0, 8)  # 상단 30%
        right_vertical_splitter.setStretchFactor(1, 2)  # 하단 70%

        # 수평 스플리터에 왼쪽 프레임과 오른쪽 수직 스플리터 추가
        main_horizontal_splitter.addWidget(left_frame)
        main_horizontal_splitter.addWidget(right_vertical_splitter)

        # 왼쪽과 오른쪽의 비율 설정 
        main_horizontal_splitter.setStretchFactor(0, 8)  # 왼쪽 80%
        main_horizontal_splitter.setStretchFactor(1, 2)  # 오른쪽 20%

        # 스플리터를 메인 레이아웃에 추가
        result_layout.addWidget(main_horizontal_splitter, 1)  # stretch factor 1로 설정하여 남은 공간 모두 차지

    
    # 시각화 캔버스 초기화 
    def init_visualization_canvases(self):
        """시각화 캔버스 초기화 및 캔버스 배열 정리"""
        self.viz_canvases = []
        
        # 모든 탭의 캔버스 찾기
        for i in range(self.viz_stack.count()):
            page = self.viz_stack.widget(i)
            if page:
                # 특수 처리가 필요한 탭
                if i == 0:  # Capa 탭
                    # Capa 탭에는 두 개의 캔버스가 있으므로 모두 찾기
                    capa_canvases = page.findChildren(MplCanvas)
                    if len(capa_canvases) >= 2:
                        # 첫 번째 캔버스는 Capa 차트용
                        self.viz_canvases.append(capa_canvases[0])
                        # 두 번째 캔버스는 Utilization 차트용
                        self.viz_canvases.append(capa_canvases[1])
                        print("Capa 탭: 2개의 캔버스를 찾았습니다.")
                elif i == 1:  # Material 탭
                    # Material 탭의 캔버스 찾기
                    material_canvas = None
                    for child in page.findChildren(MplCanvas):
                        material_canvas = child
                        break
                    
                    if material_canvas:
                        self.viz_canvases.append(material_canvas)
                        print("Material 탭: 캔버스를 찾았습니다.")
                elif i == 2:  # PortCapa 탭
                    # PortCapa 탭의 캔버스 찾기
                    port_canvas = None
                    for child in page.findChildren(MplCanvas):
                        port_canvas = child
                        break
                    
                    if port_canvas:
                        self.viz_canvases.append(port_canvas)
                        print("PortCapa 탭: 캔버스를 찾았습니다.")
        
        print(f"초기화된 캔버스 개수: {len(self.viz_canvases)}")
        # 캔버스 매핑 정보 출력
        for i, canvas in enumerate(self.viz_canvases):
            canvas_type = "Unknown"
            if i == 0:
                canvas_type = "Capa"
            elif i == 1:
                canvas_type = "Utilization"
            elif i == 2:
                canvas_type = "Material"
            elif i == 3:
                canvas_type = "PortCapa"
            
            print(f"  - 캔버스[{i}]: {canvas_type} 타입")


    """이벤트 시그널 연결"""
    def connect_signals(self):
        # 왼쪽 섹션의 데이터 변경 이벤트 연결
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'data_changed'):
            self.left_section.data_changed.connect(self.on_data_changed)
        
        # 아이템 변경 이벤트 연결
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'item_data_changed'):
            self.left_section.item_data_changed.connect(self.on_item_data_changed)

        # 셀 이동 이벤트 연결 
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'cell_moved'):
            self.left_section.cell_moved.connect(self.on_cell_moved)

        # 검증 에러 관련 신호 연결
        if hasattr(self.left_section, 'validation_error_occured'):
            self.left_section.validation_error_occured.connect(self.add_validation_error)
        
        if hasattr(self.left_section, 'validation_error_resolved'):
            self.left_section.validation_error_resolved.connect(self.remove_validation_error)


    """아이템 데이터가 변경되었을 때 호출되는 함수"""
    def on_item_data_changed(self, item, new_data):
        # 위치 변경에 의한 호출인지 확인
        if hasattr(item, '_is_position_change'):
            # 위치 변경은 on_cell_moved에서 처리하므로 여기서는 무시
            return
        
        # 수량 변경이 있는 경우 업데이트
        if 'Qty' in new_data and pd.notna(new_data['Qty']):
            line = new_data.get('Line')
            time = new_data.get('Time')
            item = new_data.get('Item')
            new_qty = new_data.get('Qty')

            # 값 변환 및 검증
            try:
                time = int(time) if time is not None else None
                new_qty = int(float(new_qty)) if new_qty is not None else None
            except (ValueError, TypeError):
                print(f"시간 또는 수량 변환 오류: time={time}, qty={new_qty}")
                return

            if line is not None and time is not None and item is not None and new_qty is not None:
                    # 계획 유지율 위젯 업데이트
                    if hasattr(self, 'plan_maintenance_widget'):
                        # 수량 직접 업데이트
                        print(f"수량 업데이트: {line}, {time}, {item}, {new_qty}")
                        self.plan_maintenance_widget.update_quantity(line, time, item, new_qty)
                        
                        
    """시각화 페이지 전환 및 버튼 스타일 업데이트"""
    def switch_viz_page(self, index):
        # # 이전 탭이 Shipment 탭이었으면 위젯 상태 초기화
        # if self.viz_stack.currentIndex() == 4 and self.shipment_widget and index != 4:
        #     # 다른 탭으로 전환할 때 Shipment 위젯 상태 초기화
        #     self.shipment_widget.reset_state()

        self.viz_stack.setCurrentIndex(index)

        # 버튼 스타일 업데이트
        for i, btn in enumerate(self.viz_buttons):
            btn.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE if i == index else ResultStyles.INACTIVE_BUTTON_STYLE)

        # 각 탭별 특수 처리
        if index == 0:  # Capa 탭
            # Capa 탭이 선택되면 두 캔버스(Capa, Utilization) 모두 업데이트
            if len(self.viz_canvases) >= 2 and self.result_data is not None:
                VisualizationUpdater.update_capa_chart(self.viz_canvases[0], self.capa_ratio_data)
                VisualizationUpdater.update_utilization_chart(self.viz_canvases[1], self.utilization_data)
        elif index == 1 and self.result_data is not None:  # Material 탭 (1번) 인덱스
            # Material 탭 데이터 업데이트
            self.update_material_shortage_analysis()
        elif index == 2 and self.result_data is not None:
            self.portcapa_widget.render_table()

        elif index == 4 and self.result_data is not None:  # Shipment 탭 (4번) 인덱스
            # Shipment 탭 데이터 업데이트
            self.shipment_widget.run_analysis(self.result_data)
        elif index == 5 and self.result_data is not None:  # SplitView 탭 (5번) 인덱스
            # SplitView 탭 데이터 업데이트
            if hasattr(self, 'split_allocation_widget'):
                self.split_allocation_widget.run_analysis(self.result_data)
        # else:
        #     # 다른 탭으로 전환 시 자재 부족 상태 초기화
        #     self.clear_left_widget_shortage_status()

    def clear_left_widget_shortage_status(self):
        """왼쪽 위젯의 모든 아이템들의 자재 부족 상태 초기화"""
        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드의 모든 컨테이너 순회
        cleared_count = 0
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                # 각 컨테이너의 아이템들 순회
                for item in container.items:
                    if hasattr(item, 'is_shortage') and item.is_shortage:
                        # 자재 부족 상태 초기화
                        item.set_shortage_status(False)
                        cleared_count += 1


    """출하 상태가 업데이트될 때 호출되는 함수"""
    def on_shipment_status_updated(self, failure_items):
        """
        출하 실패 정보가 업데이트되면 왼쪽 섹션의 아이템에 표시
        
        Args:
            failure_items (dict): 아이템 코드를 키로, 실패 정보를 값으로 가진 딕셔너리
        """
        # 왼쪽 섹션에 출하 실패 정보 전달
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'set_shipment_failure_items'):
            self.left_section.set_shipment_failure_items(failure_items)
        

    """각 지표별 초기 시각화 생성"""
    def create_initial_visualization(self, canvas, viz_type):
        # 각 지표 예시
        if viz_type == "Capa":
            VisualizationUpdater.update_capa_chart(canvas, self.capa_ratio_data)
        
        elif viz_type == "Utilization":
            if self.utilization_data is None:
                try:
                    self.utilization_data = CapaUtilization.analyze_utilization(self.result_data)
                    print("Finished Utilization Rate :", self.utilization_data)
                except Exception as e:
                    print(f"Utilization Rate Error : {str(e)}")
                    self.utilization_data = {}
            
            VisualizationUpdater.update_utilization_chart(canvas, self.utilization_data)

        elif viz_type == "PortCapa":
            pass

    """
    데이터가 변경되었을 때 호출되는 메서드
    데이터프레임을 분석하여 시각화 업데이트
    """
    def on_data_changed(self, data):
        print("on_data_changed 호출됨 - 데이터 변경 감지")
        self.result_data = data

        # 사전할당 상태 업데이트
        if hasattr(self, 'pre_assigned_items') and self.pre_assigned_items:
            self.update_left_widget_pre_assigned_status(self.pre_assigned_items)
        
        # 자재 부족 상태 업데이트
        if hasattr(self, 'material_analyzer') and self.material_analyzer and self.material_analyzer.shortage_results:
            self.update_left_widget_shortage_status(self.material_analyzer.shortage_results)
        
        # 출하 실패 상태 업데이트
        if hasattr(self.left_section, 'shipment_failure_items') and self.left_section.shipment_failure_items:
            self.left_section.apply_shipment_failure_status()

        try:
            # 데이터가 비어있지 않은 경우에만 분석 수행
            if data is not None and not data.empty:
                # 데이터 변경 이벤트 카운터 증가
                self.data_changed_count += 1
                
                self.validator = PlanAdjustmentValidator(data)
                
                # validator를 왼쪽 섹션에 전달 
                if hasattr(self, 'left_section'):
                    self.left_section.set_validator(self.validator)

                # Plan 탭의 계획 유지율 위젯 업데이트
                print("계획 유지율 위젯 업데이트 시작")

                if hasattr(self, 'plan_maintenance_widget'):
                    # 날짜 범위 가져오기 (메인 윈도우의 DataInputPage에서)
                    start_date, end_date = self.main_window.data_input_page.date_selector.get_date_range()
                    
                    # 한 번에 데이터 설정 (자동으로 이전 계획 감지 및 로드)
                    self.plan_maintenance_widget.set_data(data, start_date, end_date)
                    print("계획 유지율 위젯 데이터 업데이트 완료")
                
                # 분산 배치 위젯 업데이트
                if hasattr(self, 'split_allocation_widget'):
                    self.split_allocation_widget.run_analysis(data)

                # Capa 비율 분석
                # 두 번째 이벤트부터 정상 출력 (첫 번째 이벤트는 출력 안함)
                if self.data_changed_count > 1:
                    # 제조동별 생산량 비율 분석
                    self.capa_ratio_data = CapaRatioAnalyzer.analyze_capa_ratio(data_df=data, is_initial=False)
                else:
                    # 첫 번째 이벤트는 결과를 저장하지만 출력하지 않음
                    self.capa_ratio_data = CapaRatioAnalyzer.analyze_capa_ratio(data_df=data, is_initial=True)
                
                # 요일별 가동률 
                self.utilization_data = CapaUtilization.analyze_utilization(data)

                # 시각화 업데이트
                self.update_all_visualizations()
                    
            else:
                print("빈 데이터프레임")
                self.capa_ratio_data = {}
                self.utilization_data = {}

        except Exception as e:
            print(f"데이터 분석 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    """
    셀이 이동되었을 때 호출되는 메서드
    변경된 항목에 따라 시각화 업데이트
    """
    def on_cell_moved(self, item, old_data, new_data):
        try:
            # 결과 데이터가 있을 때만 처리
            if self.result_data is not None and not self.result_data.empty:
                # 수량만 변경된 경우 (위치는 동일)
                is_quantity_only_change = (
                    old_data.get('Line') == new_data.get('Line') and
                    old_data.get('Time') == new_data.get('Time') and
                    old_data.get('Item') == new_data.get('Item') and
                    old_data.get('Qty') != new_data.get('Qty')
                )

                # 수량만 변경된 경우
                if is_quantity_only_change:
                    print(f"[DEBUG] 수량 변경 전: {old_data['Qty']}, 변경 후: {new_data['Qty']}")
                    # 결과 데이터에서 정확한 아이템만 업데이트
                    mask = (
                        (self.result_data['Line'] == new_data.get('Line')) &
                        (self.result_data['Time'] == int(new_data.get('Time'))) &
                        (self.result_data['Item'] == new_data.get('Item'))
                    )
                    
                    matched_rows = self.result_data[mask]
                    print(f"매칭된 행 수: {len(matched_rows)}")
                    
                    if len(matched_rows) > 0:
                        # print(f"매칭된 행 정보: {matched_rows.iloc[0].to_dict()}")
                        # 수량 업데이트
                        self.result_data.loc[mask, 'Qty'] = float(new_data.get('Qty'))
                        # print(f"수량만 변경: {old_data.get('Qty')} -> {new_data.get('Qty')}")
        
                else:
                    print(f"[DEBUG] 위치 이동 감지! {old_data['Line']}→{new_data['Line']}, "
                            f"{old_data['Time']}→{new_data['Time']}, "
                            f"Qty: {old_data['Qty']} → {new_data['Qty']}")
                    # 기존 행 제거
                    old_mask = (
                        (self.result_data['Line'] == old_data.get('Line')) &
                        (self.result_data['Time'] == int(old_data.get('Time'))) &
                        (self.result_data['Item'] == old_data.get('Item'))
                    )
                    
                    # 기존 행 데이터 백업
                    old_row_data = self.result_data[old_mask].iloc[0].copy() if old_mask.any() else None
                    
                    # 기존 행 제거
                    self.result_data = self.result_data[~old_mask]
                    
                    # 새 행 추가
                    if old_row_data is not None:
                        new_row = old_row_data.copy()
                        new_row['Line'] = str(new_data.get('Line'))
                        new_row['Time'] = int(new_data.get('Time'))
                        new_row['Item'] = str(new_data.get('Item'))
                        new_row['Qty'] = float(new_data.get('Qty'))
                        
                        # 다른 필드들도 new_data에서 업데이트
                        for key, value in new_data.items():
                            if key in new_row.index and key not in ['Line', 'Time', 'Item', 'Qty']:
                                new_row[key] = value
                        
                        # 새 행을 DataFrame에 추가
                        self.result_data.loc[len(self.result_data)] = new_row
                        
                        print(f"위치 변경 완료: 기존 행 제거 후 새 행 추가")

                # 셀 이동에 따른 제조동별 생산량 비율 업데이트
                updated_ratio = CapaRatioAnalyzer.update_capa_ratio_for_cell_move(
                    self.result_data, old_data, new_data, is_initial=False  # 셀 이동 시 결과 표시
                )

                # 업데이트된 비율이 있는 경우
                if updated_ratio:
                    # 원본 데이터가 없는 경우 원본 데이터 저장
                    if not hasattr(self, 'original_capa_ratio') or self.original_capa_ratio is None:
                        self.original_capa_ratio = self.capa_ratio_data.copy() if isinstance(self.capa_ratio_data, dict) else {}
                    
                    # 비교 형식으로 데이터 구성
                    self.capa_ratio_data = {
                        'original': self.original_capa_ratio,
                        'adjusted': updated_ratio
                    }

                    # utilization 비교 데이터 처리
                    # 요일별 가동률 업데이트 : 불필요한 계산 막기 위해 capa가 업데이트 되면 시행
                    utilization_updated = CapaUtilization.update_utilization_for_cell_move(
                        self.result_data, old_data, new_data
                    )
                    
                    print(f"가동률 업데이트: {utilization_updated}")

                    if utilization_updated:
                        # 원본 데이터 저장(처음 수정 시)
                        if not hasattr(self, 'original_utilization') or self.original_utilization is None:
                            self.original_utilization = self.utilization_data.copy() if isinstance(self.utilization_data, dict) else {}

                        # 비교 형식으로 데이터 구성
                        self.utilization_data = {
                            'original' : self.original_utilization,
                            'adjusted': utilization_updated
                        }

                        print(f"비교 데이터 구성: {self.utilization_data}")

                    # 시각화 업데이트
                    self.update_all_visualizations()

                    # print(f"업데이트된 분석 결과: {self.capa_ratio_data}")

                    # Plan 탭의 계획 유지율 위젯 업데이트
                    if hasattr(self, 'plan_maintenance_widget'):
                        # 필요한 데이터 추출
                        line = new_data.get('Line')
                        time = new_data.get('Time')
                        item = new_data.get('Item')
                        qty = new_data.get('Qty')
                        
                        # 값이 있으면 수량 업데이트
                        if line and time is not None and item and qty is not None:
                            self.plan_maintenance_widget.update_quantity(line, time, item, qty)
        
        except Exception as e:
            print(f"셀 이동 처리 중 오류 발생: {e}")
            
    
    """모든 시각화 차트 업데이트"""
    def update_all_visualizations(self):
        print(f"시각화 업데이트 시작 - 캔버스 개수: {len(self.viz_canvases)}")

        # 캔버스 초기화
        if not self.viz_canvases:
            print("캔버스가 초기화되지 않음. 초기화 실행...")
            self.init_visualization_canvases()
        
        # 데이터 로그
        print(f"Capa 비율 데이터: {self.capa_ratio_data}")
        print(f"가동률 데이터: {self.utilization_data}")

        # Capa 탭의 두 차트 업데이트 (0번과 1번 캔버스)
        if len(self.viz_canvases) >= 2:
            # 첫 번째 캔버스 - Capa 차트
            VisualizationUpdater.update_capa_chart(self.viz_canvases[0], self.capa_ratio_data)
            
            # 두 번째 캔버스 - Utilization 차트
            VisualizationUpdater.update_utilization_chart(self.viz_canvases[1], self.utilization_data)
        
        # Material 탭 캔버스 업데이트 (2번 캔버스)
        if len(self.viz_canvases) >= 3 and self.viz_stack.currentIndex() == 1:  # Material 탭이 현재 선택된 경우
            # Material 탭의 경우 캔버스 업데이트 후 테이블 업데이트까지 함께 수행
            if self.result_data is not None and not self.result_data.empty:
                self.material_analyzer = VisualizationUpdater.update_material_shortage_chart(
                    self.viz_canvases[2], self.result_data
                )
                if hasattr(self, 'shortage_items_table') and self.shortage_items_table is not None:
                    self.update_shortage_items_table()
        
        # PortCapa 탭 캔버스 업데이트 (3번 캔버스) - 필요시
        if len(self.viz_canvases) >= 4:
            # PortCapa 시각화 업데이트 코드 (구현 예정)
            pass

        print("시각화 업데이트 완료")
    
    """개별 시각화 차트 업데이트"""
    def update_visualization(self, canvas, viz_type):
        """개별 시각화 차트 업데이트"""
        if viz_type == "Capa":
            VisualizationUpdater.update_capa_chart(canvas, self.capa_ratio_data)
        elif viz_type == "Utilization":
            VisualizationUpdater.update_utilization_chart(canvas, self.utilization_data)
        elif viz_type == "Material":
            # Material 탭의 경우 캔버스 업데이트 후 테이블 업데이트까지 함께 수행
            if self.result_data is not None and not self.result_data.empty:
                # canvas 매개변수는 Material 탭의 캔버스
                self.material_analyzer = VisualizationUpdater.update_material_shortage_chart(canvas, self.result_data)
                if hasattr(self, 'shortage_items_table') and self.shortage_items_table is not None:
                    self.update_shortage_items_table()
        elif viz_type == "PortCapa":
            # PortCapa 업데이트 로직 (구현 예정)
            pass
    

    """최종 최적화 결과를 파일로 내보내는 메서드"""
    def export_results(self):
        try:
            # 데이터가 있는지 확인
            if hasattr(self, 'left_section') and hasattr(self.left_section,
                                                            'data') and self.left_section.data is not None:
                
                # 날짜 범위 가져오기
                start_date, end_date = self.main_window.data_input_page.date_selector.get_date_range()
                
                # 통합 내보내기 로직
                saved_path = ExportManager.export_data(
                    parent=self,
                    data_df=self.left_section.data,
                    start_date=start_date,
                    end_date=end_date,
                    is_planning=False
                )

                # 성공적으로 파일 저장 시 시그널 발생
                if saved_path:
                    self.export_requested.emit(saved_path)

            else:
                print("No data to export.")
                QMessageBox.warning(
                    self,
                    "Export Error",
                    "No data to export."
                )

        except Exception as e:
            print(f"Export 과정에서 오류 발생: {str(e)}")
            QMessageBox.critical(
            self, 
            "Export Error", 
            f"An error occurred during export:\n{str(e)}"
        )

    """테이블 셀에 마우스 올릴 때 상세 정보 툴팁 표시"""
    def show_shortage_tooltip(self, row, column):
        if self.shortage_items_table is None or self.material_analyzer is None:
            return
            
        # 현재 셀의 아이템
        item = self.shortage_items_table.item(row, 0)
        if item is None:
            return
            
        # 모델 코드 가져오기
        model_code = item.data(Qt.UserRole)
        if not model_code:
            return
            
        # 해당 모델의 부족 정보 가져오기
        shortages = self.material_analyzer.get_item_shortages(model_code)
        if not shortages:
            return
            
        # 툴팁 내용 생성
        tooltip_text = f"<b>{model_code}</b> Material Shortage Details:<br><br>"
        tooltip_text += "<table border='1' cellspacing='0' cellpadding='3'>"
        tooltip_text += "<tr style='background-color:#f0f0f0'><th>Material</th><th>Required</th><th>Available</th><th>Shortage</th></tr>"
        
        for shortage in shortages:
            tooltip_text += f"<tr>"
            tooltip_text += f"<td>{shortage['Material']}</td>"
            tooltip_text += f"<td align='right'>{int(shortage['Required']):,}</td>"
            tooltip_text += f"<td align='right'>{int(shortage['Available']):,}</td>"
            tooltip_text += f"<td align='right' style='color:red'>{int(shortage['Shortage']):,}</td>"
            tooltip_text += f"</tr>"
            
        tooltip_text += "</table>"
        
        # 현재 마우스 위치에 툴팁 표시
        QToolTip.showText(QCursor.pos(), tooltip_text)

    """자재 부족량 분석 실행 및 UI 업데이트"""

    def update_material_shortage_analysis(self):
        """자재 부족량 분석 실행 및 UI 업데이트"""
        if not hasattr(self, 'shortage_items_table') or self.shortage_items_table is None:
            print("자재 부족 테이블이 초기화되지 않았습니다.")
            return
                
        # Material 탭의 캔버스 찾기 - viz_canvases에서 올바른 인덱스 사용
        material_canvas = None
        for i, canvas in enumerate(self.viz_canvases):
            if i == 1:  # Material 탭 캔버스 인덱스 (0:Capa, 1:Utilization, 2:Material)
                material_canvas = canvas
                break
                    
        if material_canvas is None:
            print("자재 부족량 분석을 위한 캔버스를 찾을 수 없습니다.")
            return
        
        # 결과 데이터가 없으면 메시지만 표시
        if self.result_data is None or self.result_data.empty:
            print("결과 데이터가 없습니다. 데이터를 먼저 로드해주세요.")
            material_canvas.axes.clear()
            material_canvas.axes.text(0.5, 0.5, "Please Load Result Data First", 
                                ha="center", va="center", fontsize=20)
            material_canvas.axes.set_frame_on(False)
            material_canvas.axes.get_xaxis().set_visible(False)
            material_canvas.axes.get_yaxis().set_visible(False)
            material_canvas.draw()
            
            # 테이블 초기화
            self.shortage_items_table.setRowCount(0)
            empty_item = QTableWidgetItem("자재 부족 항목이 없습니다.")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.shortage_items_table.setRowCount(1)
            self.shortage_items_table.setItem(0, 0, empty_item)
            self.shortage_items_table.setSpan(0, 0, 1, 4)  # 4개 컬럼 병합
            return
                
        print(f"자재 부족량 분석 시작 - 데이터프레임 크기: {self.result_data.shape}")

        # 자재 부족량 분석 실행 및 차트 업데이트 (결과 데이터 직접 전달)
        self.material_analyzer = VisualizationUpdater.update_material_shortage_chart(material_canvas, self.result_data)
            
        # 분석 결과가 없으면 종료
        if self.material_analyzer is None:
            print("자재 부족량 분석기가 생성되지 않았습니다.")
            return
        
        # 부족 모델을 왼쪽 위젯에 전달
        if self.material_analyzer.shortage_results:
            self.update_left_widget_shortage_status(self.material_analyzer.shortage_results)
            # self.material_analysis_done = True

        if not self.material_analyzer.shortage_results:
            print("자재 부족량 분석 결과가 없습니다.")
            self.shortage_items_table.setRowCount(0)
            empty_item = QTableWidgetItem("자재 부족 항목이 없습니다.")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.shortage_items_table.setRowCount(1)
            self.shortage_items_table.setItem(0, 0, empty_item)
            self.shortage_items_table.setSpan(0, 0, 1, 4)  # 4개 컬럼 병합
            return
        
        print(f"자재 부족 항목 수: {len(self.material_analyzer.shortage_results)}")
                
        # 부족 항목 테이블 업데이트
        self.update_shortage_items_table()

    """자재 부족 항목 테이블 업데이트"""
    def update_shortage_items_table(self):
        if not hasattr(self, 'shortage_items_table') or self.shortage_items_table is None or self.material_analyzer is None:
            print("테이블 또는 분석기 객체가 초기화되지 않았습니다.")
            return
                
        # 테이블 초기화
        self.shortage_items_table.setRowCount(0)
            
        # 부족 항목 데이터 가져오기
        shortage_df = self.material_analyzer.get_all_shortage_data()
            
        if shortage_df.empty:
            print("자재 부족 항목 데이터가 비어있습니다.")
            return
                
        # print(f"자재 부족 항목 데이터 크기: {shortage_df.shape}")
        # print(f"데이터 샘플:\n{shortage_df.head()}")
                
        # 부족률 계산 및 정렬 (부족률 높은 순)
        shortage_df['Shortage_Pct'] = (shortage_df['Shortage'] / shortage_df['Required']) * 100
        shortage_df = shortage_df.sort_values('Shortage_Pct', ascending=False)
            
        # 테이블 행 수 설정
        row_count = min(20, len(shortage_df))  # 최대 20개 행만 표시
        self.shortage_items_table.setRowCount(row_count)
        
        print(f"테이블에 표시할 행 수: {row_count}")
            
        # 테이블 데이터 추가
        for row_idx, (_, data) in enumerate(shortage_df.head(row_count).iterrows()):
            # 모델명 셀
            item_cell = QTableWidgetItem(data['Item'][:15] + '...' if len(data['Item']) > 15 else data['Item'])
            item_cell.setData(Qt.UserRole, data['Item'])  # 원본 모델 코드 저장
                
            # 자재 코드 셀
            material_cell = QTableWidgetItem(data['Material'])
                
            # 부족량 셀
            shortage_cell = QTableWidgetItem(f"{int(data['Shortage']):,}")
            shortage_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
            # 부족률 셀
            shortage_pct_cell = QTableWidgetItem(f"{data['Shortage_Pct']:.1f}%")
            shortage_pct_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
            # 부족률에 따른 배경색 설정
            if data['Shortage_Pct'] > 50:
                # 심각한 부족 (빨간색 계열)
                shortage_pct_cell.setBackground(QBrush(QColor('#FFAAAA')))
            elif data['Shortage_Pct'] > 20:
                # 중간 정도 부족 (노란색 계열)
                shortage_pct_cell.setBackground(QBrush(QColor('#FFFFAA')))
            else:
                # 경미한 부족 (옅은 빨간색)
                shortage_pct_cell.setBackground(QBrush(QColor('#FFE6E6')))
                
            # 테이블에 셀 추가
            self.shortage_items_table.setItem(row_idx, 0, item_cell)
            self.shortage_items_table.setItem(row_idx, 1, material_cell)
            self.shortage_items_table.setItem(row_idx, 2, shortage_cell)
            self.shortage_items_table.setItem(row_idx, 3, shortage_pct_cell)
            
        # 행 높이 조정
        for row in range(row_count):
            self.shortage_items_table.setRowHeight(row, 25)
            
        print("자재 부족 테이블 업데이트 완료")


    """왼쪽 위젯의 아이템들에 자재 부족 상태 적용"""
    def update_left_widget_shortage_status(self, shortage_dict):
        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # left_section에 자재부족 정보 전달
        if hasattr(self.left_section, 'set_current_shortage_items'):
            self.left_section.set_current_shortage_items(shortage_dict)
        
        # 그리드의 모든 컨테이너 순회
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                # 각 컨테이너의 아이템들 순회
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']
                        
                        # 해당 아이템이 자재 부족 목록에 있는지 확인
                        if item_code in shortage_dict:
                            # 자재 부족 상태로 설정
                            item.set_shortage_status(True, shortage_dict[item_code])
                        else:
                            # 정상 상태로 설정
                            item.set_shortage_status(False)


    """ 최적화 결과를 사전할당 정보와 함께 설정"""
    def set_optimization_result(self, results):
        # 결과 데이터 추출
        assignment_result = results.get('assignment_result')
        pre_assigned_items = results.get('pre_assigned_items', [])
        optimization_metadata = results.get('optimization_metadata', {})

        # 사전할당 아이템 저장 
        self.pre_assigned_items = set(pre_assigned_items)

        if hasattr(self, 'left_section'):
            # 왼쪽 섹션에 사전할당 정보 전달
            if hasattr(self.left_section, 'set_pre_assigned_items'):
                self.left_section.set_pre_assigned_items(self.pre_assigned_items)
            else:
                # 속성으로 직접 설정
                self.left_section.pre_assigned_items = self.pre_assigned_items

            # 데이터 설정
            self.left_section.set_data_from_external(assignment_result)

        # 메타데이터 필요시
        self.optimization_metadata = optimization_metadata

        print(f"최적화 결과 설정 완료: {len(pre_assigned_items)}개 사전할당 아이템")
        if hasattr(self, 'shipment_widget') and assignment_result is not None:
                    self.shipment_widget.run_analysis(assignment_result)
        
        # 분산 배치 위젯 업데이트 (추가)
        if hasattr(self, 'split_allocation_widget') and assignment_result is not None:
            self.split_allocation_widget.run_analysis(assignment_result)

    """왼쪽 위젯에 사전할당 상태 적용"""
    def update_left_widget_pre_assigned_status(self, pre_assigned_items):
        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드의 모든 컨테이너 순환
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                # 각 컨테이너의 아이템들 순환
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']

                        # 해당 아이템이 사전할당 목록에 있는지 확인
                        if item_code in pre_assigned_items:
                            item.set_pre_assigned_status(True)
                        else:
                            item.set_pre_assigned_status(False)

    """에러 관리 메서드"""
    def add_validation_error(self, item_info, error_message):
        error_key = f"{item_info.get('Line')}_{item_info.get('Time')}_{item_info.get('Item')}"

        # 에러 저장
        self.validation_errors[error_key] = {
            'item_info' : item_info,
            'message' : error_message
        }

        # 에러가 있는 아이템 목록에 추가
        item_key = item_info.get('Item')
        if item_key:
            self.error_items.add(item_key)

        # left_section에 정보 전달
        if hasattr(self.left_section, 'set_current_validation_errors'):
            self.left_section.set_current_validation_errors(self.validation_errors)

        # 에러표시 업데이트
        self.update_error_display()

        # 해당 아이템 카드 강조
        self.highlight_error_item(item_info)

    
    """조정검증 에러 제거"""
    def remove_validation_error(self, item_info):
        error_key = f"{item_info.get('Line')}_{item_info.get('Time')}_{item_info.get('Item')}"

        if error_key in self.validation_errors:
            del self.validation_errors[error_key]

            # 해당 아이템에 더 이상 에러가 없다면 목록에서 제거
            item_key = item_info.get('Item')
            if item_key and not any(error['item_info'].get('Item') == item_key for error in self.validation_errors.values()):
                self.error_items.discard(item_key)
        
        # 왼쪽 섹션에 업데이트된 검증 에러 정보 전달
        if hasattr(self.left_section, 'set_current_validation_errors'):
            self.left_section.set_current_validation_errors(self.validation_errors)

        # 에러 표시 업데이트
        self.update_error_display()
        
        # 아이템 카드 강조 해제
        self.remove_item_highlight(item_info)

    
    """에러 표시 위젯 업데이트"""
    def update_error_display(self):
        # 기존 에러 위젯 제거
        for i in reversed(range(self.error_display_layout.count())):
            child = self.error_display_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        # 에러가 없으면 숨김
        if not self.validation_errors:
            self.error_scroll_area.hide()
            return
        
        # 에러가 있으면 표시
        self.error_scroll_area.show()

        # 에러 제목
        title_label = QLabel("Constraint Violations")
        title_label.setStyleSheet("""
            QLabel {
            background-color: #FF6B6B;
            color: white;
            padding: 5px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 26px;
            border: none;
            }
        """)
        self.error_display_layout.addWidget(title_label)

        # 각 에러 표시
        for error_key, error_info in self.validation_errors.items():
            error_widget = self.create_error_item_widget(error_info)
            self.error_display_layout.addWidget(error_widget)

        
    """에러 항목 위젯 생성"""
    def create_error_item_widget(self, error_info):
        class ClickableErrorFrame(QFrame):
            def __init__(self, error_info, parent_widget):
                super().__init__()
                self.error_info = error_info
                self.parent_widget = parent_widget
                
            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    self.parent_widget.navigate_to_error_item(self.error_info)
                super().mousePressEvent(event)

        widget = ClickableErrorFrame(error_info, self)
        widget.setStyleSheet("""
            QFrame {
                background-color: #FFF5F5;
                border: 3px solid #FEB2B2;
                border-radius: 5px;
                padding: 3px;
                margin: 3px;
                min-height: 30px;
            }
            QFrame:hover {
                background-color: #FFE9E9;
                border-color: #FF8888;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        item_info = error_info['item_info']
        item_location_text = f"Item: {item_info.get('Item', 'N/A')} | Line: {item_info.get('Line', 'N/A')}, Time: {item_info.get('Time', 'N/A')}"

        item_location_label = QLabel(item_location_text)
        item_location_label.setStyleSheet("""
            font-weight: bold; 
            color: #333;
            font-size: 22px;
            border: none;
            background: transparent;
        """)
        item_location_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(item_location_label)

        message_label = QLabel(error_info['message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            color: #D53030; 
            font-size: 22px;
            font-weight: 700;
            border: none;
            background: transparent;
            line-height: 1.5;
        """)
        message_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(message_label)

        return widget
    

    """에러가 있는 아이템 카드 강조"""
    def highlight_error_item(self, item_info):
        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드에서 해당 아이템 찾기
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if (hasattr(item, 'item_data') and item.item_data and 
                        item.item_data.get('Line') == item_info.get('Line') and 
                        item.item_data.get('Time') == item_info.get('Time') and 
                        item.item_data.get('Item') == item_info.get('Item')):

                        # 에러 스타일 적용 대신 그냥 선택 상태로만 변경
                        item.set_selected(True)
                        return


    """아이템 카드 강조 해재"""
    def remove_item_highlight(self, item_info):
        error_key = f"{item_info.get('Line')}_{item_info.get('Time')}_{item_info.get('Item')}"
        print(f"에러 해결 시도: {error_key}")
        print(f"현재 에러 목록: {list(self.validation_errors.keys())}")

        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드에서 해당 아이템 차직
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if (hasattr(item, 'item_data') and item.item_data and 
                        item.item_data.get('Line') == item_info.get('Line') and 
                        item.item_data.get('Time') == item_info.get('Time') and 
                        item.item_data.get('Item') == item_info.get('Item')):

                        # 에러 상태 해제 대신 그냥 선택 해제
                        item.set_selected(False)
                        return

    """에러 아이템 navigation 및 highlight"""
    def navigate_to_error_item(self, error_info):
        print(f"navigate_to_error_item 호출: {error_info}")
        item_info = error_info['item_info']

        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 먼저 모든 아이템 선택 해제
        self.left_section.grid_widget.clear_all_selections()
        
        # 그리드에서 해당 아이템 찾기
        found_item = None
        target_line = str(item_info.get('Line', ''))
        target_time = str(item_info.get('Time', ''))
        target_item = str(item_info.get('Item', ''))
        
        for row_idx, row_containers in enumerate(self.left_section.grid_widget.containers):
            for col_idx, container in enumerate(row_containers):
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data:
                        current_line = str(item.item_data.get('Line', ''))
                        current_time = str(item.item_data.get('Time', ''))
                        current_item = str(item.item_data.get('Item', ''))
                        
                        if (current_line == target_line and 
                            current_time == target_time and 
                            current_item == target_item):
                            found_item = item
                            print(f"아이템 발견: 행{row_idx}, 열{col_idx}")
                            break
                    if found_item:
                        break
                if found_item:
                    break
            if found_item:
                break

        if found_item:
            # 아이템 선택 및 강조
            found_item.set_selected(True)
            
            # 컨테이너에도 선택 이벤트 전달
            container = found_item.parent()
            if hasattr(container, 'on_item_selected'):
                container.on_item_selected(found_item)
            
            # 그리드 위젯에도 선택 이벤트 전달
            self.left_section.grid_widget.on_item_selected(found_item, container)
            
            # 스크롤 이동 
            QTimer.singleShot(50, lambda: self.scroll_to_item(found_item))
            
            print("아이템으로 이동 완료")
        else:
            print("해당 아이템을 찾을 수 없습니다")

        
    """해당 아이템으로 스크롤 이동"""
    def scroll_to_item(self, item):
        print(f"scroll_to_item 호출 : {item}")
        
        # QScrollArea 찾기
        scroll_area = None
        parent = item.parent()
        while parent:
            if isinstance(parent, QScrollArea):
                scroll_area = parent
                break
            parent = parent.parent()
        
        if not scroll_area:
            print("QScrollArea를 찾지 못했습니다.")
            return
        
        # 아이템이 속한 컨테이너 찾기
        container = item.parent()
        if not isinstance(container, ItemsContainer):
            print("ItemsContainer를 찾지 못했습니다.")
            return
        
        # 스크롤 영역의 viewport 가져오기
        viewport = scroll_area.viewport()
        scroll_widget = scroll_area.widget()
        
        # 아이템의 전역 좌표를 스크롤 위젯 기준으로 변환
        item_global_pos = item.mapToGlobal(item.rect().center())
        item_pos_in_scroll = scroll_widget.mapFromGlobal(item_global_pos)
        
        # 현재 스크롤 위치 가져오기
        h_scrollbar = scroll_area.horizontalScrollBar()
        v_scrollbar = scroll_area.verticalScrollBar()
        
        # 아이템 위치 계산
        item_y = item_pos_in_scroll.y()
        viewport_height = viewport.height()
        
        # 아이템이 화면 중앙에 오도록 스크롤 위치 계산
        target_y = item_y - viewport_height // 2
        
        # 스크롤 위치 조정
        v_scrollbar.setValue(target_y)
        
        print(f"스크롤 완료 - 아이템 Y: {item_y}, 타겟 Y: {target_y}")
    
