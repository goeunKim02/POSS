# splash_start.py
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient


class SamsungSplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Samsung Production Planning System")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(800, 350)  # 스플래시 화면 크기

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
        if self.progress_value >= 100:
            self.timer.stop()

            # 가상 환경 Python 실행 파일 경로
            python_exe = sys.executable

            # main.py 경로 설정 (PyInstaller 패키징 환경 고려)
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 환경에서는 임시 폴더에 압축이 풀린 파일이 위치함
                main_path = os.path.join(sys._MEIPASS, 'main.py')
                if not os.path.exists(main_path):
                    # main.py가 없으면 직접 main 모듈을 임포트하여 실행
                    self.hide()
                    try:
                        import main
                        # main 모듈의 main 함수 실행 (있다면)
                        if hasattr(main, 'main'):
                            main.main()
                    except Exception as e:
                        print(f"메인 애플리케이션 실행 오류: {e}")
                    finally:
                        self.close()
                        QApplication.quit()
                    return
            else:
                # 일반 실행 환경에서는 현재 디렉토리에서 main.py 찾기
                main_path = 'main.py'

            # 스플래시 화면 숨기기 (아직 종료하지 않음)
            self.hide()

            # 메인 애플리케이션 실행 및 완료 대기
            print(f"메인 애플리케이션 시작: {python_exe} {main_path}")

            # 개발 환경에서는 subprocess.run, 배포 환경에서는 import 사용
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 환경에서는 import 사용
                try:
                    import main
                    if hasattr(main, 'main'):
                        main.main()
                except Exception as e:
                    print(f"메인 애플리케이션 실행 오류: {e}")
            else:
                # 개발 환경에서는 subprocess 사용
                subprocess.run([python_exe, main_path])

            # 메인 애플리케이션이 종료되면 스플래시도 종료
            self.close()
            QApplication.quit()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SamsungSplashScreen()
    splash.show()
    sys.exit(app.exec_())