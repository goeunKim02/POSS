from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal


class AnalysisPage(QWidget):
    # 시그널 추가
    export_requested = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # 제목
        title = QLabel("결과 분석 페이지")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # 내용 추가
        # 결과 내보내기 버튼 추가
        export_btn = QPushButton("결과 내보내기")
        export_btn.clicked.connect(self.on_export_click)
        layout.addWidget(export_btn)

        # 스페이서 추가
        layout.addStretch()

        # 하단 네비게이션 버튼
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("<< 이전")
        back_btn.clicked.connect(lambda: self.main_window.navigate_to_page(1))

        finish_btn = QPushButton("완료")
        finish_btn.clicked.connect(self.on_finish)

        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(finish_btn)
        layout.addLayout(btn_layout)

    def on_export_click(self):
        # 결과 내보내기 로직
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "결과 내보내기",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            self.export_requested.emit(file_path)
            # 또는 직접 메인 윈도우 메서드 호출
            self.main_window.export_results(file_path)

    def on_finish(self):
        # 완료 시 동작 정의
        # 예: 결과 저장, 애플리케이션 종료 등
        pass