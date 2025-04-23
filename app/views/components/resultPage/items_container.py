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
        item_label = DraggableItemLabel(item_text, self)
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

    def removeItem(self, item):
        """특정 아이템 삭제"""
        if item in self.items:
            self.layout.removeWidget(item)
            self.items.remove(item)
            item.deleteLater()
            self.adjustHeight()
            self.itemsChanged.emit()

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
            # 드래그된 아이템 텍스트 가져오기
            item_text = event.mimeData().text()

            # 새 아이템으로 추가
            self.addItem(item_text)

            # 원본 위젯을 찾아 삭제
            source = event.source()
            if isinstance(source, DraggableItemLabel):
                # 원본 아이템이 어떤 컨테이너에 속해있는지 찾기
                source_container = source.parent()
                if isinstance(source_container, ItemsContainer):
                    # 원본 컨테이너에서 아이템 삭제
                    source_container.removeItem(source)

            event.acceptProposedAction()
            self.itemsChanged.emit()