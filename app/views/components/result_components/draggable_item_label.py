from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor


class DraggableItemLabel(QLabel):
    """드래그 가능한 아이템 라벨"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            background-color: #F0F0F0;
            border: 1px solid #D0D0D0;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(False)  # 아이템 자체는 드롭 받지 않도록 변경
        self.drag_start_position = None
        self.setWordWrap(True)
        self.setMinimumHeight(25)
        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)  # 마우스 누를 때 커서 변경

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)  # 마우스 놓을 때 커서 원래대로

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self.drag_start_position is None:
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        # 아이템 데이터와 소스 위치 정보 저장
        mime_data.setText(self.text())
        mime_data.setData("application/x-item-data", self.text().encode())
        drag.setMimeData(mime_data)

        # 드래그 중 표시될 이미지 생성
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)  # 투명 배경으로 시작

        # 아이템의 현재 모습을 픽스맵에 그리기
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)  # 약간 투명하게 만들기
        self.render(painter)
        painter.end()

        # 드래그 이미지 설정
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())  # 마우스 커서 위치 설정

        # 드래그 액션 실행
        drag.exec_(Qt.MoveAction)