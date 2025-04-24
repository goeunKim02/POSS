from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal


class PlanningPage(QWidget):
    # 시그널 추가
    optimization_requested = pyqtSignal(dict)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        # 레이아웃 설정
        main_layout = QVBoxLayout(self)
        title_layout = QHBoxLayout()
        title_label = QLabel("Pre-Assigned Result")
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)


        # 스페이서 추가
        main_layout.addStretch()


    def on_optimization_click(self):
        # 최적화 실행 시 시그널 발생 (필요한 매개변수 전달)
        parameters = {}  # 필요한 매개변수 딕셔너리
        self.optimization_requested.emit(parameters)
        # 또는 직접 메인 윈도우 메서드 호출
        self.main_window.run_optimization()