from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal

from ....resources.styles.pre_assigned_style import CARD_DAY_FRAME_STYLE, CARD_NIGHT_FRAME_STYLE, CARD_DAY_SELECTED_STYLE, CARD_NIGHT_SELECTED_STYLE

class CalendarCard(QFrame):
    clicked = pyqtSignal(object, dict)

    def __init__(self, row_data: dict, is_day: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._row = row_data

        self.base_style = CARD_DAY_FRAME_STYLE if is_day else CARD_NIGHT_FRAME_STYLE
        self.selected_style = CARD_DAY_SELECTED_STYLE if is_day else CARD_NIGHT_SELECTED_STYLE

        self.setStyleSheet(self.base_style)
        self._is_selected = False

        self.setObjectName("cardFrameDay" if is_day else "cardFrameNight")
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
            self._is_selected = not self._is_selected
            self.setStyleSheet(self.selected_style if self._is_selected else self.base_style)
            self.clicked.emit(self, self._row)
        super().mousePressEvent(e)