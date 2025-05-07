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
        # 도움말 아이콘(물음표) 제거 - 윈도우 플래그 설정
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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

        # 안전하게 값을 가져오는 함수
        def safe_get(key, default="-"):
            value = row.get(key, default)
            # None, NaN 등을 확인하여 기본값으로 대체
            if value is None or (hasattr(value, 'isna') and value.isna()) or value == "?" or str(value).lower() == "nan":
                return default
            return str(value)

        fields = [
            ("Line",       safe_get("line")),
            ("Time",       safe_get("time")),
            ("Project",    safe_get("project")),
            ("Item",       safe_get("item")),
            ("Qty",        safe_get("qty")),
            ("Demand",     safe_get("demand")),
            ("To Site",    safe_get("to_site")),
            ("SOP",        safe_get("sop")),
            ("MFG",        safe_get("mfg")),
            ("RMC",        safe_get("rmc")),
            ("Due LT",     safe_get("due_LT")),
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