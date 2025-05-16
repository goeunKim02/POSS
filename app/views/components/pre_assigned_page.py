import pandas as pd
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QScrollArea, QSizePolicy, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal

from ...resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from ...resources.styles.result_style import ResultStyles 
from .pre_assigned_components.summary import SummaryWidget
from .pre_assigned_components.calendar_header import CalendarHeader
from .pre_assigned_components.weekly_calendar import WeeklyCalendar
from .pre_assigned_components.project_group_dialog import ProjectGroupDialog
from app.utils.fileHandler import create_from_master
from app.utils.export_manager import ExportManager

"""
공통으로 사용하는 버튼 생성 함수
"""
def create_button(text, style="primary", parent=None):
    btn = QPushButton(text, parent)
    font = QFont("Arial", 9)
    font.setBold(True)
    btn.setFont(font)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFixedSize(150, 50)
    btn.setStyleSheet(
        PRIMARY_BUTTON_STYLE if style == "primary" else SECONDARY_BUTTON_STYLE
    )
    return btn


class PlanningPage(QWidget):
    # 최적화 요청 시그널
    optimization_requested = pyqtSignal(dict)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._df = pd.DataFrame()
        self._setup_ui()

    def _setup_ui(self):
        # 메인 레이아웃 (타이틀 + 버튼)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)

        title_hbox = QHBoxLayout()
        lbl = QLabel("Pre-Assignment")
        f = QFont("Arial", 15)
        f.setBold(True)
        lbl.setFont(f)
        title_hbox.addWidget(lbl)

        # Export 버튼
        btn_export = create_button("Export", "primary", self)
        btn_export.clicked.connect(self.on_export_click)
        title_hbox.addWidget(btn_export)

        # Run 버튼
        self.btn_run = create_button("Run", "primary", self)
        self.btn_run.clicked.connect(self.on_run_click)
        title_hbox.addWidget(self.btn_run)

        # Reset 버튼
        btn_reset = create_button("Reset", "secondary", self)
        btn_reset.clicked.connect(self.on_reset_click)
        title_hbox.addWidget(btn_reset)

        self.main_layout.addLayout(title_hbox)

        # main_container: 좌우 컨테이너 배치
        self.main_container = QWidget(self)
        mh = QHBoxLayout(self.main_container)
        mh.setContentsMargins(0, 0, 0, 0)
        mh.setSpacing(10)

        # LEFT: 캘린더 영역 (데이터 없을 때 placeholder 표시)
        self.leftContainer = QWidget(self)
        self.leftContainer.setObjectName("leftContainer")
        self.leftContainer.setStyleSheet("""
            QWidget#leftContainer {
                border: 1px solid #cccccc;
            }
            QWidget#leftContainer, 
            QWidget#leftContainer * {
                background-color: white;
            }
        """)
        left_l = QVBoxLayout(self.leftContainer)
        left_l.setContentsMargins(20, 20, 20, 20)
        left_l.setSpacing(6)

        # placeholder: 데이터 없을 때 문구
        self.placeholder_label = QLabel("Please Load to Data", self.leftContainer)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        left_l.addWidget(self.placeholder_label, stretch=1)

        # RIGHT: 요약 테이블 영역
        self.rightContainer = QWidget(self)
        self.rightContainer.setObjectName("rightContainer")
        self.rightContainer.setStyleSheet("""
            QWidget#rightContainer {
                border: 1px solid #cccccc;
            }
            QWidget#rightContainer, 
            QWidget#rightContainer * {
                background-color: white;
            }
        """)
        right_l = QVBoxLayout(self.rightContainer)
        right_l.setContentsMargins(20, 20, 20, 20)
        right_l.setSpacing(6)
        
        # Summary 버튼 영역
        btn_bar = QHBoxLayout()
        self.btn_summary = QPushButton("Summary")
        self.btn_summary.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_summary.setStyleSheet(ResultStyles.INACTIVE_BUTTON_STYLE)
        self.btn_summary.setFixedHeight(36)
        btn_bar.addWidget(self.btn_summary)
        right_l.addLayout(btn_bar)
        
        # SummaryWidget 영역
        self.stack = QStackedWidget(self.rightContainer)
        right_l.addWidget(self.stack, stretch=1)
        right_l.addStretch()

        mh.addWidget(self.leftContainer, 3)
        mh.addWidget(self.rightContainer, 1)
        self.main_layout.addWidget(self.main_container)

        self.setLayout(self.main_layout)

        # 시그널 중복 연결 방지용 플래그
        self._range_connected = False

    """
    스크롤바에 따른 margin 설정 
    """
    def _sync_header_margin(self):
        if not hasattr(self, 'header'):
            return
        sb = self.scroll_area.verticalScrollBar()
        right_margin = sb.sizeHint().width() if sb.maximum() > 0 else 0
        # 캘린더 헤더 레이아웃에 오른쪽 마진 설정
        self.header.layout().setContentsMargins(0, 0, right_margin, 0)

    def on_export_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
        try:
            start, end = self.main_window.data_input_page.date_selector.get_date_range()
        except:
            start, end = None, None
        ExportManager.export_data(
            self,
            data_df=self._df,
            start_date=start,
            end_date=end,
            is_planning=True
        )

    """
    reset 버튼 클릭시 호출
    """
    def on_reset_click(self):
        # 1) 내부 데이터 초기화
        self._df = pd.DataFrame(columns=["Line", "Time", "Qty", "Item", "Project"])

        # 2) LEFT 영역: 이전 header 제거
        if hasattr(self, 'header'):
            self.leftContainer.layout().removeWidget(self.header)
            self.header.deleteLater()
            del self.header

        # 3) LEFT 영역: 이전 scroll_area(캘린더) 제거
        if hasattr(self, 'scroll_area'):
            self.leftContainer.layout().removeWidget(self.scroll_area)
            self.scroll_area.deleteLater()
            del self.scroll_area

        # 4) RIGHT 영역: SummaryWidget 모두 제거
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()
        # Summary 버튼 스타일 비활성화
        self.btn_summary.setStyleSheet(ResultStyles.INACTIVE_BUTTON_STYLE)

        # 5) LEFT 영역: placeholder 재생성
        if hasattr(self, 'placeholder_label'):
            self.leftContainer.layout().removeWidget(self.placeholder_label)
            self.placeholder_label.deleteLater()
            del self.placeholder_label

        self.placeholder_label = QLabel("데이터가 없습니다", self.leftContainer)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.leftContainer.layout().addWidget(self.placeholder_label, stretch=1)

        self._range_connected = False

    """
    run 버튼 클릭시 호출
    """
    def on_run_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Error", "You need to load the results by running it first.")
            return
        all_groups = create_from_master()
        current = set(self._df['Project'])
        filtered = {
            gid: projs
            for gid, projs in all_groups.items()
            if current & set(projs)
        }

        dlg = ProjectGroupDialog(
            filtered,
            self._df,
            on_done_callback=self._on_optimization_prepare,
            parent=self
        )
        dlg.exec_()

    """
    projectGroupDialog에서 작업 완료 후 호출
    """
    def _on_optimization_prepare(self, result_df, filtered_df):
        self.filtered_df = filtered_df
        
        if hasattr(self.main_window, 'result_page'):
            pre_items = filtered_df['Item'].unique().tolist()
            # 결과를 ResultPage 에 전달
            self.main_window.result_page.set_optimization_result({
                'assignment_result': result_df,
                'pre_assigned_items': pre_items
            })
            self.main_window.navigate_to_page(2)
        else:
            self.optimization_requested.emit({'assignment_result': result_df})

    """
    사전 할당 결과 표시 함수
    """
    def display_preassign_result(self, df: pd.DataFrame):
        self.on_reset_click()

        if hasattr(self, 'placeholder_label'):
            self.leftContainer.layout().removeWidget(self.placeholder_label)
            self.placeholder_label.deleteLater()
            del self.placeholder_label

        # 데이터 준비
        self._df = df.copy()
        agg = df.groupby(['Line', 'Time', 'Project'], as_index=False)['Qty'].sum()
        details = (
            df.groupby(['Line', 'Time', 'Project'])
              .apply(lambda g: g[[
                  'Demand', 'Item', 'To_site', 'SOP', 'MFG', 'RMC', 'Due_LT', 'Qty'
              ]].to_dict('records'))
              .to_frame('Details')
              .reset_index()
        )
        df_agg = agg.merge(details, on=['Line', 'Time', 'Project'])

        # 캘린더 헤더 생성
        self.header = CalendarHeader(set(df['Time']), parent=self)

        # 캘린더 생성
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignTop)

        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        self.body_layout.setAlignment(Qt.AlignTop)

        calendar = WeeklyCalendar(df_agg)
        self.body_layout.addWidget(calendar, 0, Qt.AlignTop)

        self.scroll_area.setWidget(self.body_container)

        # 스크롤 시그널
        if not self._range_connected:
            self.scroll_area.verticalScrollBar().rangeChanged.connect(self._sync_header_margin)
            self._range_connected = True

        # 캘린더 헤더, 캘린더 배치
        left_l = self.leftContainer.layout()
        left_l.addWidget(self.header, stretch=0)
        left_l.addWidget(self.scroll_area, stretch=1)

        # 요약 테이블 생성, 버튼 연결
        summary = SummaryWidget(df, parent=self)
        self.stack.addWidget(summary)

        try:
            self.btn_summary.clicked.disconnect()
        except TypeError:
            pass

        def _on_summary_clicked():
            self.stack.setCurrentWidget(summary)
            self.btn_summary.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE)

        self.btn_summary.clicked.connect(_on_summary_clicked)

        self.stack.setCurrentWidget(summary)
        self.btn_summary.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE)