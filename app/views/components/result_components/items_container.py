from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
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

    def addItem(self, item_text, index=-1):
        """
        아이템을 추가합니다. index가 -1이면 맨 뒤에 추가, 그 외에는 해당 인덱스에 삽입
        """
        item_label = DraggableItemLabel(item_text, self)

        if index == -1 or index >= len(self.items):
            # 맨 뒤에 추가
            self.layout.addWidget(item_label)
            self.items.append(item_label)
        else:
            # 특정 위치에 삽입
            self.layout.insertWidget(index, item_label)
            self.items.insert(index, item_label)

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

    def dragMoveEvent(self, event):
        """드래그 중 이벤트 - 드롭 가능한 위치에 시각적 표시를 위해 필요"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def findDropIndex(self, pos):
        """
        드롭된 위치에 해당하는 아이템 인덱스를 찾습니다.
        """
        if not self.items:
            return 0  # 아이템이 없으면 첫 번째 위치에 삽입

        # 각 아이템의 위치를 검사하여 드롭 위치 결정
        for i, item in enumerate(self.items):
            item_rect = item.geometry()
            item_mid_y = item_rect.top() + item_rect.height() / 2

            if pos.y() < item_mid_y:
                return i  # 아이템의 중간점보다 위에 드롭되면 해당 아이템 앞에 삽입

        return len(self.items)  # 모든 아이템보다 아래에 드롭되면 마지막에 삽입

    def dropEvent(self, event):
        if event.mimeData().hasText():
            # 드래그된 아이템 텍스트 가져오기
            item_text = event.mimeData().text()

            # 드롭 위치에 해당하는 인덱스 찾기
            drop_index = self.findDropIndex(event.pos())

            # 원본 위젯 (드래그된 아이템)
            source = event.source()

            # 원본 아이템이 같은 컨테이너 내에 있는지 확인
            same_container = False
            source_index = -1

            if isinstance(source, DraggableItemLabel):
                source_container = source.parent()
                if source_container == self:  # 같은 컨테이너 내에서 이동
                    same_container = True
                    source_index = self.items.index(source)

                    # 같은 컨테이너에서 이동할 때 인덱스 조정
                    # 만약 원본 아이템이 대상 위치보다 앞에 있다면 대상 인덱스 조정 필요
                    if source_index < drop_index:
                        drop_index -= 1

                    # 같은 위치로 이동하는 경우 무시
                    if source_index == drop_index:
                        event.acceptProposedAction()
                        return

                    # 원본 아이템 제거 (삭제하지 않고 UI에서만 제거)
                    self.layout.removeWidget(source)
                    self.items.remove(source)

                    # 새 위치에 아이템 다시 삽입
                    self.layout.insertWidget(drop_index, source)
                    self.items.insert(drop_index, source)

                elif isinstance(source_container, ItemsContainer):
                    # 다른 컨테이너에서 이동하는 경우
                    # 새 위치에 아이템 추가
                    self.addItem(item_text, drop_index)

                    # 원본 컨테이너에서 아이템 삭제
                    source_container.removeItem(source)
            else:
                # 새 아이템 생성 (원본이 없는 경우)
                self.addItem(item_text, drop_index)

            event.acceptProposedAction()
            self.itemsChanged.emit()