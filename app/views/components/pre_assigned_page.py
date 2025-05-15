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

def create_button(text, style="primary", parent=None):
    btn = QPushButton(text, parent)
    font = QFont("Arial", 9); font.setBold(True)
    btn.setFont(font)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFixedSize(150, 50)
    btn.setStyleSheet(PRIMARY_BUTTON_STYLE if style=="primary" else SECONDARY_BUTTON_STYLE)
    return btn

class PlanningPage(QWidget):
    optimization_requested = pyqtSignal(dict)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._df = pd.DataFrame()
        self._setup_ui()

    def _setup_ui(self):
        # 메인 레이아웃
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)

        title_hbox = QHBoxLayout()
        lbl = QLabel("Pre-Assignment")
        f = QFont("Arial",15); f.setBold(True)
        lbl.setFont(f)
        title_hbox.addWidget(lbl)

        btn_export = create_button("Export","primary",self)
        btn_export.clicked.connect(self.on_export_click)
        title_hbox.addWidget(btn_export)

        self.btn_run = create_button("Run","primary",self)
        self.btn_run.clicked.connect(self.on_run_click)
        title_hbox.addWidget(self.btn_run)

        btn_reset = create_button("Reset","secondary",self)
        btn_reset.clicked.connect(self.on_reset_click)
        title_hbox.addWidget(btn_reset)

        self.main_layout.addLayout(title_hbox)

        # 스크롤 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0,0,0,0)
        self.body_layout.setSpacing(0)
        self.scroll_area.setWidget(self.body_container)

        self.setLayout(self.main_layout)

        self.scroll_area.verticalScrollBar().rangeChanged.connect(lambda l,h: self._sync_header_margin())

    def _sync_header_margin(self):
        if not hasattr(self, 'header'):
            return
        sb = self.scroll_area.verticalScrollBar()
        right = sb.sizeHint().width() if sb.maximum()>0 else 0
        self.header.layout().setContentsMargins(0,0,right,0)

    def on_export_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
        try:
            start, end = self.main_window.data_input_page.date_selector.get_date_range()
        except:
            start, end = None, None
        ExportManager.export_data(self, data_df=self._df,
                                  start_date=start, end_date=end,
                                  is_planning=True)

    def on_reset_click(self):
        self._df = pd.DataFrame(columns=["Line","Time","Qty","Item","Project"])

        if hasattr(self, 'main_container'):
            self.main_layout.removeWidget(self.main_container)
            self.main_container.deleteLater()
            del self.main_container

        if hasattr(self, 'scroll_area'):
            self.scroll_area.deleteLater()
            del self.scroll_area
        if hasattr(self, 'body_container'):
            del self.body_container
            del self.body_layout

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0,0,0,0)
        self.body_layout.setSpacing(0)
        self.scroll_area.setWidget(self.body_container)

        if hasattr(self, 'summary_widget'):
            self.summary_widget.deleteLater()
            del self.summary_widget
        if hasattr(self, 'header'):
            self.header.deleteLater()
            del self.header

    def on_run_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Error", "You need to load the results by running it first.")
            return
        all_groups = create_from_master()
        current = set(self._df['Project'])
        filtered = {gid: projs for gid,projs in all_groups.items() if current & set(projs)}

        dlg = ProjectGroupDialog(
            filtered,
            self._df,
            on_done_callback=self._on_optimization_prepare,
            parent=self
        )
        dlg.exec_()

    def _on_optimization_prepare(self, result_df, filtered_df):
        self.filtered_df = filtered_df
        if hasattr(self.main_window, 'result_page'):
            pre_items = filtered_df['Item'].unique().tolist()
            self.main_window.result_page.set_optimization_result({
                'assignment_result': result_df,
                'pre_assigned_items': pre_items
            })
            self.main_window.navigate_to_page(2)
        else:
            self.optimization_requested.emit({'assignment_result': result_df})

    def display_preassign_result(self, df: pd.DataFrame):
        self.on_reset_click()

        self._df = df.copy()
        agg = df.groupby(['Line','Time','Project'], as_index=False)['Qty'].sum()
        details = (
            df.groupby(['Line','Time','Project'])
              .apply(lambda g: g[['Demand','Item','To_site','SOP','MFG','RMC','Due_LT','Qty']]
                         .to_dict('records'))
              .to_frame('Details')
              .reset_index()
        )
        df_agg = agg.merge(details, on=['Line','Time','Project'])

        summary = SummaryWidget(df, parent=self)
        header  = CalendarHeader(set(df['Time']), parent=self)

        left = QWidget(self)
        left.setObjectName("leftContainer")
        left.setStyleSheet("""
            QWidget#leftContainer {
                border:1px solid #cccccc; border-radius:8px;
            }
            QWidget#leftContainer, QWidget#leftContainer * {
                background-color: white;
            }
        """)
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(20,20,20,20)
        left_l.setSpacing(6)
        left_l.addWidget(header)
        left_l.addWidget(self.scroll_area)
        left_l.addStretch()

        btn_bar = QHBoxLayout()
        btn_bar.setContentsMargins(0,0,0,0)
        btn_bar.setSpacing(5)

        # 요약
        btn_summary = QPushButton("Summary")
        btn_summary.setCursor(QCursor(Qt.PointingHandCursor))
        btn_summary.setStyleSheet(PRIMARY_BUTTON_STYLE)  # 처음엔 활성 상태
        btn_summary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_summary.setFixedHeight(36)
        btn_bar.addWidget(btn_summary)

        stack = QStackedWidget()
        stack.addWidget(summary)

        def switch(idx):
            stack.setCurrentIndex(idx)
            btn_summary.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE if idx==0 else ResultStyles.INACTIVE_BUTTON_STYLE)

        btn_summary.clicked.connect(lambda: switch(0))

        right = QWidget(self)
        right.setObjectName("rightContainer")
        right.setStyleSheet("""
            QWidget#rightContainer {
                border:1px solid #cccccc; border-radius:8px;
            }
            QWidget#rightContainer, QWidget#rightContainer * {
                background-color: white;
            }
        """)
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(20,20,20,20)
        right_l.setSpacing(6)
        right_l.addLayout(btn_bar)
        right_l.addWidget(stack)
        right_l.addStretch()

        self.main_container = QWidget(self)
        mh = QHBoxLayout(self.main_container)
        mh.setContentsMargins(0,0,0,0)
        mh.setSpacing(10)
        mh.addWidget(left, 3)
        mh.addWidget(right, 1)

        self.body_layout.addWidget(WeeklyCalendar(df_agg))

        self.main_layout.insertWidget(1, self.main_container)

        self.summary_widget = summary
        self.header = header
        self._sync_header_margin()