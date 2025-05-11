from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QScrollArea, QWidget, QTabWidget
)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt


class DetailDialog(QDialog):
    def __init__(self, row: dict, time_map: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Detail")
        # 도움말 아이콘(물음표) 제거 - 윈도우 플래그 설정
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)

        # 다이얼로그 크기 설정
        self.resize(1000, 600)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 제목 프레임
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("background-color: #1428A0; border: none;")
        title_frame.setFixedHeight(60)

        # 제목 프레임 레이아웃
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 0, 20, 0)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 제목 레이블
        title_label = QLabel("Project Detail")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)

        # 메인 레이아웃에 제목 프레임 추가
        main_layout.addWidget(title_frame)

        # 콘텐츠 영역
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #F9F9F9; border: none;")
        scroll_area.setWidget(content_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 데이터 표시 프레임
        data_frame = QFrame()
        data_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """)
        data_layout = QVBoxLayout(data_frame)
        data_layout.setContentsMargins(20, 20, 20, 20)
        data_layout.setSpacing(15)

        # 그리드 레이아웃 생성 - 열 너비 조정
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(12)

        # 열 너비 설정: 0열(라벨명), 1열(값), 2열(라벨명), 3열(값)
        grid.setColumnMinimumWidth(0, 100)  # 첫 번째 라벨열 최소 너비
        grid.setColumnMinimumWidth(1, 300)  # 첫 번째 값열 최소 너비
        grid.setColumnMinimumWidth(2, 100)  # 두 번째 라벨열 최소 너비
        grid.setColumnMinimumWidth(3, 300)  # 두 번째 값열 최소 너비

        # 각 열의 늘어나는 비율 설정
        grid.setColumnStretch(0, 0)  # 첫 번째 라벨열은 늘어나지 않음
        grid.setColumnStretch(1, 2)  # 첫 번째 값열은 약간 늘어남
        grid.setColumnStretch(2, 0)  # 두 번째 라벨열은 늘어나지 않음
        grid.setColumnStretch(3, 2)  # 두 번째 값열은 약간 늘어남

        # 안전하게 값을 가져오는 함수
        def safe_get(key, default="-"):
            value = row.get(key, default)
            # None, NaN 등을 확인하여 기본값으로 대체
            if value is None or (hasattr(value, 'isna') and value.isna()) or value == "?" or str(
                    value).lower() == "nan":
                return default
            return str(value)

        fields = [
            ("Line", safe_get("line")),
            ("Time", safe_get("time")),
            ("Project", safe_get("project")),
            ("Qty", safe_get("qty")),
        ]

        # 필드 스타일 정의
        field_name_style = """
            font-family: Arial;
            font-size: 10pt;
            font-weight: bold;
            color: #555555;
            border: none;
        """

        field_value_style = """
            font-family: Arial;
            font-size: 10pt;
            color: #333333;
            background-color: #f5f5f5;
            padding: 5px 10px;
            border-radius: 4px;
            min-width: 280px;
            max-width: 280px;
        """

        # 그리드에 필드 추가
        for i, (name, val) in enumerate(fields):
            lbl_name = QLabel(f"{name}:")
            lbl_name.setStyleSheet(field_name_style)
            lbl_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            lbl_val = QLabel(str(val))
            lbl_val.setStyleSheet(field_value_style)
            lbl_val.setFixedWidth(280)  # 고정 너비 설정
            lbl_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # 값이 너무 길면 자동으로 줄바꿈
            lbl_val.setWordWrap(True)

            # 2열 그리드로 배치 (홀수/짝수 열 구분)
            row_idx = i // 2
            col_idx = (i % 2) * 2  # 0, 2, 0, 2, ...

            grid.addWidget(lbl_name, row_idx, col_idx, Qt.AlignRight)
            grid.addWidget(lbl_val, row_idx, col_idx + 1, Qt.AlignLeft)

        data_layout.addLayout(grid)

        details_list = row.get('details', [])
        if details_list:
            tab_widget = QTabWidget()
            tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            keys = ["Demand","Item","Qty","To_site","SOP","MFG","RMC","Due_LT"]
            for rec in details_list:
                tab = QWidget()
                tab_layout = QGridLayout(tab)
                tab_layout.setContentsMargins(30, 10, 30, 10)
                tab_layout.setHorizontalSpacing(12)
                tab_layout.setVerticalSpacing(6)

                for i, key in enumerate(keys):
                    value = rec.get(key, "-")
                    name_lbl = QLabel(f"{key}:")
                    name_lbl.setFont(QFont("Arial", 9, QFont.Bold))
                    name_lbl.setStyleSheet("border: none;")
                    name_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    val_lbl = QLabel(str(value))
                    val_lbl.setStyleSheet("border: none;")
                    val_lbl.setFont(QFont("Arial", 9))

                    row_idx = i // 2
                    col_idx = (i % 2) * 2
                    tab_layout.addWidget(name_lbl, row_idx, col_idx, Qt.AlignLeft)
                    tab_layout.addWidget(val_lbl, row_idx, col_idx + 1, Qt.AlignLeft)

                # 탭 라벨
                demand_label = str(rec.get("Demand", "-"))
                tab_widget.addTab(tab, demand_label)

            data_layout.addWidget(tab_widget)

        content_layout.addWidget(data_frame)
        content_layout.addStretch(1)
        # 버튼 프레임
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #F0F0F0; border: none;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 30, 10)

        # 닫기 버튼
        close_button = QPushButton("Close")
        close_button_font = QFont("Arial", 10)
        close_button_font.setBold(True)
        close_button.setFont(close_button_font)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                border: none;
                color: white;
                border-radius: 10px;
                width: 130px;
                height: 40px;
            }
            QPushButton:hover {
                background-color: #1e429f;
                border: none;
                color: white;
            }
        """)
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.setFixedSize(130, 60)
        close_button.clicked.connect(self.accept)

        button_layout.addStretch(1)
        button_layout.addWidget(close_button)

        # 메인 레이아웃에 스크롤 영역과 버튼 프레임 추가
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(button_frame)