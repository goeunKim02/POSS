# help_components/base_tab.py - 수정된 기본 탭 컴포넌트
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt


class BaseTabComponent(QWidget):
    """도움말 탭의 기본 클래스"""

    def __init__(self, parent=None):  # css_path를 선택적 인자로 추가
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # 스크롤 영역 생성
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setStyleSheet("background-color:#F9F9F9; border-radius:10px;")

        # 스크롤 내용을 담을 위젯
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_layout.setAlignment(Qt.AlignTop)

        # 스크롤 영역에 콘텐츠 위젯 설정
        self.scroll_area.setWidget(self.content_widget)

        # 메인 레이아웃에 스크롤 영역 추가
        self.layout.addWidget(self.scroll_area)