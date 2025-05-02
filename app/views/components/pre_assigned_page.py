from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QScrollArea, QDialog
from PyQt5.QtCore import Qt, pyqtSignal, QStandardPaths

import os
import pandas as pd

from ...resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from .pre_assigned_components.calendar_header import CalendarHeader
from .pre_assigned_components.weekly_calendar import WeeklyCalendar
from .pre_assigned_components.project_group_dialog import ProjectGroupDialog
from app.utils.fileHandler import create_from_master

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

        # 제목 및 버튼 레이아웃
        title_hbox = QHBoxLayout()
        lbl = QLabel("Pre-Assigned Calendar View")
        font_title = QFont("Arial", 15)
        font_title.setBold(True)
        lbl.setFont(font_title)
        title_hbox.addWidget(lbl)
        title_hbox.addStretch()

        btn_export = create_button("Export", "primary", self)
        btn_export.clicked.connect(self.on_export_click)
        title_hbox.addWidget(btn_export)

        btn_run = create_button("Run", "primary", self)
        btn_run.clicked.connect(self.on_run_click)
        title_hbox.addWidget(btn_run)

        btn_reset = create_button("Reset", "secondary", self)
        btn_reset.clicked.connect(self.on_reset_click)
        title_hbox.addWidget(btn_reset)

        layout.addLayout(title_hbox)

        # 본문 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 캘린더 헤더
        self.header = CalendarHeader(self)
        layout.addWidget(self.header)

        # 본문 컨테이너
        layout.addWidget(self.scroll_area)
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        self.scroll_area.setWidget(self.body_container)

        # 헤더 마진
        self._sync_header_margin()
        sb = self.scroll_area.verticalScrollBar()
        sb.rangeChanged.connect(lambda low, high: self._sync_header_margin())

        self.setLayout(layout)

    # 헤더 마진 조정
    def _sync_header_margin(self):
        sb = self.scroll_area.verticalScrollBar()
        has_scroll = sb.maximum() > 0
        right_margin = sb.sizeHint().width() if has_scroll else 0

        self.header.layout().setContentsMargins(0, 10, right_margin, 0)

    # 엑셀 파일로 내보내기
    def on_export_click(self):
        options = QFileDialog.Options()
        desktop_dir = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        default_path = os.path.join(desktop_dir, "initial_assign.xlsx")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as Excel", default_path,
            "Excel Files (*.xlsx);;All Files (*)", options=options
        )
        if not file_path:
            return
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        try:
            self._df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Export Success", f"파일이 다음 경로로 저장되었습니다: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"엑셀 파일 저장 중 오류가 발생했습니다: {e}")

    # 캘린더 초기화
    def on_reset_click(self):
        cols = ["Line","Time","Qty","Item","Project"]
        empty_df = pd.DataFrame(columns=cols)

        self._df = empty_df
        for i in range(self.body_layout.count()-1, -1, -1):
            w = self.body_layout.takeAt(i).widget()
            if w:
                w.deleteLater()
        self.body_layout.addWidget(WeeklyCalendar(self._df))

    # 최적화 요청
    def on_run_click(self):
        if self._df.empty:
            QMessageBox.warning(self, "Error", "먼저 Run을 통해 결과를 불러와야 합니다.")
            return

        # 전체 프로젝트 그룹 생성
        all_groups = create_from_master()

        # 화면에 표시된 데이터 프로젝트 집합
        current = set(self._df['Project'])

        # 화면에 있는 프로젝트가 하나라도 포함된 그룹
        filtered_groups = {
            gid: projs
            for gid, projs in all_groups.items()
            if current & set(projs)
        }

        # 필터된 그룹을 다이얼로그에 전달
        dlg = ProjectGroupDialog(filtered_groups, parent=self)
        if dlg.exec_() != QDialog.Accepted:
            # 사용자가 취소를 누르면 함수 종료
            return

        # 사용자가 체크한 그룹 ID 리스트
        selected = dlg.selected_groups()

        # 선택된 그룹에 속한 모든 프로젝트 집합
        selected_projects = set()
        for gid in selected:
            selected_projects.update(filtered_groups[gid])

        filtered_df = self._df[self._df['Project'].isin(selected_projects)].copy()

        print(filtered_df)

    # 결과 데이터 표시
    def display_preassign_result(self, df: pd.DataFrame):
        self._df = df
        for i in range(self.body_layout.count()-1, -1, -1):
            w = self.body_layout.takeAt(i).widget()
            if w:
                w.deleteLater()
        self.body_layout.addWidget(WeeklyCalendar(self._df))