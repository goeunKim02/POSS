# app/views/components/settings_dialogs/settings_dialog.py - 모던한 디자인으로 개선된 설정 다이얼로그
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTabWidget, QFrame, QApplication, QMessageBox, QWidget)
from PyQt5.QtGui import QFont, QCursor, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from app.resources.fonts.font_manager import font_manager

# 분리된 탭 컴포넌트 import
from app.views.components.settings_dialogs.settings_components import (
    BasicTabComponent,
    PreOptionTabComponent,
    DetailTabComponent
)

from app.models.common.settings_store import SettingsStore


class SettingsDialog(QDialog):
    """모던하게 디자인된 설정 다이얼로그 창"""

    # 설정 변경 시그널 정의
    settings_changed = pyqtSignal(dict)  # 변경된 설정 값 딕셔너리

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Samsung Production Planning Optimization Settings")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # 모던한 스타일 설정
        self.setStyle()

        screen = self.screen()
        screen_size = screen.availableGeometry()
        self.resize(int(screen_size.width() * 0.5), int(screen_size.height() * 0.8))

        self.settings_map = {}  # 변경된 설정 추적
        self.init_ui()

        # 초기 설정 상태 저장
        self.original_settings = self.settings_map.copy()

    def setStyle(self):
        """전체적인 모던 스타일 설정"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
        """)

        # 창 그림자 효과 추가
        if hasattr(self, 'setGraphicsEffect'):
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(60)
            shadow.setXOffset(0)
            shadow.setYOffset(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            self.setGraphicsEffect(shadow)

    def init_ui(self):
        screen = self.screen()
        screen_size = screen.availableGeometry()

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 탭 위젯 생성 (모던 스타일)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""      
            QTabWidget::pane {{
                background-color: #ffffff;
                border: none;
                border-top: 1px solid #e9ecef;
            }}

            QTabBar {{
                background-color: #f8f9fa;
                border: none;
            }}

            QTabBar::tab {{
                background: transparent;
                color: #666;
                padding: 16px 24px;
                font-family: {font_manager.get_just_font("SamsungOne-700").family()};
                font-size: 14px;
                font-weight: 600;
                border-bottom: 3px solid transparent;
                margin-right: 0px;
            }}

            QTabBar::tab:hover {{
                color: #1428A0;
                background: rgba(20, 40, 160, 0.05);
            }}

            QTabBar::tab:selected {{
                color: #1428A0;
                font-weight: 700;
                border-bottom: 3px solid #1428A0;
                background: rgba(20, 40, 160, 0.05);
            }}

            QTabBar::tab:first {{
                margin-left: 24px;
            }}
        """)

        # 탭 컴포넌트 생성 (모던 스타일 적용)
        self.basic_tab = BasicTabComponent()
        self.pre_option_tab = PreOptionTabComponent()
        self.detail_tab = DetailTabComponent()

        # 모던 스타일 적용
        for tab in [self.basic_tab, self.pre_option_tab, self.detail_tab]:
            self.apply_modern_style_to_tab(tab)

        # 설정 변경 이벤트 연결
        self.basic_tab.settings_changed.connect(self.on_setting_changed)
        self.pre_option_tab.settings_changed.connect(self.on_setting_changed)
        self.detail_tab.settings_changed.connect(self.on_setting_changed)

        # 탭 추가
        self.tab_widget.addTab(self.basic_tab, "Basic")
        self.tab_widget.addTab(self.pre_option_tab, "Pre-Option")
        self.tab_widget.addTab(self.detail_tab, "Detail")

        # 버튼 영역 (모던 스타일)
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: none;
                border-top: 1px solid #e9ecef;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 20, 40, 20)

        # 저장 버튼 (모던 스타일)
        save_button = QPushButton("Save")
        save_button.setFont(QFont("Arial", 10, QFont.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                border: none;
                color: white;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 15px;
                font-weight: 700;
                min-width: 130px;
            }
            QPushButton:hover {
                background-color: #1a35cc;
            }
            QPushButton:pressed {
                background-color: #1e429f;
            }
        """)
        save_button.setCursor(QCursor(Qt.PointingHandCursor))
        save_button.clicked.connect(self.save_settings)

        # 취소 버튼 (모던 스타일)
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Arial", 10, QFont.Bold))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dddddd;
                border: none;
                color: #333333;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 15px;
                font-weight: 700;
                min-width: 130px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
            QPushButton:pressed {
                background-color: #bbbbbb;
            }
        """)
        cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch(1)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(button_frame)

        # 설정 로드
        self.load_settings()

    def apply_modern_style_to_tab(self, tab):
        """탭에 모던 스타일 적용"""
        tab.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
                border: none;
            }

            QScrollBar:vertical {
                background: #f8f9fa;
                border: none;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #dee2e6;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #ced4da;
            }
        """)

    def load_settings(self):
        """저장된 설정 로드"""
        SettingsStore.load_settings()
        self.settings_map = SettingsStore.get_all()

    def on_setting_changed(self, key, value):
        """설정 변경 시 호출되는 콜백"""
        self.settings_map[key] = value

    def save_settings(self):
        """설정 저장 및 다이얼로그 종료"""
        try:
            # 설정 저장소에 일괄 업데이트
            SettingsStore.update(self.settings_map)

            # 파일에 저장
            SettingsStore.save_settings()

            # 설정 변경 시그널 발생
            self.settings_changed.emit(self.settings_map)

            # 모던한 성공 메시지
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText("Settings have been saved successfully.")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #333;
                    font-size: 14px;
                }
                QMessageBox QPushButton {
                    background-color: #1428A0;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #1a35cc;
                }
            """)
            msg.exec_()

            # 다이얼로그 종료
            self.accept()

        except Exception as e:
            # 에러 메시지 표시
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"An error occurred while saving the settings:\n{str(e)}")
            msg.setIcon(QMessageBox.Critical)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #333;
                    font-size: 14px;
                }
                QMessageBox QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            msg.exec_()