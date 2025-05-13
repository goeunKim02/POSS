from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QFont
from app.resources.fonts.font_manager import font_manager  # 폰트 매니저 임포트


class Navbar(QFrame):
    # 시그널 정의
    help_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #1428A0;
                min-height: 65px;
                max-height: 65px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                color: white;
                border: 3px solid white;
                padding: 4px 8px;
                background-color: transparent;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1e429f;
            }
        """)

        navbar_layout = QHBoxLayout(self)
        navbar_layout.setContentsMargins(20, 0, 20, 0)

        logo_label = QLabel("SAMSUNG Production Planning Optimization")
        logo_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # font_manager 사용
        logo_font = font_manager.get_font("SamsungOne-700", 13)
        logo_label.setFont(logo_font)

        navbar_layout.addWidget(logo_label)
        navbar_layout.addStretch()

        settings_btn = QPushButton("Settings")
        settings_btn.setCursor(QCursor(Qt.PointingHandCursor))

        # font_manager 사용
        btn_font = font_manager.get_font("SamsungOne-700", 9, QFont.Bold)
        settings_btn.setFont(btn_font)

        help_btn = QPushButton("Help")
        help_btn.setCursor(QCursor(Qt.PointingHandCursor))
        help_btn.setFont(btn_font)  # 같은 폰트 사용

        # 시그널 연결
        help_btn.clicked.connect(self.help_clicked.emit)
        settings_btn.clicked.connect(self.settings_clicked.emit)

        navbar_layout.addWidget(settings_btn)
        navbar_layout.addWidget(help_btn)