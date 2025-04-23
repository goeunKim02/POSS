from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag


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
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.setWordWrap(True)
        self.setMinimumHeight(25)
        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

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
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            # 드롭된 아이템의 텍스트 가져오기
            source_text = event.mimeData().text()
            # 현재 아이템의 텍스트 임시 저장
            current_text = self.text()

            # 텍스트 교환
            self.setText(source_text)

            # 소스 위젯 찾기 (소스가 같은 애플리케이션 내에 있는 경우)
            source_widget = event.source()
            if isinstance(source_widget, DraggableItemLabel):
                source_widget.setText(current_text)

            event.acceptProposedAction()