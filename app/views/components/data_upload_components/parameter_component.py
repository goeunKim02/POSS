from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame



class ParameterComponent(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 레이아웃 생성
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("""
            background-color: #F5F5F5;
            border: none;
        """)
        title_frame.setFixedHeight(40)

        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 0, 0, 0)

        # 제목 레이블 생성
        title_label = QLabel("Parameter Setting")
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)

        # 제목 레이블을 레이아웃에 추가
        title_layout.addWidget(title_label)

        # 레이아웃을 메인 레이아웃에 추가 (addWidget이 아닌 addLayout 사용)
        main_layout.addWidget(title_frame)
        main_layout.addStretch(1)





