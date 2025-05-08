from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy,QVBoxLayout, QDialog, QWidget
from PyQt5.QtCore import Qt, pyqtSignal

from app.views.components.pre_assigned_components.calendar_card import CalendarCard

from ....resources.styles.pre_assigned_style import CARD_DAY_FRAME_STYLE, CARD_NIGHT_FRAME_STYLE

class CalendarBox(QFrame):
    clicked = pyqtSignal(list)  # 카드 데이터 리스트 전달

    def __init__(self, qty_sum: int, records: list, is_day: bool = True, parent=None):
        super().__init__(parent)

        if is_day:
            self.setObjectName("cardFrameDay")
            self.setStyleSheet(CARD_DAY_FRAME_STYLE)
        else:
            self.setObjectName("cardFrameNight")
            self.setStyleSheet(CARD_NIGHT_FRAME_STYLE)

        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.records = records
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        label = QLabel(f"QTY: {qty_sum}")
        label.setFont(QFont("Arial", 10, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.records)
        super().mouseReleaseEvent(event)