from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QFont
from app.resources.fonts.font_manager import font_manager
from app.models.common.screen_manager import *


class Navbar(QFrame):
    # 시그널 정의
    help_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1428A0;
                min-height: {h(45)}px;
                max-height: {h(45)}px;
            }}
            QLabel {{
                color: white;
            }}
            QPushButton {{
                color: white;
                border: {s(2)}px solid white;
                padding: {p(4)}px {p(8)}px;
                background-color: transparent;
                border-radius: {s(5)}px;
                min-width: {w(50)}px;
                min-height: {h(15)}px;
            }}
            QPushButton:hover {{
                background-color: #1e429f;
            }}
        """)

        navbar_layout = QHBoxLayout(self)
        navbar_layout.setContentsMargins(m(20), 0, m(20), 0)
        navbar_layout.setSpacing(sp(10))  # 버튼 간격도 조정

        logo_label = QLabel("SAMSUNG Production Planning Optimization")
        logo_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # font_manager 사용
        logo_font = font_manager.get_font("SamsungOne-700", fs(13))
        logo_font.setBold(True)
        logo_font.setWeight(99)
        logo_label.setFont(logo_font)

        navbar_layout.addWidget(logo_label)
        navbar_layout.addStretch()

        settings_btn = QPushButton("Settings")
        settings_btn.setCursor(QCursor(Qt.PointingHandCursor))

        # font_manager 사용
        btn_font = font_manager.get_font("SamsungOne-700", fs(10), QFont.Bold)
        settings_btn.setFont(btn_font)

        help_btn = QPushButton("Help")
        help_btn.setCursor(QCursor(Qt.PointingHandCursor))
        help_btn.setFont(btn_font)  # 같은 폰트 사용

        # 시그널 연결
        help_btn.clicked.connect(self.help_clicked.emit)
        settings_btn.clicked.connect(self.settings_clicked.emit)

        navbar_layout.addWidget(settings_btn)
        navbar_layout.addWidget(help_btn)