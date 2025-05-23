from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSplitter, QStackedWidget,
                             QWidget, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from ..base.base_section import BaseSection, SignalManager
from .kpi.kpi_widget import KpiWidget
from .error.adj_error_manager import AdjErrorManager
from .tabs.tab_manager import TabManager


"""
오른쪽 섹션 통합 관리 클래스
"""
class RightSectionManager(BaseSection):

    # 추가 시그널
    kpi_updated = pyqtSignal(dict)        # KPI 업데이트
    tab_changed = pyqtSignal(str, int)    # 탭 변경
    analysis_requested = pyqtSignal(str)  # 분석 요청

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_page = parent  # ResultPage 참조

        # 컴포넌트
        self.kpi_widget = None
        self.error_manager = None
        self.tab_manager = None

        # 시그널 관리자
        self.signal_manager = SignalManager()

        # 데이터 저장
        self.current_data = None
        self.capa_ratio_data = None
        self.utilization_data = None

        # 초기화
        self.initialize()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # 수직 스플리터 생성 (상단/하단 분할)
        self.main_splitter = QSplitter(Qt.Vertical)
        
        # 상단 영역 생성 (KPI + Error)
        self.setup_top_section()
        
        # 하단 영역 생성 (Tabs)
        self.setup_bottom_section()
        
        # 스플리터에 추가
        self.main_splitter.addWidget(self.top_widget)
        self.main_splitter.addWidget(self.bottom_widget)
        
        # 비율 설정 (상단 30%, 하단 70%)
        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 7)
        
        main_layout.addWidget(self.main_splitter)

    """
    상단 섹션 구성 : KPI + Error
    """
    def setup_top_section(self):
        self.top_widget = QWidget()
        top_layout = QHBoxLayout(self.top_widget)
        top_layout.setContentsMargins(5, 5, 5, 5)
        top_layout.setSpacing(10)
        
        # 수평 스플리터 (KPI | Error)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # KPI 위젯
        self.kpi_widget = KpiWidget(self)
        self.kpi_widget.setMinimumWidth(200)
        
        # Error 위젯
        self.error_widget = self.setup_error_section()
        
        top_splitter.addWidget(self.kpi_widget)
        top_splitter.addWidget(self.error_widget)
        
        # 1:1 비율로 설정
        top_splitter.setSizes([500, 500])
        
        top_layout.addWidget(top_splitter)

    """
    에러 섹션 구성
    """
    def setup_error_section(self):
        error_frame = QWidget()
        error_frame.setStyleSheet("""
            QWidget {
                background-color: white; 
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)
        
        error_layout = QVBoxLayout(error_frame)
        error_layout.setContentsMargins(0, 0, 0, 0)
        
        # 에러 표시 위젯
        error_display_widget = QWidget()
        error_display_layout = QVBoxLayout(error_display_widget)
        error_display_layout.setContentsMargins(5, 5, 5, 5)
        error_display_layout.setAlignment(Qt.AlignTop)
        
        # 스크롤 영역
        error_scroll_area = QScrollArea()
        error_scroll_area.setWidgetResizable(True)
        error_scroll_area.setWidget(error_display_widget)
        error_scroll_area.setStyleSheet("border: none;")

        # 에러 매니저 초기화
        self.error_manager = AdjErrorManager(
            parent_widget=self,
            error_scroll_area=error_scroll_area,
            navigate_callback=self.navigate_to_error_item,
            left_section=None  # 나중에 설정
        )

        error_layout.addWidget(error_scroll_area)
        
        return error_frame
    
    """
    하단 섹션 구성 
    """
    def setup_bottom_section(self):
        """하단 섹션 구성 (Tabs)"""
        self.bottom_widget = QWidget()
        self.bottom_widget.setStyleSheet("""
            QWidget {
                background-color: white; 
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)
        
        bottom_layout = QVBoxLayout(self.bottom_widget)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        
        # 탭 매니저 생성
        self.tab_manager = TabManager(self.result_page)
        
        self.viz_stack = QStackedWidget()
        self.tab_manager.set_stack_widget(self.viz_stack)
        
        # 탭 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 5)
        button_layout.setAlignment(Qt.AlignCenter)
        
        # 탭 생성
        self.tab_manager.create_tab_buttons(button_layout)
        
        # 위젯 참조 설정
        self.setup_widget_references()
        
        # 레이아웃에 추가
        bottom_layout.addLayout(button_layout)
        bottom_layout.addWidget(self.viz_stack, 1)

    """
    위젯 참조 설정 : 호환성 유지
    """
    def setup_widget_reference(self):
        if self.result_page:
            # Summary 위젯
            summary_tab = self.tab_manager.get_tab_instance('Summary')
            if summary_tab and hasattr(summary_tab, 'summary_widget'):
                self.result_page.summary_widget = summary_tab.summary_widget
            
            # Plan 위젯
            plan_tab = self.tab_manager.get_tab_instance('Plan')
            if plan_tab and hasattr(plan_tab, 'plan_maintenance_widget'):
                self.result_page.plan_maintenance_widget = plan_tab.plan_maintenance_widget
            
            # PortCapa 위젯
            portcapa_tab = self.tab_manager.get_tab_instance('PortCapa')
            if portcapa_tab and hasattr(portcapa_tab, 'portcapa_widget'):
                self.result_page.portcapa_widget = portcapa_tab.portcapa_widget
            
            # Shipment 위젯
            shipment_tab = self.tab_manager.get_tab_instance('Shipment')
            if shipment_tab and hasattr(shipment_tab, 'shipment_widget'):
                self.result_page.shipment_widget = shipment_tab.shipment_widget
                if hasattr(shipment_tab.shipment_widget, 'shipment_status_updated'):
                    shipment_tab.shipment_widget.shipment_status_updated.connect(
                        self.result_page.on_shipment_status_updated
                    )
            
            # SplitView 위젯
            splitview_tab = self.tab_manager.get_tab_instance('SplitView')
            if splitview_tab and hasattr(splitview_tab, 'split_allocation_widget'):
                self.result_page.split_allocation_widget = splitview_tab.split_allocation_widget
            
            # Material 위젯
            material_tab = self.tab_manager.get_tab_instance('Material')
            if material_tab:
                self.result_page.material_widget = material_tab.get_widget() if hasattr(material_tab, 'get_widget') else None
                if hasattr(material_tab, 'get_table'):
                    self.result_page.shortage_items_table = material_tab.get_table()
                
                # 자재 부족 정보 업데이트 시그널 연결
                if (hasattr(self.result_page, 'material_widget') and 
                    self.result_page.material_widget and 
                    hasattr(self.result_page.material_widget, 'material_shortage_updated')):
                    self.result_page.material_widget.material_shortage_updated.connect(
                        self.result_page.on_material_shortage_updated
                    )
            
            # 캔버스 리스트 설정
            capa_tab = self.tab_manager.get_tab_instance('Capa')
            if capa_tab and hasattr(capa_tab, 'get_canvases'):
                self.result_page.viz_canvases = capa_tab.get_canvases()

    """
    시그널 연결
    """
    def connect_signals(self):
        if self.tab_manager:
            self.signal_manager.connect(
                self.tab_manager.tab_changed,
                self.on_tab_changed
            )

    """
    에러 메세지 섹션 설정
    """
    def set_left_section(self, left_section):
        if self.error_manager:
            self.error_manager.left_section = left_section
    
    """
    에러 아이템으로 이동 : result page의 메서드 호출
    """
    def navigate_to_error_item(self, error_info):
        if self.result_page and hasattr(self.result_page, 'navigate_to_error_item'):
            self.result_page.navigate_to_error_item(error_info)

    """
    탭 변경 처리
    """
    def on_tab_changed(self, tab_name, index):
        self.tab_changed.emit(tab_name, index)

        # 특정 탭에 대한 추가 처리
        if tab_name == 'Material' and hasattr(self.result_page, 'material_widget'):
            if (self.result_page.material_widget and 
                hasattr(self.result_page, 'result_data') and 
                self.result_page.result_data is not None):
                self.result_page.material_widget.run_analysis(self.result_page.result_data)
        
        elif tab_name == 'Shipment' and hasattr(self.result_page, 'shipment_widget'):
            if (self.result_page.shipment_widget and 
                hasattr(self.result_page, 'result_data') and 
                self.result_page.result_data is not None):
                self.result_page.shipment_widget.run_analysis(self.result_page.result_data)

    """
    KPI 업데이트
    """
    def update_kpi(self, kpi_data):
        if self.kpi_widget:
            self.kpi_widget.update_scores(**kpi_data)
            self.kpi_updated.emit(kpi_data)

    """
    시각화 업데이트
    """
    def update_visualizations(self, capa_data=None, utilization_data=None):
        # 데이터 저장
        if capa_data is not None:
            self.capa_ratio_data = capa_data
        if utilization_data is not None:
            self.utilization_data = utilization_data
        
        # Capa 탭 업데이트
        capa_tab = self.tab_manager.get_tab_instance('Capa')
        if capa_tab and hasattr(capa_tab, 'update_content'):
            capa_tab.update_content(self.capa_ratio_data, self.utilization_data)
    
    """
    검증 에러 추가
    """
    def add_validation_error(self, item_info, error_message):
        if self.error_manager:
            return self.error_manager.add_validation_error(item_info, error_message)
        return {}
    
    """
    검증 에러 제거
    """
    def remove_validation_error(self, item_info):
        if self.error_manager:
            self.error_manager.remove_validation_error(item_info)
    
    """
    데이터 업데이트
    """
    def update_data(self, data):
        self.current_data = data
        self.data_changed.emit(data)
        
        # 각 탭에 데이터 전달
        if self.tab_manager:
            for tab_name in ['Summary', 'Material', 'Shipment', 'SplitView']:
                tab_instance = self.tab_manager.get_tab_instance(tab_name)
                if tab_instance and hasattr(tab_instance, 'update_content'):
                    tab_instance.update_content(data)
    
    """
    현재 선택된 탭 반환
    """
    def get_current_tab(self):
        if self.tab_manager:
            return self.tab_manager.current_tab_idx
        return 0
    
    """
    특정 탭으로 전환
    """
    def switch_to_tab(self, index):
        if self.tab_manager:
            self.tab_manager.switch_tab(index)
    
    """
    정리 작업
    """
    def cleanup(self):
        if self.signal_manager:
            self.signal_manager.disconnect_all()
        super().cleanup()