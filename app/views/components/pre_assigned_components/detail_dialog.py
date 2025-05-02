from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ....resources.styles.pre_assigned_style import (
    DETAIL_DIALOG_STYLE,
    DETAIL_LABEL_TRANSPARENT,
    DETAIL_FRAME_TRANSPARENT,
    DETAIL_FIELD_NAME_STYLE,
    DETAIL_FIELD_VALUE_STYLE,
    DETAIL_BUTTON_STYLE
)

class DetailDialog(QDialog):
    def __init__(self, row: dict, time_map: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("카드 상세 정보")
        self.setModal(True)
        self.setStyleSheet(
            DETAIL_DIALOG_STYLE
          + DETAIL_LABEL_TRANSPARENT
          + DETAIL_FRAME_TRANSPARENT
          + DETAIL_FIELD_NAME_STYLE
          + DETAIL_FIELD_VALUE_STYLE
          + DETAIL_BUTTON_STYLE
        )

        # 바깥 레이아웃
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(16, 16, 16, 16)
        main_lay.setSpacing(12)

        # 제목
        title = QLabel("상세 정보")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_lay.addWidget(title)

        # 구분선
        sep = QFrame(self)
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        main_lay.addWidget(sep)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)

        fields = [
            ("Line",       row.get("line", "-")),
            ("Time",       row.get("time", "-")),
            ("Project",    row.get("project", "-")),
            ("Item",       row.get("item", "-")),
            ("Qty",        row.get("qty", "-")),
            ("Demand",     row.get("demand", "-")),
            ("To Site",    row.get("to_site", "-")),
            ("SOP",        row.get("sop", "-")),
            ("MFG",        row.get("mfg", "-")),
            ("RMC",        row.get("rmc", "-")),
            ("Due LT",     row.get("due_LT", "-")),
        ]

        for i, (name, val) in enumerate(fields):
            lbl_name = QLabel(f"{name}:")
            lbl_name.setObjectName("field-name")
            lbl_name.setProperty("class", "field-name")
            lbl_val  = QLabel(str(val))
            lbl_val.setObjectName("field-value")
            lbl_val.setProperty("class", "field-value")
            lbl_name.setFont(QFont("Arial", 10))
            lbl_val.setFont(QFont("Arial", 10))
            grid.addWidget(lbl_name, i, 0, Qt.AlignRight)
            grid.addWidget(lbl_val,  i, 1, Qt.AlignLeft)

        main_lay.addLayout(grid)

        # 버튼
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        btn_close = QPushButton("닫기", self)
        btn_close.setFixedWidth(80)
        btn_close.clicked.connect(self.accept)
        btn_lay.addWidget(btn_close)
        main_lay.addLayout(btn_lay)