from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame


class ErrorStatusComponent(QWidget):
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
        title_label = QLabel("Error Status")
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)

        # 제목 레이블을 레이아웃에 추가
        title_layout.addWidget(title_label)

        # 에러 메시지를 표시할 레이블 생성
        self.message_label = QLabel("You don't have a problem now")
        message_font = QFont()
        message_font.setFamily("Arial")
        message_font.setPointSize(14)
        message_font.setBold(True)
        message_font.setWeight(99)
        self.message_label.setFont(message_font)


        self.message_label.setStyleSheet("color: blue; font-size: 14px; border: none; padding: 10px")

        # 레이아웃을 메인 레이아웃에 추가 (addWidget이 아닌 addLayout 사용)
        main_layout.addWidget(title_frame)
        main_layout.addWidget(self.message_label)

    def set_message(self, message, status_type="info"):
        """상태 메시지 설정

        Args:
            message (str): 표시할 메시지
            status_type (str): 메시지 유형 ('success', 'error', 'info' 중 하나)
        """
        self.message_label.setText(message)

        if status_type == "success":
            self.message_label.setStyleSheet("color: green; font-size: 14px;")
        elif status_type == "error":
            self.message_label.setStyleSheet("color: red; font-size: 14px;")
        else:  # info
            self.message_label.setStyleSheet("color: blue; font-size: 14px;")