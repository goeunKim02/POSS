from PyQt5.QtGui import QFont, QCursor, QMovie, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QScrollArea, QDialog
from PyQt5.QtCore import Qt, pyqtSignal, QStandardPaths, QThread, QSize

import os
import pandas as pd

from ...resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from .pre_assigned_components.calendar_header import CalendarHeader
from .pre_assigned_components.weekly_calendar import WeeklyCalendar
from .pre_assigned_components.project_group_dialog import ProjectGroupDialog
from app.utils.fileHandler import create_from_master
from app.core.optimizer import Optimizer
from app.views import main_window
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

class ProcessThread(QThread):
    finished = pyqtSignal(pd.DataFrame)

    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.df = df

    # 테스트용(실제 처리 로직으로 교체)
    def run(self):
        import time

        time.sleep(10)  # 테스트용 지연
        self.finished.emit(self.df) # 테스트용 원본 데이터 반환

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

        # 캘린더 헤더
        self.header = CalendarHeader(self)
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
        self.body_layout.addWidget(WeeklyCalendar(self._df))

    # 최적화 요청
    def on_run_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Error", "먼저 Run을 통해 결과를 불러와야 합니다.")
            return

        # 화면에 표시된 데이터 기반 프로젝트 그룹 필터링
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
        selected_projects = set()
        for gid in selected:
            selected_projects.update(filtered_groups[gid])

        # 클래스 맴버 변수로 저장
        self.filtered_df = self._df[self._df['Project'].isin(selected_projects)].copy()
        self.selected_projects = list(selected_projects)

        # 실행 버튼 비활성화
        self.btn_run.setEnabled(False)
        self.btn_run.setText("Processing...")
        self.run_spinner.start()

        try:
            # 최적화 알고리즘 직접 실행
            optimizer = Optimizer()
            results = optimizer.run_optimization({
                'pre_assigned_df': self.filtered_df,
                'selected_projects': list(self.selected_projects)
            })
            
            # 결과를 결과 페이지로 전달
            if hasattr(self.main_window, 'result_page'):
                self.main_window.result_page.left_section.set_data_from_external(results['assignment_result'])
                self.main_window.navigate_to_page(2)
            else:
                self.optimization_requested.emit(results)
                
        except Exception as e:
            QMessageBox.critical(self, "최적화 오류", f"최적화 과정에서 오류가 발생했습니다: {str(e)}")
        finally:
            # 실행 버튼 상태 복원
            self.run_spinner.stop()  # 로딩 애니메이션 중지
            self.btn_run.setIcon(QIcon())  # 아이콘 제거
            self.btn_run.setText("Run")
            self.btn_run.setEnabled(True)
            self.btn_run.setStyleSheet(PRIMARY_BUTTON_STYLE)

    def _on_process_done(self, result_df):
        # 실행 버튼 활성화
        self.run_spinner.stop()
        self.btn_run.setIcon(QIcon())

        self.btn_run.setText("Run")
        self.btn_run.setEnabled(True)
        self.btn_run.setStyleSheet(PRIMARY_BUTTON_STYLE)

        print(result_df)

    def _update_run_icon(self):
        pix = self.run_spinner.currentPixmap()
        if not pix.isNull():
            self.btn_run.setIcon(QIcon(pix))


    # 결과 데이터 표시
    def display_preassign_result(self, df: pd.DataFrame):
        self._df = df
        for i in range(self.body_layout.count()-1, -1, -1):
            w = self.body_layout.takeAt(i).widget()
            if w:
                w.deleteLater()
        self.body_layout.addWidget(WeeklyCalendar(self._df))