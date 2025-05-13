# splash_start.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient


class SamsungSplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Samsung Production Planning System")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        screen = self.screen()
        screen_size = screen.availableGeometry()
        self.resize(int(screen_size.width()*0.5), int(screen_size.height()*0.4))

        # 창을 화면 중앙에 배치
        self.center()

        # 배경 설정
        self.backgroundColor = QColor(255, 255, 255)  # 흰색 배경
        self.accentColor = QColor(20, 40, 160)  # 삼성 파란색

        # 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # 로고 텍스트
        logo_label = QLabel("SAMSUNG")
        logo_label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 25, QFont.Bold)
        logo_label.setFont(font)
        logo_label.setStyleSheet(
            f"color: rgb({self.accentColor.red()}, {self.accentColor.green()}, {self.accentColor.blue()});")

        # 부제목
        subtitle_label = QLabel("Production Planning Optimization System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #555555;")

        # 로딩 상태 메시지
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont("Arial", 10)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #888888;")

        # 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #F0F0F0;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: rgb({self.accentColor.red()}, {self.accentColor.green()}, {self.accentColor.blue()});
                border-radius: 3px;
            }}
        """)

        # 버전 정보
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        version_font = QFont("Arial", 8)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #AAAAAA;")

        # 레이아웃에 위젯 추가
        layout.addStretch(1)
        layout.addWidget(logo_label)
        layout.addWidget(subtitle_label)
        layout.addStretch(1)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch(1)
        layout.addWidget(version_label)

        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # 30ms마다 업데이트

        self.progress_value = 0
        self.loading_stages = [
            "Initializing application...",
            "Loading resources...",
            "Preparing UI components...",
            "Starting main application..."
        ]
        self.current_stage = 0

        # MainWindow 참조 저장
        self.main_window = None

    def center(self):
        """창을 화면 중앙에 배치"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

    def update_progress(self):
        """프로그레스 바 업데이트 및 메인 앱 시작"""
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)

        # 진행 단계 업데이트
        stage_progress = 100 / len(self.loading_stages)
        if self.progress_value % int(stage_progress) == 0 and self.current_stage < len(self.loading_stages):
            self.status_label.setText(self.loading_stages[self.current_stage])
            self.current_stage += 1

        # 로딩 완료 시 메인 앱 실행 및 스플래시 숨기기
        if self.progress_value >= 90:
            self.timer.stop()

            # 스플래시 화면 숨기기
            self.hide()

            try:
                # 직접 MainWindow 클래스 가져오기
                print("app.views.main_window에서 MainWindow 로드 시도...")
                from app.views.main_window import MainWindow

                # MainWindow 인스턴스 생성 및 표시
                self.main_window = MainWindow()
                self.main_window.show()

                # 스플래시 창만 닫기 (애플리케이션은 계속 실행)
                self.close()
                print("MainWindow 성공적으로 로드되어 표시됨")

            except Exception as e:
                print(f"메인 애플리케이션 실행 오류: {e}")
                import traceback
                traceback.print_exc()

                # 사용자에게 오류 메시지 표시
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setText("애플리케이션 시작 실패")
                error_box.setInformativeText(f"오류 발생: {str(e)}")
                error_box.setDetailedText(traceback.format_exc())
                error_box.setWindowTitle("시작 오류")
                error_box.exec_()

                # 오류 발생시 애플리케이션 종료
                self.close()
                QApplication.instance().quit()

    def paintEvent(self, event):
        """배경 그라데이션 및 테두리 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 배경 그리기
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255))  # 위쪽 흰색
        gradient.setColorAt(1, QColor(245, 245, 250))  # 아래쪽 연한 파란색

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)

        # 테두리 그리기
        painter.setPen(QPen(QColor(230, 230, 240), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 15, 15)


# 직접 실행할 경우 (테스트용)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SamsungSplashScreen()
    splash.show()
    sys.exit(app.exec_())