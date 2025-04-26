from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from .items_container import ItemsContainer


class ItemGridWidget(QWidget):
    """아이템 그리드 위젯 (테이블 대체)"""

    # 아이템 선택 시그널 추가
    itemSelected = pyqtSignal(object, object)  # (선택된 아이템, 컨테이너)

    # 아이템 데이터 변경 시그널 추가
    itemDataChanged = pyqtSignal(object, dict)  # (아이템, 새 데이터)

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

        # 현재 선택된 아이템 정보
        self.current_selected_container = None
        self.current_selected_item = None

    def setupGrid(self, rows, columns, row_headers=None, column_headers=None):
        """그리드 초기화"""
        # 기존 위젯 정리
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.containers = []

        # 선택 상태 초기화
        self.current_selected_container = None
        self.current_selected_item = None

        # 열 헤더 추가 (있는 경우)
        if column_headers:
            for col, header in enumerate(column_headers):
                label = QLabel(header)
                label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #F0F0F0;")
                label.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(label, 0, col + 1)

        # 행 헤더와 컨테이너 추가
        for row in range(rows):
            row_containers = []

            # 행 헤더 추가 (있는 경우)
            if row_headers and row < len(row_headers):
                label = QLabel(row_headers[row])
                label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #F0F0F0;")
                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.grid_layout.addWidget(label, row + 1, 0)

            # 각 셀에 아이템 컨테이너 추가
            for col in range(columns):
                container = ItemsContainer()
                container.setMinimumHeight(200)
                container.setMinimumWidth(230)
                container.setStyleSheet("border: 1px solid #D9D9D9; background-color: white;")

                # 아이템 선택 이벤트 연결
                container.itemSelected.connect(self.on_item_selected)

                # 아이템 데이터 변경 이벤트 연결
                container.itemDataChanged.connect(self.on_item_data_changed)

                self.grid_layout.addWidget(container, row + 1, col + 1)
                row_containers.append(container)

            self.containers.append(row_containers)

    def on_item_selected(self, selected_item, container):
        """컨테이너에서 아이템이 선택되었을 때 호출되는 핸들러"""
        # 이전에 선택된 컨테이너가 있고, 현재 컨테이너와 다르다면 선택 해제
        if self.current_selected_container and self.current_selected_container != container:
            self.current_selected_container.clear_selection()

        # 현재 선택된 컨테이너와 아이템 업데이트
        self.current_selected_container = container
        self.current_selected_item = selected_item

        # 상위 위젯에 아이템 선택 이벤트 전달
        self.itemSelected.emit(selected_item, container)

    def on_item_data_changed(self, item, new_data):
        """아이템 데이터가 변경되었을 때 호출되는 핸들러"""
        # 상위 위젯에 데이터 변경 이벤트 전달
        self.itemDataChanged.emit(item, new_data)

    def addItemAt(self, row, col, item_text, item_data=None):
        """
        특정 위치에 아이템 추가

        매개변수:
        - row: 행 인덱스
        - col: 열 인덱스
        - item_text: 표시할 텍스트
        - item_data: 아이템 관련 데이터 (툴팁에 표시할 전체 정보)
        """
        if 0 <= row < len(self.containers) and 0 <= col < len(self.containers[row]):
            return self.containers[row][col].addItem(item_text, -1, item_data)
        return None

    def clearAllItems(self):
        """모든 아이템 삭제"""
        # 선택 상태 초기화
        self.current_selected_container = None
        self.current_selected_item = None

        for row in self.containers:
            for container in row:
                container.clearItems()

    def clear_all_selections(self):
        """모든 컨테이너의 선택 상태 초기화"""
        for row in self.containers:
            for container in row:
                container.clear_selection()

        self.current_selected_container = None
        self.current_selected_item = None