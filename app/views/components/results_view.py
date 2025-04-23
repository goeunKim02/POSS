from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class ResultPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃 설정
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 제목 레이블
        title_label = QLabel("Test Page")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 설명 텍스트
        desc_label = QLabel("이 페이지는 테스트 및 개발 목적으로 사용됩니다.")
        desc_label.setStyleSheet("font-size: 14px; margin: 10px 0;")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)

        # 버튼 영역
        button_layout = QHBoxLayout()

        # 테스트 버튼 1
        test_button1 = QPushButton("테스트 버튼 1")
        test_button1.setStyleSheet("""
            QPushButton {
                background-color: #1a56db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e429f;
            }
        """)
        test_button1.clicked.connect(self.on_test_button1_clicked)
        button_layout.addWidget(test_button1)

        # 테스트 버튼 2
        test_button2 = QPushButton("테스트 버튼 2")
        test_button2.setStyleSheet("""
            QPushButton {
                background-color: #e02424;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        test_button2.clicked.connect(self.on_test_button2_clicked)
        button_layout.addWidget(test_button2)

        main_layout.addLayout(button_layout)

        # 결과 출력 영역
        self.result_label = QLabel("테스트 결과가 여기에 표시됩니다")
        self.result_label.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            min-height: 50px;
        """)
        self.result_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.result_label)

        # 레이아웃에 여백 추가
        main_layout.addStretch()

    def on_test_button1_clicked(self):
        self.result_label.setText("테스트 버튼 1이 클릭되었습니다!")
        print("테스트 버튼 1 클릭")

    def on_test_button2_clicked(self):
        self.result_label.setText("테스트 버튼 2가 클릭되었습니다!")
        print("테스트 버튼 2 클릭")