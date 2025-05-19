import pandas as pd

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QSizePolicy,
    QLabel, QFrame, QScrollArea, QWidget, QPushButton, QProgressBar, QStackedLayout, QApplication
)
from ....resources.styles.pre_assigned_style import (
    DETAIL_DIALOG_STYLE
)
from .processThread import ProcessThread

"""
프로젝트 그룹을 선택하는 팝업
"""
class ProjectGroupDialog(QDialog):
    optimizationDone = pyqtSignal(pd.DataFrame, pd.DataFrame)

    def __init__(self, project_groups: dict, df, on_done_callback=None, parent=None):
        super().__init__(parent)
        self.df = df
        self.project_groups = project_groups
        self.df_to_opt = None

        if on_done_callback:
            self.optimizationDone.connect(on_done_callback)

        self.setStyleSheet(DETAIL_DIALOG_STYLE)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Select Project Groups")
        self.setModal(True)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 제목 프레임
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("background-color: #1428A0; border: none;")
        title_frame.setFixedHeight(60)

        # 제목 프레임 레이아웃
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 0, 20, 0)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 제목 레이블
        title_label = QLabel("Select Project Groups")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)

        main_layout.addWidget(title_frame)

        # 콘텐츠 영역
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # 설명 레이블 프레임
        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 10px; border: 1px solid #cccccc; }
        """)
        desc_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        desc_frame.setMinimumHeight(20)
        
        self.desc_stack = QStackedLayout(desc_frame)

        # 설명 라벨
        page_desc = QWidget()
        pd_layout = QVBoxLayout(page_desc)
        pd_layout.setContentsMargins(20, 15, 20, 15)
        self.desc_label = QLabel(
            "Select the project group to include in the optimization process"
        )
        self.desc_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.desc_label.setStyleSheet("background-color: transparent; color: #333333; border: none;")
        pd_layout.addWidget(self.desc_label)
        self.desc_stack.addWidget(page_desc)

        # 프로그레스바
        page_prog = QWidget()
        pp_layout = QVBoxLayout(page_prog)
        pp_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #AAA; border-radius: 10px; text-align: center; background-color: #E0E0E0; }
            QProgressBar::chunk { background-color: #1428A0;}
        """)
        pp_layout.addWidget(self.progress_bar)
        pp_layout.setStretch(pp_layout.indexOf(self.progress_bar), 1)
        
        self.desc_stack.addWidget(page_prog)
        self.desc_stack.setCurrentIndex(0)

        content_layout.addWidget(desc_frame)
        
        # 체크박스 영역
        checkbox_frame = QFrame()
        checkbox_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """)
        checkbox_layout = QVBoxLayout(checkbox_frame)
        checkbox_layout.setContentsMargins(20, 20, 20, 20)
        checkbox_layout.setSpacing(10)

        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")

        # 스크롤 컨텐츠 위젯
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        # 체크박스 생성
        self.checkboxes = {}

        for group_id, projects in project_groups.items():
            cb = QCheckBox(f"{', '.join(projects)}")
            cb.setStyleSheet("""
                QCheckBox {
                    font-family: Arial;
                    font-size: 11pt;
                    color: #333333;
                    padding: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox:hover {
                    background-color: #f0f0f0;
                    border-radius: 4px;
                }
            """)
            cb.setChecked(False)
            cb.stateChanged.connect(self._update_ok_button)

            scroll_layout.addWidget(cb)
            self.checkboxes[group_id] = cb

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        checkbox_layout.addWidget(scroll_area)

        content_layout.addWidget(checkbox_frame)
        content_layout.addStretch(1)

        # 스크롤 영역
        main_scroll_area = QScrollArea()
        main_scroll_area.setWidgetResizable(True)
        main_scroll_area.setStyleSheet("background-color: #F9F9F9; border: none;")
        main_scroll_area.setWidget(content_widget)
        main_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_layout.addWidget(main_scroll_area)

        # 버튼 프레임
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #F0F0F0; border: none;")
        button_frame.setFixedHeight(80)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 20, 30, 20)
        button_layout.addStretch(1)

        # OK 버튼
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(100, 40)

        ok_font = QFont("Arial", 11)
        ok_font.setBold(True)

        self.ok_button.setFont(ok_font)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                border: none;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1e429f;
            }
            QPushButton:disabled {
                background-color: #ACACAC;
                color: white;
            }
        """)
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self._on_ok_clicked)

        # Cancel 버튼
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(100, 40)
        cancel_font = QFont("Arial", 11)
        cancel_font.setBold(True)
        self.cancel_button.setFont(cancel_font)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                border: none;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #545B62;
            }
        """)
        self.cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addSpacing(15)
        button_layout.addWidget(self.cancel_button)

        main_layout.addWidget(button_frame)

        self.setFixedWidth(1000)
        self.adjustSize()

    """
    OK 버튼 활성화 상태 업데이트
    """
    def _update_ok_button(self):
        any_checked = any(cb.isChecked() for cb in self.checkboxes.values())
        self.ok_button.setEnabled(any_checked)

        # 활성화 상태에 따른 커서 설정
        if any_checked:
            self.ok_button.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            self.ok_button.setCursor(Qt.ArrowCursor)

    """
    사용자가 선택한 프로젝트 그룹 리스트 반환
    """
    def selected_groups(self):
        return [gid for gid, cb in self.checkboxes.items() if cb.isChecked()]

    """
    OK 버튼 클릭 시 호출출
    """
    def _on_ok_clicked(self):
        gids = [gid for gid, cb in self.checkboxes.items() if cb.isChecked()]
        projects = sum((self.project_groups[gid] for gid in gids), [])
        self.df_to_opt = self.df[self.df['Project'].isin(projects)].copy()

        self.desc_stack.setCurrentIndex(1)
        self.ok_button.setEnabled(False)

        for cb in self.checkboxes.values():
           cb.setEnabled(False)

        self.thread = ProcessThread(self.df_to_opt, projects)
        self.thread.progress.connect(self._on_progress)
        self.thread.finished.connect(self._on_finished)
        self.thread.start()

    """
    프로세스 진행 사항 업데이트
    """
    @pyqtSlot(int, int)
    def _on_progress(self, pct: int, remaining: int):
        self.progress_bar.setValue(pct)

        m, s = divmod(remaining, 60)
        self.progress_bar.setFormat(f"{pct}%   remaining time {m}:{s:02d}")

    """
    프로세스 완료 시 호출 
    """
    @pyqtSlot(pd.DataFrame)
    def _on_finished(self, result_df: pd.DataFrame):
        self._on_progress(100, 0)
        QApplication.processEvents()

        self.optimizationDone.emit(result_df, self.df_to_opt)
        self.accept()