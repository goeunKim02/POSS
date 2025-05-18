
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QCursor
from app.resources.styles.result_style import ResultStyles
from app.views.components.result_components.right_section.summary_tab import SummaryTab
from app.views.components.result_components.right_section.capa_tab import CapaTab
from app.views.components.result_components.right_section.material_tab import MaterialTab
from app.views.components.result_components.right_section.plan_tab import PlanTab
from app.views.components.result_components.right_section.portcapa_tab import PortCapaTab
from app.views.components.result_components.right_section.shipment_tab import ShipmentTab
from app.views.components.result_components.right_section.splitview_tab import SplitViewTab

"""결과 페이지 시각화 탭 관리 클래스"""
class TabManager(QObject):
    # 탭 설정 정보
    TAB_CONFIGS = {
        'Summary':  {'class': SummaryTab},
        'Capa':     {'class': CapaTab},
        'Material': {'class': MaterialTab},
        'PortCapa': {'class': PortCapaTab},
        'Plan':     {'class': PlanTab},
        'Shipment': {'class': ShipmentTab},
        'SplitView':{'class': SplitViewTab},
    }


    tab_changed = pyqtSignal(str, int)  # 탭이름, 인덱스

    def __init__(self, parent_page):
        super().__init__(parent_page)
        self.parent_page = parent_page
        self.tab_names = list(self.TAB_CONFIGS.keys())
        self.buttons = []
        self.stack_widget = None
        self.current_tab_idx = 0
        self.tab_instances = {}

    """
    QStackedWidget 객체 연결
    """
    def set_stack_widget(self, stack_widget: QStackedWidget):
        print("[TabManager] set_stack_widget() 호출 :", stack_widget)
        self.stack_widget = stack_widget
        
    """
    탭 버튼 생성 + 페이지 인스턴스화 → 스택에 추가
    button_layout: 버튼을 붙일 레이아웃
    stack_widget은 반드시 set_stack_widget() 이후에 호출하세요.
    """
    def create_tab_buttons(self, button_layout: QHBoxLayout):
        if self.stack_widget is None:
            raise RuntimeError("Call set_stack_widget() 먼저 해주세요.")

        for idx, name in enumerate(self.tab_names):
            # 1) 탭 페이지 생성
            TabClass = self.TAB_CONFIGS[name]['class']
            page = TabClass(parent=self.parent_page)

            # 2) 스택에 추가 & 참조 저장
            self.stack_widget.addWidget(page)
            self.tab_instances[name] = page

            # 3) 버튼 생성
            btn = QPushButton(name)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFixedHeight(50)
            # 첫 탭만 활성 스타일
            btn.setStyleSheet(
                ResultStyles.ACTIVE_BUTTON_STYLE if idx == 0 
                else ResultStyles.INACTIVE_BUTTON_STYLE
            )
            # 클릭 시 전환
            btn.clicked.connect(lambda _, i=idx: self.switch_tab(i))

            button_layout.addWidget(btn)
            self.buttons.append(btn)

        # 초기 탭 활성화
        self.switch_tab(0)
    
    
    """
    버튼 클릭 시 호출되어 스택 위젯을 전환하고 버튼 스타일 갱신
    """
    def switch_tab(self, idx: int):
        if not self.stack_widget or idx < 0 or idx >= len(self.tab_names):
            return

        # 1) 스택 위젯 인덱스 전환
        self.stack_widget.setCurrentIndex(idx)
        self.current_tab_idx = idx

        # 2) 버튼 스타일 업데이트
        for i, btn in enumerate(self.buttons):
            btn.setStyleSheet(
                ResultStyles.ACTIVE_BUTTON_STYLE if i == idx 
                else ResultStyles.INACTIVE_BUTTON_STYLE
            )

        # 3) 탭별 콘텐츠 업데이트 (필요한 경우)
        tab_name = self.tab_names[idx]
        page = self.tab_instances.get(tab_name)
        # capa 탭은 두가지 parameter 필요 
        if tab_name == 'Capa' and page:
            page.update_content(getattr(self.parent_page, 'capa_ratio_data', None),
                                getattr(self.parent_page, 'utilization_data', None))
        elif page and hasattr(page, 'update_content'):
            # parent_page에 저장된 데이터를 넘겨줍니다.
            data = getattr(self.parent_page, f"{tab_name.lower()}_data", None)
            page.update_content(data)

        # 4) 시그널 방출
        self.tab_changed.emit(tab_name, idx)

    
    """
    탭 인스턴스 반환
    """
    def get_tab_instance(self, tab_name):
        return self.tab_instances.get(tab_name)
    