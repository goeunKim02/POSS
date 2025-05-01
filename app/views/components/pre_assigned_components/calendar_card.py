from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal

from .style import CARD_DAY_FRAME_STYLE, CARD_NIGHT_FRAME_STYLE

class CalendarCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, row_data: dict, is_day: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._row = row_data

        if is_day:
            self.setObjectName("cardFrameDay")
            self.setStyleSheet(CARD_DAY_FRAME_STYLE)
        else:
            self.setObjectName("cardFrameNight")
            self.setStyleSheet(CARD_NIGHT_FRAME_STYLE)

        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # 클릭 이벤트
        self.setMouseTracking(True)

        # 내부 레이아웃
        hl = QHBoxLayout(self)
        hl.setContentsMargins(8, 8, 8, 8)
        hl.setSpacing(4)

        lbl_item = QLabel(self._row.get('project', ''), self)
        lbl_item.setFont(QFont("Arial", 10, QFont.Bold))
        lbl_item.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        lbl_qty = QLabel(str(self._row.get('qty', '')), self)
        lbl_qty.setFont(QFont("Arial", 9))
        lbl_qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        hl.addWidget(lbl_item)
        hl.addWidget(lbl_qty)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self._row)
        super().mousePressEvent(e)