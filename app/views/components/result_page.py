from PyQt5.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                             QFrame, QSplitter, QStackedWidget, QTableWidget, QHeaderView, QToolTip, 
                             QTableWidgetItem, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QCursor, QFont
import pandas as pd

from app.analysis.output.material_shortage_analysis import MaterialShortageAnalyzer
from ..components.visualization.visualization_updater import VisualizationUpdater
from app.analysis.output.daily_capa_utilization import CapaUtilization
from app.analysis.output.capa_ratio import CapaRatioAnalyzer
from app.utils.export_manager import ExportManager
from app.core.output.adjustment_validator import PlanAdjustmentValidator
from app.resources.styles.result_style import ResultStyles 
from app.views.components.result_components.modified_left_section import ModifiedLeftSection
from app.views.components.result_components.split_allocation_widget import SplitAllocationWidget
from app.views.components.result_components.items_container import ItemsContainer
from app.views.components.result_components.right_section.adj_error_manager import AdjErrorManager
from app.views.components.result_components.right_section.tab_manager import TabManager
from app.views.components.result_components.split_allocation_widget import SplitAllocationWidget

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

        # 위젯 참조 (호환성 유지)
        self.summary_widget = None
        self.plan_maintenance_widget = None
        self.portcapa_widget = None
        self.shipment_widget = None
        self.split_allocation_widget = None
        self.shortage_items_table = None
        self.viz_canvases = []

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

        left_layout.addWidget(self.left_section)
        
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

        # 에러 위젯
        self.error_manager = AdjErrorManager(
            parent_widget=self,
            error_scroll_area=self.error_scroll_area,
            navigate_callback=self.navigate_to_error_item,
            left_section=self.left_section
        )

        # 오른쪽 상단 섹션 
        right_top_frame = QFrame()
        right_top_frame.setFrameShape(QFrame.StyledPanel)
        right_top_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 2px solid #cccccc;")

        right_top_layout = QVBoxLayout(right_top_frame)

        # 1) TabManager 인스턴스화
        self.tab_manager = TabManager(self)

        # 2) 스택 위젯 생성
        self.viz_stack = QStackedWidget()
        self.viz_stack.setStyleSheet("border: none;")

        # 3) stack_widget 연결 - *반드시* create_tab_buttons 전에
        self.tab_manager.set_stack_widget(self.viz_stack)

        # 4) 버튼 레이아웃 준비
        button_group_layout = QHBoxLayout()
        button_group_layout.setSpacing(5)
        button_group_layout.setContentsMargins(10, 10, 10, 5)
        button_group_layout.setAlignment(Qt.AlignCenter)  # 중앙 정렬

        # 5) 탭 버튼/페이지 생성
        self.tab_manager.create_tab_buttons(button_group_layout)
        self.viz_buttons = self.tab_manager.buttons    # 호환성을 위해 기존 참조 유지

        # 위젯 참조 설정 (호환성 유지)
        self._setup_widget_references()

        # 6) 레이아웃에 버튼과 스택 추가
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


    def _create_material_tab_content(self, layout):
        """Material 탭 콘텐츠 생성"""
        material_page = QWidget()
        material_layout = QVBoxLayout(material_page)
        material_layout.setContentsMargins(0, 0, 0, 0)
        
        # 자재 부족 테이블
        self.shortage_items_table = QTableWidget()
        self.shortage_items_table.setColumnCount(4)
        self.shortage_items_table.setHorizontalHeaderLabels(["Material", "Model", "Shortage", "Shift"])
        self.shortage_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 테이블 스타일 적용
        self._apply_material_table_style()
        
        # 테이블 이벤트 연결
        self.shortage_items_table.setMouseTracking(True)
        self.shortage_items_table.cellEntered.connect(self.show_shortage_tooltip)
        
        material_layout.addWidget(self.shortage_items_table)
        layout.addWidget(material_page)
    
    """위젯 참조 설정"""
    def _setup_widget_references(self):
    
        # Summary 위젯
        summary_tab = self.tab_manager.get_tab_instance('Summary')
        if summary_tab:
            self.summary_widget = summary_tab.summary_widget

        # Plan 위젯
        plan_tab = self.tab_manager.get_tab_instance('Plan')
        if plan_tab:
            # PlanTab 클래스 안에 plan_maintenance_widget 프로퍼티가 있다고 가정
            self.plan_maintenance_widget = plan_tab.plan_maintenance_widget

        # PortCapa 위젯
        portcapa_tab = self.tab_manager.get_tab_instance('PortCapa')
        if portcapa_tab:
            self.portcapa_widget = portcapa_tab.portcapa_widget

        shipment_tab = self.tab_manager.get_tab_instance('Shipment')
        if shipment_tab:
            self.shipment_widget = shipment_tab.shipment_widget
            self.shipment_widget.shipment_status_updated.connect(self.on_shipment_status_updated)

        # SplitView 위젯 
        splitview_tab = self.tab_manager.get_tab_instance('SplitView')
        if splitview_tab:
            self.split_allocation_widget = splitview_tab.split_allocation_widget
        # 없으면 직접 생성
        elif self.split_allocation_widget is None:
            self.split_allocation_widget = SplitAllocationWidget()

        # Material 테이블
        material_tab = self.tab_manager.get_tab_instance('Material')
        if material_tab:
            self.shortage_items_table = material_tab.shortage_items_table

        # 캔버스 리스트 설정
        capa_tab = self.tab_manager.get_tab_instance('Capa')
        if capa_tab:
            self.viz_canvases = capa_tab.get_canvases()
    
    
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
                        
                        
    """
    시각화 페이지 전환 및 버튼 스타일 업데이트
    """
    def switch_viz_page(self, index):
        # TabManager를 통한 탭 전환 (호환성 유지)
        self.tab_manager.switch_tab(index)


    """
    Material 테이블 스타일 적용
    """
    def _apply_material_table_style(self):
        # 행 번호 스타일 설정
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
        
        # 테이블 메인 스타일 설정
        self.shortage_items_table.setStyleSheet("""
            QTableWidget {
                border: none;
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


    """
    왼쪽 위젯의 모든 아이템들의 자재 부족 상태 초기화
    """
    def clear_left_widget_shortage_status(self):
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

    """
    출하 상태가 업데이트될 때 호출되는 함수
    출하 실패 정보가 업데이트되면 왼쪽 섹션의 아이템에 표시
    
    Args:
        failure_items (dict): 아이템 코드를 키로, 실패 정보를 값으로 가진 딕셔너리
    """
    def on_shipment_status_updated(self, failure_items):
        # 왼쪽 섹션에 출하 실패 정보 전달
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'set_shipment_failure_items'):
            self.left_section.set_shipment_failure_items(failure_items)
        

    """
    각 지표별 초기 시각화 생성
    """
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

        # 위젯 참조가 없으면 다시 설정 (지연 초기화)
        if self.plan_maintenance_widget is None:
            self._setup_widget_references()


        # 데이터 로드 후 바로 자재부족 분석
        if data is not None and not data.empty:
            print("데이터 로드 후 자재 부족 분석 시행")
            try:
                # material_analyzer가 없으면 생성
                if not hasattr(self, 'material_analysis') or self.material_analyzer is None:
                    self.material_analyzer = MaterialShortageAnalyzer()

                # 분석 실행 시 데이터 전달
                self.material_analyzer.analyze_material_shortage(data)
            except Exception as e:
                print(f"초기 자재 부족 분석 중 오류 :{e}")

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
                    
                    # 데이터 설정 (FilePaths에서 자동으로 이전 계획 파일 확인) 
                    self.plan_maintenance_widget.set_data(data, start_date, end_date)
                    print("계획 유지율 위젯 데이터 업데이트 완료")
                
                # 분산 배치 위젯 업데이트
                if hasattr(self, 'split_allocation_widget'):
                    self.split_allocation_widget.run_analysis(data)

                # summary 위젯 업데이트
                if hasattr(self, 'summary_widget'):
                    self.summary_widget.run_analysis(data)

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
            
    
    """
    모든 시각화 차트 업데이트
    """
    def update_all_visualizations(self):
        print(f"시각화 업데이트 시작 - 캔버스 개수: {len(self.viz_canvases)}")

        # Capa 탭 업데이트 
        capa_tab = self.tab_manager.get_tab_instance('Capa')
        if capa_tab:
            capa_tab.update_content(self.capa_ratio_data, self.utilization_data)

        print("시각화 업데이트 완료")


    """
    개별 시각화 차트 업데이트
    """
    def update_visualization(self, canvas, viz_type):
        if viz_type == "Capa":
            VisualizationUpdater.update_capa_chart(canvas, self.capa_ratio_data)
        elif viz_type == "Utilization":
            VisualizationUpdater.update_utilization_chart(canvas, self.utilization_data)
        elif viz_type == "Material":
            if self.result_data is not None and not self.result_data.empty:
                if hasattr(self, 'shortage_items_table') and self.shortage_items_table is not None:
                    self.update_shortage_items_table()
        elif viz_type == "PortCapa":
            pass
    

    """
    최종 최적화 결과를 파일로 내보내는 메서드
    """
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


    """
    테이블 셀에 마우스 올릴 때 상세 정보 툴팁 표시
    """
    def show_shortage_tooltip(self, row, column):
        if self.shortage_items_table is None or self.material_analyzer is None:
            return
                
        # 현재 셀의 아이템
        material_item = self.shortage_items_table.item(row, 0)  # Material 컬럼
        model_item = self.shortage_items_table.item(row, 1)     # Model 컬럼
        
        if material_item is None or model_item is None:
            return
                
        # 모델 코드 가져오기
        model_code = model_item.text()
        material_code = material_item.text()
        
        if not model_code or not material_code:
            return
                
        # 해당 모델의 부족 정보 가져오기
        shortages = self.material_analyzer.get_item_shortages(model_code)
        if not shortages:
            return
                
        # 툴팁 내용 생성
        tooltip_text = f"<b>{model_code}</b> Material Shortage Details:<br><br>"
        tooltip_text += "<table border='1' cellspacing='0' cellpadding='3'>"
        tooltip_text += "<tr style='background-color:#f0f0f0'><th>Material</th><th>Shift</th><th>Shortage</th></tr>"
        
        for shortage in shortages:
            if shortage.get('material') == material_code:  # 현재 선택된 자재와 일치하는 항목만 표시
                tooltip_text += f"<tr>"
                tooltip_text += f"<td>{shortage.get('material', 'Unknown')}</td>"
                tooltip_text += f"<td align='center'>{shortage.get('shift', 0)}</td>"
                tooltip_text += f"<td align='right' style='color:red'>{int(shortage.get('shortage', 0)):,}</td>"
                tooltip_text += f"</tr>"
                
        tooltip_text += "</table>"
        
        # 현재 마우스 위치에 툴팁 표시
        QToolTip.showText(QCursor.pos(), tooltip_text)


    """
    자재 부족량 분석 실행 및 UI 업데이트
    """
    def update_material_shortage_analysis(self):
        
        # 결과 데이터가 없으면 메시지만 표시
        if self.result_data is None or self.result_data.empty:
            # print("결과 데이터가 없습니다. 데이터를 먼저 로드해주세요.")

            # 테이블 초기화
            if self.shortage_items_table:
            
                # 테이블 초기화
                self.shortage_items_table.setRowCount(0)
                empty_item = QTableWidgetItem("자재 부족 항목이 없습니다.")
                empty_item.setTextAlignment(Qt.AlignCenter)
                self.shortage_items_table.setRowCount(1)
                self.shortage_items_table.setItem(0, 0, empty_item)
                self.shortage_items_table.setSpan(0, 0, 1, 4)  # 4개 컬럼 병합
            return
                    
        print(f"자재 부족량 분석 시작 - 데이터프레임 크기: {self.result_data.shape}")

        # 자재 부족량 분석 실행
        if not hasattr(self, 'material_analysis') or self.material_analyzer is None:
            self.material_analyzer = MaterialShortageAnalyzer()

        # 분석 수행
        self.material_analyzer.analyze_material_shortage(self.result_data)
        # self.material_analyzer = VisualizationUpdater.update_material_shortage_chart(self.result_data)

        # 분석 결과가 없으면 종료
        if self.material_analyzer is None:
            print("자재 부족량 분석기가 생성되지 않았습니다.")
            return
        
        # 부족 모델을 왼쪽 위젯에 전달
        if self.material_analyzer.shortage_results:
            self.update_left_widget_shortage_status(self.material_analyzer.shortage_results)
        
        # 부족 항목 테이블 업데이트
        self.update_shortage_items_table()


    """
    자재 부족 항목 테이블 업데이트
    """
    def update_shortage_items_table(self):
        if not hasattr(self, 'shortage_items_table') or self.shortage_items_table is None or self.material_analyzer is None:
            print("테이블 또는 분석기 객체가 초기화되지 않았습니다.")
            return
                
        # 테이블 초기화 및 컬럼 구조 변경
        self.shortage_items_table.clear()
        self.shortage_items_table.setColumnCount(4)
        self.shortage_items_table.setHorizontalHeaderLabels(["Material", "Model", "Shortage", "Shift"])
        
        # 부족 항목 데이터 가져오기
        shortage_df = self.material_analyzer.get_all_shortage_data()
            
        if shortage_df.empty:
            print("자재 부족 항목 데이터가 비어있습니다.")
            # 비어있는 경우 메시지 표시
            self.shortage_items_table.setRowCount(1)
            empty_item = QTableWidgetItem("No material shortage detected")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.shortage_items_table.setItem(0, 0, empty_item)
            self.shortage_items_table.setSpan(0, 0, 1, 4)  # 4개 컬럼 병합
            return
                
        # print(f"자재 부족 항목 데이터 크기: {shortage_df.shape}")
        # print(f"부족 데이터 컬럼: {shortage_df.columns.tolist()}")
        
        # Material별로 그룹화하여 처리
        material_groups = shortage_df.groupby('Material')
        
        # 전체 필요한 행 수 계산 
        total_rows = sum(len(group) for _, group in material_groups)
        self.shortage_items_table.setRowCount(total_rows)
        
        # 테이블 데이터 추가
        current_row = 0
        for material, group in material_groups:
            # 그룹의 시작 행 인덱스 저장
            material_start_row = current_row
            
            # 이 자재에 대한 모든 모델 처리
            for i, (_, data) in enumerate(group.iterrows()):
                # 자재 코드 셀 (첫 번째 항목에만 표시)
                if i == 0:
                    material_cell = QTableWidgetItem(material)
                    material_cell.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.shortage_items_table.setItem(current_row, 0, material_cell)
                    
                    # 부족량 셀 (첫 번째 항목에만 표시)
                    shortage_amt = data['Shortage']
                    shortage_cell = QTableWidgetItem(f"{int(shortage_amt):,}")
                    shortage_cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.shortage_items_table.setItem(current_row, 2, shortage_cell)
                    
                    # 시프트 셀 (첫 번째 항목에만 표시)
                    shift = data['Shift']
                    shift_cell = QTableWidgetItem(str(shift))
                    shift_cell.setTextAlignment(Qt.AlignCenter)
                    self.shortage_items_table.setItem(current_row, 3, shift_cell)
                
                # 모델명 셀 (각 항목마다 별도 표시)
                item_code = data['Item']
                item_cell = QTableWidgetItem(item_code)
                item_cell.setData(Qt.UserRole, item_code)  # 원본 모델 코드 저장
                self.shortage_items_table.setItem(current_row, 1, item_cell)
                
                # 다음 행으로 이동
                current_row += 1
            
            # 그룹 내 행이 2개 이상인 경우 병합 수행
            group_row_count = len(group)
            if group_row_count > 1:
                # Material 컬럼 병합
                self.shortage_items_table.setSpan(material_start_row, 0, group_row_count, 1)
                # Shortage 컬럼 병합
                self.shortage_items_table.setSpan(material_start_row, 2, group_row_count, 1)
                # Shift 컬럼 병합
                self.shortage_items_table.setSpan(material_start_row, 3, group_row_count, 1)
        
        # 행 높이 및 컬럼 너비 조정
        for row in range(total_rows):
            self.shortage_items_table.setRowHeight(row, 25)
        
        # 컬럼 너비 자동 조정
        self.shortage_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Material
        self.shortage_items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Model
        self.shortage_items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Shortage
        self.shortage_items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Shift
        
        # 테이블 스타일 업데이트
        self.shortage_items_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                border: none;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        
        print("자재 부족 테이블 업데이트 완료")



    """왼쪽 위젯의 아이템들에 자재 부족 상태 적용
    
    Args:
        shortage_dict: {item_code: [{shift: shift_num, material: material_code, shortage: shortage_amt}]}
    """
    def update_left_widget_shortage_status(self, shortage_dict):
        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드의 모든 컨테이너 순회
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                # 각 컨테이너의 아이템들 순회
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']
                        item_time = item.item_data.get('Time')  # 시프트(Time) 정보 가져오기
                        
                        # 해당 아이템이 자재 부족 목록에 있는지 확인
                        if item_code in shortage_dict:
                            # 시프트별 부족 정보 검사
                            shortages_for_item = shortage_dict[item_code]
                            matching_shortages = []
                            
                            for shortage in shortages_for_item:
                                shortage_shift = shortage.get('shift')
                                
                                # 시프트가 일치하면 부족 정보 저장
                                if shortage_shift and item_time and int(shortage_shift) == int(item_time):
                                    matching_shortages.append(shortage)
                            
                            # 일치하는 시프트의 부족 정보가 있으면 부족 상태로 설정
                            if matching_shortages:
                                item.set_shortage_status(True, matching_shortages)
                            else:
                                item.set_shortage_status(False)
                        else:
                            # 부족 목록에 없는 경우 부족 상태 해제
                            item.set_shortage_status(False)


    """
    최적화 결과를 사전할당 정보와 함께 설정
    """
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
 

    """
    왼쪽 위젯에 사전할당 상태 적용
    """
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

    """
    에러 관리 메서드
    """
    def add_validation_error(self, item_info, error_message):
        self.error_manager.add_validation_error(item_info, error_message)

    """
    조정검증 에러 제거
    """
    def remove_validation_error(self, item_info):
        self.error_manager.remove_validation_error(item_info)

    """
    에러 아이템 navigation 및 highlight
    """
    def navigate_to_error_item(self, error_info):
        # print(f"navigate_to_error_item 호출: {error_info}")
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

        
    """
    해당 아이템으로 스크롤 이동
    """
    def scroll_to_item(self, item):
        # print(f"scroll_to_item 호출 : {item}")
        
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
    
