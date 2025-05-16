from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QProgressBar, QLabel,
    QPushButton, QFrame, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from app.resources.fonts.font_manager import font_manager
from app.models.common.settings_store import SettingsStore
from app.models.common.screen_manager import *


class OptimizationProgressDialog(QDialog):
    """최적화 진행 상황을 표시하는 다이얼로그"""

    optimization_completed = pyqtSignal()
    optimization_cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Optimization is in progress.")
        self.setModal(True)
        self.setFixedSize(w(1000), h(600))

        # WindowStaysOnTopHint 제거하고 대신 다른 플래그 사용
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        # 다이얼로그가 부모 창 중앙에 위치하도록 설정
        if parent:
            parent_rect = parent.geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

        # 진행 상태 변수
        self.current_progress = 0
        self.total_time = SettingsStore.get('time_limit1', 10)  # 초 단위
        self.is_running = False

        # 타이머 설정
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        self.init_ui()

        # 다이얼로그를 최상위로 유지
        self.raise_()
        self.activateWindow()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 제목 프레임
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1428A0;
                border: none;
                padding: 0px;
            }}
        """)
        title_frame.setFixedHeight(h(80))

        # 제목 프레임의 레이아웃을 먼저 생성하고 설정
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(w(20), 0, w(20), 0)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        # 제목 레이블
        title_label = QLabel("First Optimization")
        title_font = font_manager.get_font("SamsungSharpSans-Bold", f(15))
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")

        # 레이아웃에 레이블 추가
        title_layout.addWidget(title_label)

        main_layout.addWidget(title_frame)

        # 컨텐츠 영역
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(w(30), h(40), w(30), h(30))
        content_layout.setSpacing(w(20))

        # 진행 상태 레이블
        self.status_label = QLabel("First optimization is currently underway...")
        status_font = font_manager.get_font("SamsungOne-700", f(12))
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: #333333;
                padding: {w(10)}px;
            }}
        """)
        content_layout.addWidget(self.status_label)

        # 프로그래스바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #E0E0E0;
                border-radius: {w(8)}px;
                background-color: white;
                text-align: center;
                height: {h(40)}px;
                font-size: {f(11)}px;
                font-weight: bold;
                color: #333333;
            }}
            QProgressBar::chunk {{
                background-color: #1428A0;
                border-radius: {w(6)}px;
                margin: {w(2)}px;
            }}
        """)
        content_layout.addWidget(self.progress_bar)

        # 시간 정보 레이블
        self.time_label = QLabel(f"Estimated time: {self.total_time}(s)")
        time_font = font_manager.get_font("SamsungOne-700", f(10))
        self.time_label.setFont(time_font)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: #666666;
                padding: {w(5)}px;
            }}
        """)
        content_layout.addWidget(self.time_label)

        content_layout.addStretch()

        main_layout.addWidget(content_frame)

        # 버튼 영역
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #F0F0F0;
                border: none;
                border-top: 1px solid #E0E0E0;
                padding: {w(15)}px;
            }}
        """)
        button_frame.setFixedHeight(h(70))

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(w(20), 0, w(20), 0)
        button_layout.addStretch()

        # 취소 버튼
        self.cancel_button = QPushButton("cancel")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_font = font_manager.get_font("SamsungOne-700", f(10))
        cancel_font.setBold(True)
        self.cancel_button.setFont(cancel_font)
        self.cancel_button.setFixedSize(w(100), h(36))
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: {w(5)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #D0D0D0;
            }}
            QPushButton:pressed {{
                background-color: #C0C0C0;
            }}
        """)
        self.cancel_button.clicked.connect(self.cancel_optimization)
        button_layout.addWidget(self.cancel_button)

        main_layout.addWidget(button_frame)

    def start_optimization(self):
        """최적화 프로세스 시작"""
        self.is_running = True
        self.current_progress = 0
        self.progress_bar.setValue(0)

        # 진행 시간 계산 (100ms 간격으로 업데이트)
        self.timer.start(100)  # 0.1초마다 업데이트

    def update_progress(self):
        """프로그래스바 업데이트"""
        if not self.is_running:
            return

        # 진행률 계산
        elapsed_time = (self.current_progress / 10)  # 0.1초 단위로 계산
        progress_percentage = min((elapsed_time / self.total_time) * 100, 100)

        # 50% 이상일 때 텍스트 색상을 하얀색으로 변경
        if progress_percentage >= 50:
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #E0E0E0;
                    border-radius: {w(8)}px;
                    background-color: white;
                    text-align: center;
                    height: {h(40)}px;
                    font-size: {f(11)}px;
                    font-weight: bold;
                    color: white;  /* 텍스트 색상을 하얀색으로 변경 */
                }}
                QProgressBar::chunk {{
                    background-color: #1428A0;
                    border-radius: {w(6)}px;
                    margin: {w(2)}px;
                }}
            """)
        else:
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #E0E0E0;
                    border-radius: {w(8)}px;
                    background-color: white;
                    text-align: center;
                    height: {h(40)}px;
                    font-size: {f(11)}px;
                    font-weight: bold;
                    color: #333333;  /* 기본 텍스트 색상 */
                }}
                QProgressBar::chunk {{
                    background-color: #1428A0;
                    border-radius: {w(6)}px;
                    margin: {w(2)}px;
                }}
            """)

        self.progress_bar.setValue(int(progress_percentage))

        # 남은 시간 계산
        remaining_time = max(self.total_time - elapsed_time, 0)
        self.time_label.setText(f"Estimated time: {remaining_time:.1f}(s)")

        # 진행률 증가
        self.current_progress += 1

        # 완료 체크
        if progress_percentage >= 100:
            self.optimization_complete()

    def optimization_complete(self):
        """최적화 완료 처리"""
        self.is_running = False
        self.timer.stop()

        self.status_label.setText("Optimization is complete!")
        self.progress_bar.setValue(100)
        self.time_label.setText("Complete")
        self.cancel_button.setText("Close")

        # 완료 시그널 발생
        self.optimization_completed.emit()

        # 1초 후 자동 닫기
        QTimer.singleShot(1000, self.accept)

    def cancel_optimization(self):
        """최적화 취소"""
        if self.is_running:
            self.is_running = False
            self.timer.stop()

            # 시그널 발생 전에 다이얼로그 상태 변경
            self.status_label.setText("Optimization has been canceled.")
            self.cancel_button.setText("Close")

            # 즉시 시그널 발생하고 다이얼로그 닫기
            self.optimization_cancelled.emit()
            self.reject()
        else:
            self.accept()

    def closeEvent(self, event):
        """다이얼로그 닫기 이벤트 처리"""
        if self.is_running:
            self.is_running = False
            if self.timer and self.timer.isActive():
                self.timer.stop()
            self.optimization_cancelled.emit()
        event.accept()

    def keyPressEvent(self, event):
        """키 이벤트 처리 - ESC 키 처리"""
        if event.key() == Qt.Key_Escape:
            if self.is_running:
                self.cancel_optimization()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)