from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtGui import QCursor, QFont


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
                min-height: 60px;
                max-height: 60px;
            }
            QLabel {
                color: white;
                font-size: 30px;
                font-weight: bold;
            }
            QPushButton {
                color: white;
                border: 1px solid white;
                padding: 8px 16px;
                background-color: transparent;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e429f;
            }
        """)

        navbar_layout = QHBoxLayout(self)
        navbar_layout.setContentsMargins(20, 0, 20, 0)

        logo_label = QLabel("SAMSUNG Production Planning Optimization")
        logo_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        logo_font = QFont()
        logo_font.setFamily("Arial")
        logo_font.setPointSize(15)
        logo_font.setBold(True)
        logo_font.setWeight(99)
        logo_label.setFont(logo_font)


        navbar_layout.addWidget(logo_label)
        navbar_layout.addStretch()

        settings_btn = QPushButton("Settings")
        settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        help_btn = QPushButton("Help")
        help_btn.setCursor(QCursor(Qt.PointingHandCursor))

        # 시그널 연결
        help_btn.clicked.connect(self.help_clicked.emit)
        settings_btn.clicked.connect(self.settings_clicked.emit)

        navbar_layout.addWidget(settings_btn)
        navbar_layout.addWidget(help_btn)