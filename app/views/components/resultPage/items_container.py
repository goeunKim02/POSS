from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from .draggable_item_label import DraggableItemLabel


class ItemsContainer(QWidget):
    """아이템들을 담는 컨테이너 위젯"""

    itemsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        self.setAcceptDrops(True)
        self.items = []  # 아이템 라벨 리스트

        self.base_height = 100
        self.item_height = 30  # 각 아이템의 예상 높이
        self.setMinimumHeight(self.base_height)

    def addItem(self, item_text):
        item_label = DraggableItemLabel(item_text)
        self.layout.addWidget(item_label)
        self.items.append(item_label)
        self.adjustHeight()
        return item_label

    def adjustHeight(self):
        """아이템 개수에 따라 컨테이너 높이 자동 조정"""
        if not self.items:
            # 아이템이 없으면 기본 높이 설정
            self.setMinimumHeight(self.base_height)
            return

        # 아이템 개수에 따라 높이 계산 (여유 공간 포함)
        items_height = len(self.items) * self.item_height
        padding = 10  # 여유 공간
        new_height = max(self.base_height, items_height + padding)

        # 컨테이너 최소 높이 설정
        self.setMinimumHeight(new_height)

    def clearItems(self):
        for item in self.items:
            self.layout.removeWidget(item)
            item.deleteLater()
        self.items.clear()
        self.setMinimumHeight(self.base_height)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            # 새 아이템 추가
            self.addItem(event.mimeData().text())

            # 소스 위젯 삭제 (옵션)
            source_widget = event.source()
            if isinstance(source_widget, DraggableItemLabel) and source_widget not in self.items:
                parent_container = source_widget.parent()
                source_widget.setParent(None)
                source_widget.deleteLater()

                if hasattr(parent_container, 'adjustHeight'):
                    parent_container.adjustHeight()

            event.acceptProposedAction()
            self.itemsChanged.emit()
            self.adjustHeight()