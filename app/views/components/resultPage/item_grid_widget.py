from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel
from PyQt5.QtCore import Qt
from .items_container import ItemsContainer


class ItemGridWidget(QWidget):
    """아이템 그리드 위젯 (테이블 대체)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)

        # 스크롤 영역 설정
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.main_layout.addWidget(self.scroll_area)

        # 컨테이너 위젯 저장용 2D 배열
        self.containers = []

    def setupGrid(self, rows, columns, row_headers=None, column_headers=None):
        """그리드 초기화"""
        # 기존 위젯 정리
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.containers = []

        # 열 헤더 추가 (있는 경우)
        if column_headers:
            for col, header in enumerate(column_headers):
                label = QLabel(header)
                label.setStyleSheet("font-weight: bold; padding: 5px; background-color: blue;")
                label.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(label, 0, col + 1)

        # 행 헤더와 컨테이너 추가
        for row in range(rows):
            row_containers = []

            # 행 헤더 추가 (있는 경우)
            if row_headers and row < len(row_headers):
                label = QLabel(row_headers[row])
                label.setStyleSheet("font-weight: bold; padding: 5px; background-color: red;")
                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.grid_layout.addWidget(label, row + 1, 0)

            # 각 셀에 아이템 컨테이너 추가
            for col in range(columns):
                container = ItemsContainer()
                container.setMinimumHeight(200)
                container.setMinimumWidth(300)
                container.setStyleSheet("border: 1px solid #D9D9D9; background-color: white;")
                self.grid_layout.addWidget(container, row + 1, col + 1)
                row_containers.append(container)

            self.containers.append(row_containers)

    def addItemAt(self, row, col, item_text):
        """특정 위치에 아이템 추가"""
        if 0 <= row < len(self.containers) and 0 <= col < len(self.containers[row]):
            return self.containers[row][col].addItem(item_text)
        return None

    def clearAllItems(self):
        """모든 아이템 삭제"""
        for row in self.containers:
            for container in row:
                container.clearItems()