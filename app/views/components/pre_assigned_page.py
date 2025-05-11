import threading
import time
import os
import pandas as pd

from PyQt5.QtGui import QFont, QCursor, QMovie, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QScrollArea, QDialog, QProgressBar, QStyleFactory
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSize
from datetime import datetime

from ...resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from .pre_assigned_components.calendar_header import CalendarHeader
from .pre_assigned_components.weekly_calendar import WeeklyCalendar
from .pre_assigned_components.project_group_dialog import ProjectGroupDialog
from app.utils.fileHandler import create_from_master
from app.core.optimizer import Optimizer
from app.utils.export_manager import ExportManager
from app.models.common.settings_store import SettingsStore

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

class ProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame)

    def __init__(self, df: pd.DataFrame, projects: list, time_limit: int = None):
        super().__init__()
        self.df = df
        self.projects = projects
        # 설정된 time_limit 없으면 기본값 사용
        self.time_limit = time_limit or SettingsStore._settings.get("time_limit", 300)
        self._opt_result = None

    def run(self):
        # 최적화 작업
        def do_opt():
            results = Optimizer().run_optimization({
                'pre_assigned_df': self.df,
                'selected_projects': self.projects
            })
            self._opt_result = results['assignment_result']

        opt_thread = threading.Thread(target=do_opt, daemon=True)
        opt_thread.start()

        # 진행률 업데이트
        for i in range(self.time_limit):
            time.sleep(1)
            pct = int((i+1) / self.time_limit * 100)
            self.progress.emit(pct)

            if self._opt_result is not None:
                self.progress.emit(100)
                self.finished.emit(self._opt_result)
                return

        # 시간 제한 후 처리
        if self._opt_result is not None:
            self.finished.emit(self._opt_result)
        else:
            self.finished.emit(self.df)

class PlanningPage(QWidget):
    optimization_requested = pyqtSignal(dict)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._df = pd.DataFrame()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 제목 및 버튼 레이아웃
        title_hbox = QHBoxLayout()
        lbl = QLabel("Pre-Assignment")
        font_title = QFont("Arial", 15)
        font_title.setBold(True)
        font_title.setWeight(99)
        lbl.setFont(font_title)
        title_hbox.addWidget(lbl)
        title_hbox.addStretch()

        btn_export = create_button("Export", "primary", self)
        btn_export.clicked.connect(self.on_export_click)
        title_hbox.addWidget(btn_export)

        self.btn_run = create_button("Run", "primary", self)
        self.btn_run.clicked.connect(self.on_run_click)
        self.btn_run.setIconSize(QSize(32,32))
        title_hbox.addWidget(self.btn_run)

        icon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources/icon'))
        gif_path = os.path.join(icon_dir, 'loading.gif')

        self.run_spinner = QMovie(gif_path)
        self.run_spinner.setScaledSize(QSize(32,32))
        self.run_spinner.frameChanged.connect(self._update_run_icon)
        self.btn_run.setIcon(QIcon())

        btn_reset = create_button("Reset", "secondary", self)
        btn_reset.clicked.connect(self.on_reset_click)
        title_hbox.addWidget(btn_reset)

        layout.addLayout(title_hbox)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        self.progress_bar.setStyle(QStyleFactory.create("Fusion"))

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #AAA;
                border-radius: 4px;
                text-align: center;
                background-color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #1428A0;
                width: 20px;
            }
        """)
        
        layout.addWidget(self.progress_bar)

        # 캘린더 헤더
        present_times = set(self._df['Time']) if not self._df.empty else set()
        self.header = CalendarHeader(present_times, parent=self)
        layout.addWidget(self.header)

        # 본문 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 본문 컨테이너
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        self.scroll_area.setWidget(self.body_container)

        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        # 헤더 마진
        self._sync_header_margin()
        sb = self.scroll_area.verticalScrollBar()
        sb.rangeChanged.connect(lambda low, high: self._sync_header_margin())

    # 헤더 마진 조정
    def _sync_header_margin(self):
        sb = self.scroll_area.verticalScrollBar()
        has_scroll = sb.maximum() > 0
        right_margin = sb.sizeHint().width() if has_scroll else 0

        self.header.layout().setContentsMargins(0, 10, right_margin, 0)

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

        for i in range(self.body_layout.count() - 1, -1, -1):
            w = self.body_layout.takeAt(i).widget()
            if w:
                w.deleteLater()

        present_times = set(self._df['Time'])
        self.header.setParent(None)
        self.header = CalendarHeader(present_times, parent=self)
        self.layout().insertWidget(2, self.header)
        self._sync_header_margin()

        self.body_layout.addWidget(WeeklyCalendar(self._df))

    # 최적화 요청
    def on_run_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Error", "먼저 Run을 통해 결과를 불러와야 합니다.")
            return

        all_groups = create_from_master()
        current = set(self._df['Project'])
        filtered_groups = {
            gid: projs for gid, projs in all_groups.items()
            if current & set(projs)
        }
        dlg = ProjectGroupDialog(filtered_groups, parent=self)
        if dlg.exec_() != QDialog.Accepted:
            return
        selected = dlg.selected_groups()
        self.selected_projects = set()
        for gid in selected:
            self.selected_projects |= set(filtered_groups[gid])
        self.filtered_df = self._df[self._df['Project'].isin(self.selected_projects)].copy()

        self.btn_run.setEnabled(False)
        self.btn_run.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        self.thread = ProcessThread(
            self.filtered_df,
            list(self.selected_projects),
            time_limit=SettingsStore._settings.get("time_limit", 300)
        )
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self._on_optimization_prepare)
        self.thread.start()

    # 실제 최적화 로직
    def _on_optimization_prepare(self, result_df: pd.DataFrame):
        self.progress_bar.setValue(100)

        if hasattr(self.main_window, 'result_page'):
            # 사전할당된 아이템 리스트
            pre_assigned_items = self.filtered_df['Item'].unique().tolist()
            
            # 새로운 메서드 호출
            self.main_window.result_page.set_optimization_result({
                'assignment_result': result_df,
                'pre_assigned_items': pre_assigned_items,
                'optimization_metadata': {
                    'execution_time': datetime.now(),
                    'selected_projects': self.selected_projects
                }
            })
            # 페이지 전환
            self.main_window.navigate_to_page(2)
        else:
            self.optimization_requested.emit({'assignment_result': result_df})

        self.progress_bar.hide()
        self.btn_run.setEnabled(True)
        self.btn_run.setStyleSheet(PRIMARY_BUTTON_STYLE)

    def _update_run_icon(self):
        pix = self.run_spinner.currentPixmap()
        if not pix.isNull():
            self.btn_run.setIcon(QIcon(pix))

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

        old_header = self.header
        self.layout().removeWidget(old_header)
        old_header.deleteLater()
        
        self.header = CalendarHeader(set(df_agg['Time']), parent=self)
        self.layout().insertWidget(2, self.header)
        self._sync_header_margin()

        for i in range(self.body_layout.count()-1, -1, -1):
            w = self.body_layout.takeAt(i).widget()
            if w:
                w.deleteLater()
        self.body_layout.addWidget(WeeklyCalendar(df_agg))