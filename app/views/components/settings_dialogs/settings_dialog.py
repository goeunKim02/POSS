# app/views/components/settings_dialogs/settings_dialog.py - 설정 다이얼로그 클래스
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QFrame, QApplication
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

# 분리된 탭 컴포넌트 import
from app.views.components.settings_dialogs.settings_components import (
    BasicTabComponent,
    PreOptionTabComponent,
    DetailTabComponent
)

from app.models.common.settings_store import SettingsStore


class SettingsDialog(QDialog):
    """설정 다이얼로그 창"""

    # 설정 변경 시그널 정의
    settings_changed = pyqtSignal(dict)  # 변경된 설정 값 딕셔너리

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Samsung Production Planning Optimization Settings")

        # 화면 크기 가져오기
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(self)
        screen_width, screen_height = screen_rect.width(), screen_rect.height()

        # 화면 크기의 80%로 다이얼로그 크기 설정
        dialog_width = int(screen_width * 0.8)
        dialog_height = int(screen_height * 0.8)
        self.resize(dialog_width, dialog_height)

        self.settings_map = {}  # 변경된 설정 추적
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 레이블
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("background-color: #1428A0; border: none;")
        title_frame.setFixedHeight(60)

        # 프레임 레이아웃 생성
        title_frame_layout = QVBoxLayout(title_frame)
        title_frame_layout.setContentsMargins(20, 0, 10, 0)
        title_frame_layout.setAlignment(Qt.AlignLeft)

        # 제목 레이블 생성
        title_label = QLabel("Settings")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")  # 텍스트 색상 설정

        # 레이아웃에 레이블 추가
        title_frame_layout.addWidget(title_label)

        # 메인 레이아웃에 프레임 추가
        main_layout.addWidget(title_frame)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """      
                QTabBar::tab::first { margin-left: 10px;}
                QTabBar {
                    background-color: transparent;
                    border: none;
                    font-family : Arial;

                }
                QTabBar::tab {
                    background: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    padding: 6px 10px;
                    margin-right: 2px;
                    margin-bottom: 0px;
                }
                QTabBar::tab:selected, QTabBar::tab:hover {
                    background: #1428A0;
                    color: white;
                    font-family : Arial;
                }
            """
        )

        # 탭 컴포넌트 생성
        self.basic_tab = BasicTabComponent()
        self.pre_option_tab = PreOptionTabComponent()
        self.detail_tab = DetailTabComponent()

        # 설정 변경 이벤트 연결
        self.basic_tab.settings_changed.connect(self.on_setting_changed)
        self.pre_option_tab.settings_changed.connect(self.on_setting_changed)
        self.detail_tab.settings_changed.connect(self.on_setting_changed)

        # 탭 추가
        self.tab_widget.addTab(self.basic_tab, "Basic")
        self.tab_widget.addTab(self.pre_option_tab, "Pre-Option")
        self.tab_widget.addTab(self.detail_tab, "Detail")

        # 버튼 레이아웃
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #F0F0F0; border: none;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 30, 10)

        # 저장 및 닫기 버튼
        save_button = QPushButton("Save")
        save_button_font = QFont("Arial", 10)
        save_button_font.setBold(True)
        save_button.setFont(save_button_font)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                border: none;
                color: white;
                border-radius: 10px;
                width: 130px;
                height: 50px;
            }
            QPushButton:hover {
                background-color: #1e429f;
                border: none;
                color: white;
            }
        """)
        save_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_button.clicked.connect(self.save_settings)

        # 취소 버튼
        cancel_button = QPushButton("Cancel")
        cancel_button_font = QFont("Arial", 10)
        cancel_button_font.setBold(True)
        cancel_button.setFont(cancel_button_font)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #DDDDDD;
                border: none;
                color: #333333;
                border-radius: 10px;
                width: 130px;
                height: 50px;
            }
            QPushButton:hover {
                background-color: #CCCCCC;
                border: none;
                color: #333333;
            }
        """)
        cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)  # 다이얼로그 취소

        button_layout.addStretch(1)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(button_frame)

        # 설정 로드
        self.load_settings()

    def load_settings(self):
        """저장된 설정 로드"""
        # 설정 파일에서 설정 로드
        SettingsStore.load_settings()

        # 모든 설정 값을 복사
        self.settings_map = SettingsStore.get_all()

    def on_setting_changed(self, key, value):
        """설정 변경 시 호출되는 콜백"""
        # 변경된 설정 추적
        self.settings_map[key] = value

    def save_settings(self):
        """설정 저장 및 다이얼로그 종료"""
        # 설정 저장소에 일괄 업데이트
        SettingsStore.update(self.settings_map)

        # 설정 변경 시그널 발생
        self.settings_changed.emit(self.settings_map)

        # 다이얼로그 종료
        self.accept()