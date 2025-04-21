from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal


class PlanningPage(QWidget):
    # 시그널 추가
    optimization_requested = pyqtSignal(dict)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # 제목
        title = QLabel("생산계획 실행 페이지")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # 생산계획 최적화 실행 버튼 추가
        plan_btn = QPushButton("생산계획 최적화 실행")
        plan_btn.clicked.connect(self.on_optimization_click)
        layout.addWidget(plan_btn)

        # 스페이서 추가
        layout.addStretch()

        # 하단 네비게이션 버튼
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("<< 이전")
        back_btn.clicked.connect(lambda: self.main_window.navigate_to_page(0))

        next_btn = QPushButton("다음 >>")
        next_btn.clicked.connect(lambda: self.main_window.navigate_to_page(2))

        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(next_btn)
        layout.addLayout(btn_layout)

    def on_optimization_click(self):
        # 최적화 실행 시 시그널 발생 (필요한 매개변수 전달)
        parameters = {}  # 필요한 매개변수 딕셔너리
        self.optimization_requested.emit(parameters)
        # 또는 직접 메인 윈도우 메서드 호출
        self.main_window.run_optimization()