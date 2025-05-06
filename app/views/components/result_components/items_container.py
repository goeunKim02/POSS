from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from .draggable_item_label import DraggableItemLabel
from .item_edit_dialog import ItemEditDialog
import json


class ItemsContainer(QWidget):
    """아이템들을 담는 컨테이너 위젯"""

    itemsChanged = pyqtSignal()
    itemSelected = pyqtSignal(object, object)  # (선택된 아이템, 컨테이너) 시그널 추가
    itemDataChanged = pyqtSignal(object, dict, dict)  # (아이템, 새 데이터, 변경 필드 정보) 시그널 추가

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        self.setAcceptDrops(True)
        self.items = []  # 아이템 라벨 리스트
        self.selected_item = None  # 현재 선택된 아이템

        self.base_height = 100
        self.item_height = 30  # 각 아이템의 예상 높이
        self.setMinimumHeight(self.base_height)

        # 드롭 인디케이터 관련 변수
        self.drop_indicator_position = -1
        self.show_drop_indicator = False

        # 늘어나는 공간을 위한 스페이서 추가
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def find_parent_grid_widget(self):
        """현재 컨테이너의 부모 ItemGridWidget을 찾습니다."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'containers') and isinstance(parent.containers, list):
                return parent
            parent = parent.parent()
        return None

    def addItem(self, item_text, index=-1, item_data=None):
        """
        아이템을 추가합니다. index가 -1이면 맨 뒤에 추가, 그 외에는 해당 인덱스에 삽입
        item_data: 아이템에 대한 추가 정보 (pandas Series 또는 딕셔너리)
        """
        # 스페이서 제거
        self.layout.removeItem(self.spacer)

        item_label = DraggableItemLabel(item_text, self, item_data)
        item_label.setFont(QFont('Arial', 8, QFont.Normal))

        # 아이템 선택 이벤트 연결
        item_label.itemSelected.connect(self.on_item_selected)

        # 아이템 더블클릭 이벤트 연결
        item_label.itemDoubleClicked.connect(self.on_item_double_clicked)

        if index == -1 or index >= len(self.items):
            # 맨 뒤에 추가
            self.layout.addWidget(item_label)
            self.items.append(item_label)
        else:
            # 특정 위치에 삽입
            self.layout.insertWidget(index, item_label)
            self.items.insert(index, item_label)

        # 스페이서 다시 추가 (항상 맨 아래에 위치하도록)
        self.layout.addSpacerItem(self.spacer)

        return item_label

    def on_item_selected(self, selected_item):
        """아이템이 선택되었을 때 처리"""
        # 이전에 선택된 아이템이 있고, 현재 선택된 아이템과 다르다면 선택 해제
        if self.selected_item and self.selected_item != selected_item:
            self.selected_item.set_selected(False)

        # 새로 선택된 아이템 저장
        self.selected_item = selected_item

        # 선택 이벤트 발생 (상위 위젯에서 다른 컨테이너의 선택 해제 등을 처리할 수 있도록)
        self.itemSelected.emit(selected_item, self)

    def on_item_double_clicked(self, item):
        """아이템이 더블클릭되었을 때 처리"""
        if not item or not hasattr(item, 'item_data'):
            return

        # 수정 다이얼로그 생성
        dialog = ItemEditDialog(item.item_data, self)

        # 데이터 변경 이벤트 연결 (변경된 필드 정보 포함)
        dialog.itemDataChanged.connect(lambda new_data, changed_fields:
                                       self.update_item_data(item, new_data, changed_fields))

        # 다이얼로그 실행
        dialog.exec_()

    def update_item_data(self, item, new_data, changed_fields=None):
        """아이템 데이터 업데이트"""
        if item and item in self.items and new_data:
            # 아이템 데이터 업데이트 전에 검증 로직을 여기에 통합
            # DraggableItemLabel.update_item_data는 이제 (성공여부, 오류메시지)를 반환
            if hasattr(item, 'update_item_data'):
                success, error_message = item.update_item_data(new_data)
                if not success:
                    # 검증 실패 - 오류 메시지 반환만 하고 UI에 표시하지 않음
                    # UI 표시는 호출자(ModifiedLeftSection)가 처리
                    return False, error_message
            
            # 아이템 데이터 업데이트
            # if item.update_item_data(new_data):
                # 데이터 변경 시그널 발생 (변경 필드 정보 포함)
                self.itemDataChanged.emit(item, new_data, changed_fields)
                self.itemsChanged.emit()
                return True, ""
            return False, "update_item_data 메서드가 없습니다"
        return False, "유효하지 않은 아이템 또는 데이터"

    def clear_selection(self):
        """모든 아이템 선택 해제"""
        if self.selected_item:
            self.selected_item.set_selected(False)
            self.selected_item = None

    def removeItem(self, item):
        """특정 아이템 삭제"""
        if item in self.items:
            # 선택된 아이템을 삭제하는 경우 선택 상태 초기화
            if item == self.selected_item:
                self.selected_item = None

            self.layout.removeWidget(item)
            self.items.remove(item)
            item.deleteLater()
            self.itemsChanged.emit()

    def clearItems(self):
        """모든 아이템 삭제"""
        self.selected_item = None  # 선택 상태 초기화

        # 스페이서 제거 (임시)
        self.layout.removeItem(self.spacer)

        for item in self.items:
            self.layout.removeWidget(item)
            item.deleteLater()
        self.items.clear()

        # 스페이서 다시 추가
        self.layout.addSpacerItem(self.spacer)

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
                    print(f"드롭 이벤트에서 파싱된 아이템 데이터: {item_data}")
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

                    # 스페이서 제거 (임시)
                    self.layout.removeItem(self.spacer)

                    # 원본 아이템 제거 (삭제하지 않고 UI에서만 제거)
                    self.layout.removeWidget(source)
                    self.items.remove(source)

                    # 새 위치에 아이템 다시 삽입
                    self.layout.insertWidget(drop_index, source)
                    self.items.insert(drop_index, source)

                    # 스페이서 다시 추가
                    self.layout.addSpacerItem(self.spacer)

                elif isinstance(source_container, ItemsContainer):
                    # 다른 컨테이너에서 이동하는 경우
                    # 부모 위젯 찾기 (ItemGridWidget)
                    grid_widget = self.find_parent_grid_widget()

                    # 현재 컨테이너의 위치 구하기
                    target_row, target_col = -1, -1
                    if grid_widget:
                        for row_idx, row in enumerate(grid_widget.containers):
                            if self in row:
                                target_row = row_idx
                                target_col = row.index(self)
                                break

                    # 아이템 데이터가 없으면 소스 아이템에서 가져오기
                    if item_data is None and hasattr(source, 'item_data'):
                        if source.item_data is not None:
                            item_data = source.item_data.copy()

                    # 새 위치에 대한 데이터 업데이트
                    if item_data and target_row >= 0 and target_col >= 0:
                        # Import ItemPositionManager
                        from .item_position_manager import ItemPositionManager

                        # 현재 행의 라인과 교대 정보 추출
                        if grid_widget and grid_widget.row_headers and target_row < len(grid_widget.row_headers):
                            row_key = grid_widget.row_headers[target_row]

                            # 라인 정보 추출 (Line_() 형식에서 Line 부분)
                            if '_(' in row_key:
                                line_part = row_key.split('_(')[0]
                                shift_part = row_key.split('_(')[1].rstrip(')')

                                # Line 값 업데이트
                                item_data['Line'] = line_part

                                # Time 값 계산 및 업데이트
                                day_idx = target_col  # 열 인덱스는 요일 인덱스와 대응

                                # 교대 정보에 따라 Time 값 결정 (주간: 홀수, 야간: 짝수)
                                is_day_shift = shift_part == "주간"
                                new_time = (day_idx * 2) + (1 if is_day_shift else 2)

                                # Time 값 업데이트
                                item_data['Time'] = str(new_time)

                                # 제약사항 검증
                                validator = None
                                if hasattr(grid_widget, 'validator'):
                                    validator = grid_widget.validator

                                if validator:
                                    # 기존 위치 정보
                                    source_line = source.item_data.get('Line') if hasattr(source, 'item_data') else None
                                    source_time = source.item_data.get('Time') if hasattr(source, 'item_data') else None

                                    # 검증 실행
                                    valid, message = validator.validate_adjustment(
                                        line_part,  # 새 라인
                                        new_time,   # 새 시간(시프트)
                                        item_data.get('Item', ''),  # 아이템 코드
                                        item_data.get('Qty', 0),    # 수량
                                        source_line,  # 원래 라인
                                        source_time   # 원래 시간(시프트)
                                    )

                                     # 검증 실패 시 드롭 거부하고 함수 종료
                                    if not valid:
                                        QMessageBox.warning(self, "이동 불가", message)
                                        event.ignore()  # 드롭 거부
                                        self.show_drop_indicator = False
                                        self.update()
                                        return

                                print(f"드래그 위치에 맞게 데이터 업데이트: Line={line_part}, Time={new_time}")

                    # 선택 상태 확인
                    was_selected = getattr(source, 'is_selected', False)

                    # 새 위치에 아이템 추가 (업데이트된 데이터 포함)
                    new_item = self.addItem(item_text, drop_index, item_data)

                    # 새 아이템의 텍스트 업데이트
                    if new_item and hasattr(new_item, 'update_text_from_data'):
                        new_item.update_text_from_data()

                    # 이전 아이템이 선택되어 있었으면 새 아이템도 선택 상태로 설정
                    if was_selected:
                        new_item.set_selected(True)
                        self.on_item_selected(new_item)

                    # 데이터 변경 시그널 발생
                    if new_item and item_data and hasattr(source, 'item_data'):
                        # 변경된 필드 정보 생성
                        changed_fields = {}

                        # Line 값이 변경되었는지 확인
                        if 'Line' in source.item_data and 'Line' in item_data:
                            if source.item_data.get('Line', '') != item_data.get('Line', ''):
                                changed_fields['Line'] = {
                                    'from': source.item_data.get('Line', ''),
                                    'to': item_data.get('Line', '')
                                }

                        # Time 값이 변경되었는지 확인
                        if 'Time' in source.item_data and 'Time' in item_data:
                            if source.item_data.get('Time', '') != item_data.get('Time', ''):
                                changed_fields['Time'] = {
                                    'from': source.item_data.get('Time', ''),
                                    'to': item_data.get('Time', '')
                                }

                        # 변경 사항 알림
                        self.itemDataChanged.emit(new_item, item_data, changed_fields)

                    # 원본 컨테이너에서 아이템 삭제
                    source_container.removeItem(source)
            else:
                # 새 아이템 생성 (원본이 없는 경우)
                new_item = self.addItem(item_text, drop_index, item_data)
                # 새 아이템의 텍스트 업데이트
                if new_item and hasattr(new_item, 'update_text_from_data'):
                    new_item.update_text_from_data()

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