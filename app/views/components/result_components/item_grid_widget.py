from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from .items_container import ItemsContainer


class ItemGridWidget(QWidget):
    """아이템 그리드 위젯 (테이블 대체)"""

    # 아이템 선택 시그널 추가
    itemSelected = pyqtSignal(object, object)  # (선택된 아이템, 컨테이너)

    # 아이템 데이터 변경 시그널 추가 (변경된 필드 정보 포함)
    itemDataChanged = pyqtSignal(object, dict, dict)  # (아이템, 새 데이터, 변경 필드 정보)

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

        # 행 헤더와 열 헤더 저장 (드래그 앤 드롭 시 위치 계산에 필요)
        self.row_headers = []
        self.column_headers = []

        # 라인별 행 그룹 정보 저장
        self.line_row_groups = {}  # 라인명 -> [시작 행 인덱스, 끝 행 인덱스]
        self.row_line_mapping = {}  # 행 인덱스 -> 라인명

    def setupGrid(self, rows, columns, row_headers=None, column_headers=None, line_shifts=None):
        """
        그리드 초기화

        매개변수:
        - rows: 행 수
        - columns: 열 수
        - row_headers: 행 헤더 리스트 (형식: "Line_(교대)")
        - column_headers: 열 헤더 리스트
        - line_shifts: 라인별 교대 정보 (형식: {"라인명": ["주간", "야간"]})
        """
        # 기존 위젯 정리
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.containers = []
        self.line_row_groups = {}
        self.row_line_mapping = {}

        # 헤더 정보 저장
        self.row_headers = row_headers if row_headers else []
        self.column_headers = column_headers if column_headers else []

        # 선택 상태 초기화
        self.current_selected_container = None
        self.current_selected_item = None

        # 열 헤더 추가 (있는 경우) - 첫 번째 열과 두 번째 열은 행 헤더용으로 예약
        if column_headers:
            # 빈 헤더 셀 (첫 번째 행, 첫 번째 열 - 라인 헤더 위)
            empty_header1 = QLabel("")
            empty_header1.setStyleSheet("background-color: #F0F0F0;")
            self.grid_layout.addWidget(empty_header1, 0, 0)

            # 빈 헤더 셀 (첫 번째 행, 두 번째 열 - 교대 헤더 위)
            empty_header2 = QLabel("")
            empty_header2.setStyleSheet("background-color: #F0F0F0;")
            self.grid_layout.addWidget(empty_header2, 0, 1)

            # 열 헤더 추가 (데이터 열)
            for col, header in enumerate(column_headers):
                label = QLabel(header)
                label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #F0F0F0;")
                label.setAlignment(Qt.AlignCenter)
                # 데이터 열은 2부터 시작 (0: 라인 헤더, 1: 교대 헤더)
                self.grid_layout.addWidget(label, 0, col + 2)

        # 라인별 교대 정보가 있는 경우 행 헤더 설정
        if line_shifts:
            row_index = 1  # 실제 행 인덱스 (헤더 다음부터)

            for line, shifts in line_shifts.items():
                # 라인 헤더 (첫 번째 열, 셀 병합)
                start_row = row_index
                line_label = QLabel(line)
                line_label.setStyleSheet("""
                    font-weight: bold; 
                    padding: 5px; 
                    background-color: #1428A0;
                    color: white;
                    border: 1px solid #0C1A6B;
                    border-radius: 10px;
                    font-family: Arial;
                """)
                line_label.setAlignment(Qt.AlignCenter)

                # 교대 수에 따라 행 구성
                shift_rows = []
                for shift in shifts:
                    # 교대 레이블 추가 (두 번째 열)
                    shift_label = QLabel(shift)

                    # 주간/야간에 따라 스타일 다르게 적용
                    if shift == "주간":
                        shift_style = """
                            padding: 5px; 
                            background-color: #F8F8F8;
                            border: 1px solid #D9D9D9;
                            font-weight: bold;
                            font-family: Arial;
                        """
                    else:  # 야간
                        shift_style = """
                            padding: 5px; 
                            background-color: #F0F0F0;
                            border: 1px solid #D9D9D9;
                            color: #666666;
                            font-weight: bold;
                            font-family: Arial;   
                        """
                    shift_label.setStyleSheet(shift_style)
                    shift_label.setAlignment(Qt.AlignCenter)

                    # 교대 레이블을 두 번째 열(인덱스 1)에 배치
                    self.grid_layout.addWidget(shift_label, row_index, 1)

                    # 행 키 생성 및 저장 (내부 관리용)
                    row_key = f"{line}_({shift})"
                    if row_key not in self.row_headers:
                        self.row_headers.append(row_key)

                    # 라인-행 매핑 저장
                    self.row_line_mapping[row_index] = line

                    # 각 셀에 아이템 컨테이너 추가 (데이터 열)
                    row_containers = []
                    for col in range(columns):
                        container = ItemsContainer()
                        container.setMinimumHeight(200)
                        container.setMinimumWidth(230)
                        container.setStyleSheet("border: 1px solid #D9D9D9; background-color: white;")

                        # 아이템 선택 이벤트 연결
                        container.itemSelected.connect(self.on_item_selected)

                        # 아이템 데이터 변경 이벤트 연결
                        container.itemDataChanged.connect(self.on_item_data_changed)

                        # 컨테이너를 데이터 열(인덱스 2부터)에 배치
                        self.grid_layout.addWidget(container, row_index, col + 2)
                        row_containers.append(container)

                    self.containers.append(row_containers)
                    shift_rows.append(row_index)
                    row_index += 1

                # 라인 레이블 세로 병합 (첫 번째 열)
                end_row = row_index - 1
                self.line_row_groups[line] = [start_row, end_row]

                if len(shifts) > 1:  # 교대가 2개 이상일 때만 병합
                    # 라인 레이블을 첫 번째 열(인덱스 0)에 배치하고 세로 병합
                    self.grid_layout.addWidget(line_label, start_row, 0, end_row - start_row + 1, 1)
                else:
                    # 교대가 하나뿐이면 병합 필요 없음
                    self.grid_layout.addWidget(line_label, start_row, 0)
        else:
            # 기존 방식으로 행 헤더와 컨테이너 추가 (여기는 수정 불필요)
            for row in range(rows):
                row_containers = []

                # 행 헤더 추가 (있는 경우)
                if row_headers and row < len(row_headers):
                    label = QLabel(row_headers[row])
                    label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #F0F0F0;")
                    label.setAlignment(Qt.AlignCenter)
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

                    # 기존 방식에서는 데이터 열이 인덱스 1부터 시작
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

    def on_item_data_changed(self, item, new_data, changed_fields=None):
        """아이템 데이터가 변경되었을 때 호출되는 핸들러"""
        # 상위 위젯에 데이터 변경 이벤트 전달 (변경된 필드 정보 포함)
        self.itemDataChanged.emit(item, new_data, changed_fields)

    def addItemAt(self, row, col, item_text, item_data=None, index=-1):
        """
        특정 위치에 아이템 추가

        매개변수:
        - row: 행 인덱스
        - col: 열 인덱스
        - item_text: 표시할 텍스트
        - item_data: 아이템 관련 데이터 (툴팁에 표시할 전체 정보)
        """
        if 0 <= row < len(self.containers) and 0 <= col < len(self.containers[row]):
            if item_data and '_drop_pos_x' in item_data:
                # 내부 사용 후 삭제
                item_data.pop('_drop_pos_x', None)
                item_data.pop('_drop_pos_y', None)
            return self.containers[row][col].addItem(item_text, index, item_data)
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

    def get_line_from_row(self, row_index):
        """행 인덱스에 해당하는 라인명 반환"""
        return self.row_line_mapping.get(row_index)
    
    def set_validator(self, validator):
        self.validator = validator