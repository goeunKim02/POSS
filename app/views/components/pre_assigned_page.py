import os
import pandas as pd

from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QDialog, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal

from ...resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from .pre_assigned_components.summary import SummaryWidget
from .pre_assigned_components.calendar_header import CalendarHeader
from .pre_assigned_components.weekly_calendar import WeeklyCalendar
from .pre_assigned_components.project_group_dialog import ProjectGroupDialog
from app.utils.fileHandler import create_from_master
from app.utils.export_manager import ExportManager

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
    optimization_requested = pyqtSignal(dict)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._df = pd.DataFrame()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # 제목 및 버튼 레이아웃
        title_hbox = QHBoxLayout()
        lbl = QLabel("Pre-Assignment")
        font_title = QFont("Arial", 15)
        font_title.setBold(True)
        font_title.setWeight(99)
        lbl.setFont(font_title)
        title_hbox.addWidget(lbl)

        btn_export = create_button("Export", "primary", self)
        btn_export.clicked.connect(self.on_export_click)
        title_hbox.addWidget(btn_export)

        self.btn_run = create_button("Run", "primary", self)
        self.btn_run.clicked.connect(self.on_run_click)
        title_hbox.addWidget(self.btn_run)

        btn_reset = create_button("Reset", "secondary", self)
        btn_reset.clicked.connect(self.on_reset_click)
        title_hbox.addWidget(btn_reset)

        layout.addLayout(title_hbox)

        # 본문 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scroll_area.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        # 본문 컨테이너
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        self.scroll_area.setWidget(self.body_container)

        self.setLayout(layout)

        # 헤더 마진
        sb = self.scroll_area.verticalScrollBar()
        sb.rangeChanged.connect(lambda low, high: self._sync_header_margin())

    # 헤더 마진 조정
    def _sync_header_margin(self):
        if not hasattr(self, 'header'):
            return
        
        sb = self.scroll_area.verticalScrollBar()
        has_scroll = sb.maximum() > 0
        right_margin = sb.sizeHint().width() if has_scroll else 0

        self.header.layout().setContentsMargins(0, 10, right_margin, 6)

    # 엑셀 파일로 내보내기
    def on_export_click(self):
        # 데이터가 있는지 확인
        if self._df is None or self._df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
        
        try:
            start_date, end_date = self.main_window.data_input_page.date_selector.get_date_range()
        except Exception as e:
            # 날짜 범위를 가져올 수 없는 경우 기본값 사용
            print("Could not retrieve date range. Using current date instead")
            start_date, end_date = None, None

        # 통합 내보내기 사용
        ExportManager.export_data(
            parent=self,
            data_df=self._df,
            start_date=start_date,
            end_date=end_date,
            is_planning=True  # 사전할당 페이지임을 표시
        )

    # 캘린더 초기화
    def on_reset_click(self):
        cols = ["Line", "Time", "Qty", "Item", "Project"]
        self._df = pd.DataFrame(columns=cols)

        old = self.scroll_area.takeWidget()
        if old:
            old.deleteLater()

        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0,0,0,0)
        self.body_layout.setSpacing(0)
        self.scroll_area.setWidget(self.body_container)

        if getattr(self, 'header', None):
            self.header.deleteLater()
            self.header = None

        if getattr(self, 'main_container', None):
            self.layout().removeWidget(self.main_container)
            self.main_container.deleteLater()
            self.main_container = None

        if getattr(self, 'summary_widget', None):
            self.summary_widget.deleteLater()
            self.summary_widget = None

    # 최적화 요청
    def on_run_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Error", "You need to load the results by running it first.")
            return

        all_groups = create_from_master()
        current = set(self._df['Project'])
        filtered = {gid: projs for gid, projs in all_groups.items() if current & set(projs)}

        dlg = ProjectGroupDialog(filtered, self._df, parent=self)
        dlg.optimizationDone.connect(self._on_optimization_prepare)
        dlg.exec_()

    # 실제 최적화 완료 처리
    def _on_optimization_prepare(self, result_df, filtered_df):
        self.filtered_df = filtered_df

        if hasattr(self.main_window, 'result_page'):
            pre_assigned_items = self.filtered_df['Item'].unique().tolist()
            
            self.main_window.result_page.set_optimization_result({
                'assignment_result': result_df,
                'pre_assigned_items': pre_assigned_items,
            })
            self.main_window.navigate_to_page(2)
        else:
            self.optimization_requested.emit({
                'assignment_result': result_df
            })

    # 결과 데이터 표시
    def display_preassign_result(self, df: pd.DataFrame):
        self._df = df.copy()
        
        agg_qty = (
            df.groupby(['Line','Time','Project'], as_index=False)
            ['Qty']
            .sum()
        )
        detail_series = df.groupby(['Line','Time','Project']).apply(
            lambda g: g[
                ['Demand','Item','To_site','SOP','MFG','RMC','Due_LT','Qty']
            ].to_dict('records')
        )
        details = (
            detail_series
            .to_frame('Details')
            .reset_index()
        )
        df_agg = agg_qty.merge(
            details,
            on=['Line','Time','Project']
        )

        # 요약 위젯
        summary = SummaryWidget(df, parent=self)
        
        # 캘린더 헤더
        header = CalendarHeader(set(df['Time']), parent=self)

        # 기존 위젯 제거
        if getattr(self, 'summary_widget', None):
            self.summary_widget.deleteLater()
            self.summary_widget = None
        if getattr(self, 'header', None):
            self.header.deleteLater()
            self.header = None

        # 본문 레이아웃 초기화
        for i in reversed(range(self.body_layout.count())):
            w = self.body_layout.takeAt(i).widget()
            if w:
                w.deleteLater()

        # 왼쪽: 헤더 + 달력
        left_container = QWidget(parent=self)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(header)
        left_layout.addWidget(self.scroll_area)
        left_layout.addStretch()

        # 메인 컨테이너: 캘린더 + 요약
        main_container = QWidget(parent=self)
        main_hbox = QHBoxLayout(main_container)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)
        main_hbox.addWidget(left_container, stretch=3)
        main_hbox.addWidget(summary, stretch=1, alignment=Qt.AlignTop)

        self.layout().insertWidget(1, main_container)

        self.body_layout.addWidget(WeeklyCalendar(df_agg))

        self.summary_widget = summary
        self.header = header

        self._sync_header_margin()