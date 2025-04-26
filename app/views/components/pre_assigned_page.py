from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor


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

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)  # 버튼 사이 간격 확대
        button_layout.addStretch()

        # Export 버튼 설정
        export_button = QPushButton("Export")
        export_font = QFont()
        export_font.setFamily("Arial")
        export_font.setPointSize(9)
        export_font.setBold(True)
        export_button.setFont(export_font)

        export_button.setCursor(QCursor(Qt.PointingHandCursor))
        export_button.setFixedSize(150, 50)  # 버튼 크기 설정

        export_button.setStyleSheet("""
                QPushButton {
                background-color: #1428A0; 
                color: white;
                padding: 8px 10px; 
                border-radius: 5px; 
                }
                QPushButton:hover {
                        background-color: #004C99;
                    }
                    QPushButton:pressed {
                        background-color: #003366;
                    }
                """)

        # Run 버튼 설정
        run_button = QPushButton("Run")
        run_button.setCursor(QCursor(Qt.PointingHandCursor))
        run_button.setFixedSize(150, 50)
        run_font = QFont()
        run_font.setFamily("Arial")
        run_font.setPointSize(9)
        run_font.setBold(True)
        run_button.setFont(run_font)

        run_button.setStyleSheet("""
                QPushButton {
                background-color: #1428A0; 
                color: white; 
                padding: 8px 10px; 
                border-radius: 5px; 
                }
                QPushButton:hover {
                        background-color: #004C99;
                    }
                    QPushButton:pressed {
                        background-color: #003366;
                    }
                """)

        # Reset 버튼 설정
        reset_button = QPushButton("Reset")
        reset_button.setCursor(QCursor(Qt.PointingHandCursor))
        reset_button.setFixedSize(150, 50)
        reset_font = QFont()
        reset_font.setFamily("Arial")
        reset_font.setPointSize(9)
        reset_font.setBold(True)
        reset_button.setFont(reset_font)


        reset_button.setStyleSheet("""
                QPushButton {
                background-color: #ACACAC; 
                color: white; 
                padding: 8px 10px; 
                border-radius: 5px; 
                }
                QPushButton:hover {
                        background-color: #C0C0C0;
                    }
                    QPushButton:pressed {
                        background-color: #848282;
                    }
                """)

        # 버튼 연결
        export_button.clicked.connect(self.on_export_click)
        run_button.clicked.connect(self.on_optimization_click)
        reset_button.clicked.connect(self.on_reset_click)

        button_layout.addWidget(export_button)
        button_layout.addWidget(run_button)
        button_layout.addWidget(reset_button)
        title_layout.addLayout(button_layout)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_frame.setFrameShadow(QFrame.Raised)
        content_frame.setMinimumSize(200,200)
        content_frame.setStyleSheet("""
        QFrame { background-color: white;
         border: 2px solid grey;}
        """)
        content_layout.addWidget(content_frame,1)

        main_layout.addLayout(content_layout,1)
        # 스페이서 추가
        main_layout.addStretch()

    def on_optimization_click(self):
        # 최적화 실행 시 시그널 발생 (필요한 매개변수 전달)
        parameters = {}  # 필요한 매개변수 딕셔너리
        self.optimization_requested.emit(parameters)
        # 또는 직접 메인 윈도우 메서드 호출
        self.main_window.run_optimization()

    def on_export_click(self):
        # Export 버튼 클릭 시 수행할 작업
        pass

    def on_reset_click(self):
        # Reset 버튼 클릭 시 수행할 작업
        pass