from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
from .draggable_item_label import DraggableItemLabel
import json


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

        # 드롭 인디케이터 관련 변수
        self.drop_indicator_position = -1
        self.show_drop_indicator = False

    def addItem(self, item_text, index=-1, item_data=None):
        """
        아이템을 추가합니다. index가 -1이면 맨 뒤에 추가, 그 외에는 해당 인덱스에 삽입
        item_data: 아이템에 대한 추가 정보 (pandas Series 또는 딕셔너리)
        """
        item_label = DraggableItemLabel(item_text, self, item_data)

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
            # 드래그 시작 시 인디케이터 표시
            self.show_drop_indicator = True
            self.drop_indicator_position = self.findDropIndex(event.pos())
            self.update()  # 화면 갱신

    def dragLeaveEvent(self, event):
        """드래그가 위젯을 벗어날 때 인디케이터 숨김"""
        self.show_drop_indicator = False
        self.update()

    def dragMoveEvent(self, event):
        """드래그 중 이벤트 - 드롭 가능한 위치에 시각적 표시"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # 드래그 중 인디케이터 위치 업데이트
            self.drop_indicator_position = self.findDropIndex(event.pos())
            self.update()  # 화면 갱신

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

            # 전체 아이템 데이터 가져오기 (JSON 형식)
            item_data = None
            if event.mimeData().hasFormat("application/x-item-full-data"):
                try:
                    data_bytes = event.mimeData().data("application/x-item-full-data")
                    json_str = data_bytes.data().decode()
                    item_data = json.loads(json_str)
                except Exception as e:
                    print(f"아이템 데이터 파싱 오류: {e}")

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
                        # 인디케이터 숨기기
                        self.show_drop_indicator = False
                        self.update()
                        return

                    # 원본 아이템 제거 (삭제하지 않고 UI에서만 제거)
                    self.layout.removeWidget(source)
                    self.items.remove(source)

                    # 새 위치에 아이템 다시 삽입
                    self.layout.insertWidget(drop_index, source)
                    self.items.insert(drop_index, source)

                elif isinstance(source_container, ItemsContainer):
                    # 다른 컨테이너에서 이동하는 경우
                    # 아이템 데이터가 없으면 소스 아이템에서 가져오기
                    if item_data is None and hasattr(source, 'item_data'):
                        item_data = source.item_data

                    # 새 위치에 아이템 추가 (전체 데이터 포함)
                    self.addItem(item_text, drop_index, item_data)

                    # 원본 컨테이너에서 아이템 삭제
                    source_container.removeItem(source)
            else:
                # 새 아이템 생성 (원본이 없는 경우)
                self.addItem(item_text, drop_index, item_data)

            # 드롭 완료 후 인디케이터 숨기기
            self.show_drop_indicator = False
            self.update()

            event.acceptProposedAction()
            self.itemsChanged.emit()

    def paintEvent(self, event):
        """컨테이너 위젯 그리기 - 드롭 인디케이터 표시"""
        super().paintEvent(event)

        # 드롭 인디케이터 그리기
        if self.show_drop_indicator and self.drop_indicator_position >= 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # 인디케이터 스타일 설정
            pen = QPen(QColor(0, 120, 215))  # 파란색 인디케이터
            pen.setWidth(2)
            painter.setPen(pen)

            # 인디케이터 위치 계산
            if self.drop_indicator_position == 0:
                # 첫 번째 위치
                y = 2  # 상단 여백
            elif self.drop_indicator_position >= len(self.items):
                # 마지막 위치
                if len(self.items) > 0:
                    last_item = self.items[-1]
                    y = last_item.geometry().bottom() + 2
                else:
                    y = self.height() // 2
            else:
                # 중간 위치
                item = self.items[self.drop_indicator_position]
                y = item.geometry().top() - 2

            # 선 그리기
            width = self.width() - 4  # 양쪽 여백 2픽셀씩
            painter.drawLine(2, y, width, y)

            # 화살표 그리기 (양쪽에 작은 삼각형)
            arrow_size = 5
            painter.setBrush(QColor(0, 120, 215))  # 화살표 채우기

            # 왼쪽 화살표
            points_left = [
                QPoint(2, y),
                QPoint(2 + arrow_size, y - arrow_size),
                QPoint(2 + arrow_size, y + arrow_size)
            ]
            painter.drawPolygon(points_left)

            # 오른쪽 화살표
            points_right = [
                QPoint(width, y),
                QPoint(width - arrow_size, y - arrow_size),
                QPoint(width - arrow_size, y + arrow_size)
            ]
            painter.drawPolygon(points_right)