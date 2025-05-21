from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
from .draggable_item_label import DraggableItemLabel
from .item_edit_dialog import ItemEditDialog
import json
from app.views.components.common.enhanced_message_box import EnhancedMessageBox
from app.utils.item_key_manager import ItemKeyManager
from app.models.common.screen_manager import *

"""
아이템들을 담는 컨테이너 위젯
"""
class ItemsContainer(QWidget):
    # 통합 시그널: change_type in ['add','modify','remove','move','copy']
    itemsChanged = pyqtSignal(str, dict)
    itemSelected = pyqtSignal(object, object)
    itemCopied = pyqtSignal(object, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(w(2))
        self.setAcceptDrops(True)
        self.items = []
        self.selected_item = None

        self.base_height = 100
        self.item_height = 30
        self.setMinimumHeight(self.base_height)

        self.drop_indicator_position = -1
        self.show_drop_indicator = False

        self.default_style = "border: 1px solid  background-color: white;"
        self.empty_style = "background-color: rgba(245, 245, 245, 0.5); border: 1px dashed #cccccc;"

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def _emit_items_changed(self, change_type: str, payload: dict):
        self.itemsChanged.emit(change_type, payload)

    def update_visibility(self):
        # 필요 시 아이템 필터링/보이기 로직 추가
        pass

    def find_parent_grid_widget(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, 'containers') and isinstance(parent.containers, list):
                return parent
            parent = parent.parent()
        return None

    def addItem(self, item_text, index=-1, item_data=None):
        # 스페이서 제거
        self.layout.removeItem(self.spacer)

        item_label = DraggableItemLabel(item_text, self, item_data)
        item_label.itemSelected.connect(self.on_item_selected)
        item_label.itemDoubleClicked.connect(self.on_item_double_clicked)
        item_label.itemDeleteRequested.connect(self.on_item_delete_requested)

        if index == -1 or index >= len(self.items):
            self.layout.addWidget(item_label)
            self.items.append(item_label)
        else:
            self.layout.insertWidget(index, item_label)
            self.items.insert(index, item_label)

        # 스페이서 복원
        self.layout.addSpacerItem(self.spacer)
        item_label.show()

        # add 이벤트
        payload = item_data.copy() if item_data else {}
        payload.update({
            'itemId': ItemKeyManager.extract_item_id(item_label),
            'Item': item_text,
            'Line': item_data.get('Line') if item_data else None,
            'Time': item_data.get('Time') if item_data else None,
        })
        self._emit_items_changed('add', payload)
        return item_label

    def on_item_selected(self, selected_item):
        if self.selected_item and self.selected_item != selected_item:
            self.selected_item.set_selected(False)
        self.selected_item = selected_item
        self.itemSelected.emit(selected_item, self)

    def on_item_double_clicked(self, item):
        if not item or not hasattr(item, 'item_data'):
            return
        dialog = ItemEditDialog(item.item_data, self)
        dialog.itemDataChanged.connect(
            lambda new_data, changed_fields: self.update_item_data(item, new_data, changed_fields)
        )
        dialog.exec_()

    def update_item_data(self, item, new_data, changed_fields=None):
        if item in self.items and new_data:
            payload = {
                'itemId': ItemKeyManager.extract_item_id(item),
                'Item': new_data.get('Item'),
                'Line': new_data.get('Line'),
                'Time': new_data.get('Time'),
                'changedFields': changed_fields or {}
            }
            self._emit_items_changed('modify', payload)
            return True, ""
        return False, "유효하지 않은 아이템 또는 데이터"

    def clear_selection(self):
        if self.selected_item:
            self.selected_item.set_selected(False)
            self.selected_item = None

    def remove_item(self, item):
        # UI 제거만 수행; remove 이벤트는 on_item_delete_requested에서 처리
        if item in self.items:
            if self.selected_item == item:
                self.selected_item = None
            self.layout.removeWidget(item)
            self.items.remove(item)
            item.deleteLater()
            self.update_visibility()

    def clear_items(self):
        self.selected_item = None
        self.layout.removeItem(self.spacer)
        for it in list(self.items):
            self.layout.removeWidget(it)
            it.deleteLater()
        self.items.clear()
        self.layout.addSpacerItem(self.spacer)
        self.update_visibility()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            source = event.source()
            source_container = source.parent() if isinstance(source, DraggableItemLabel) else None
            if source_container and source_container != self:
                self.show_drop_indicator = True
                self.drop_indicator_position = -2
            else:
                self.show_drop_indicator = True
                self.drop_indicator_position = self.findDropIndex(event.pos())
            self.update()

    def dragLeaveEvent(self, event):
        self.show_drop_indicator = False
        self.update()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            source = event.source()
            source_container = source.parent() if isinstance(source, DraggableItemLabel) else None
            self.drop_indicator_position = -2 if source_container and source_container != self else self.findDropIndex(event.pos())
            self.update()

    def findDropIndex(self, pos):
        if not self.items:
            return 0
        for i, item in enumerate(self.items):
            rect = item.geometry()
            mid = rect.top() + rect.height() / 2
            if pos.y() < mid:
                return i
        return len(self.items)

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            return
        # 데이터 파싱
        item_text = event.mimeData().text()
        item_data = None
        if event.mimeData().hasFormat("application/x-item-full-data"):
            try:
                raw = event.mimeData().data("application/x-item-full-data")
                item_data = json.loads(raw.data().decode())
                item_data['_drop_pos_x'] = event.pos().x()
                item_data['_drop_pos_y'] = event.pos().y()
            except:
                pass

        drop_index = self.findDropIndex(event.pos())
        source = event.source()
        source_states = source.item_data if isinstance(source, DraggableItemLabel) else {}

        # Ctrl+드래그: 복사
        if event.keyboardModifiers() & Qt.ControlModifier and isinstance(source, DraggableItemLabel):
            if item_data is None:
                item_data = source.item_data.copy()
            item_data['Qty'] = 0
            new_item = self.addItem(item_data['Item'], -1, item_data)
            payload = item_data.copy()
            payload.update({'itemId': ItemKeyManager.extract_item_id(new_item), 'operation': 'copy'})
            self._emit_items_changed('copy', payload)
            event.acceptProposedAction()
            return

        # 이동
        if isinstance(source, DraggableItemLabel):
            if source.parent() == self:
                # 같은 컨테이너 내 순서 교체
                self.layout.removeItem(self.spacer)
                old_idx = self.items.index(source)
                if old_idx < drop_index:
                    drop_index -= 1
                self.layout.removeWidget(source)
                self.items.pop(old_idx)
                self.layout.insertWidget(drop_index, source)
                self.items.insert(drop_index, source)
                self.layout.addSpacerItem(self.spacer)
            else:
                # 다른 컨테이너에서 이동
                self.addItem(item_text, -1, item_data)
                source.parent().remove_item(source)

            # move 이벤트 한 번만
            payload = {
                'itemId': ItemKeyManager.extract_item_id(source),
                'fromLine': source_states.get('Line'),
                'fromTime': source_states.get('Time'),
                'toLine': item_data.get('Line'),
                'toTime': item_data.get('Time'),
            }
            self._emit_items_changed('move', payload)
            event.acceptProposedAction()
            return

        # 순수 추가
        self.addItem(item_text, -1, item_data)
        event.acceptProposedAction()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.show_drop_indicator:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor(0, 120, 215))
            pen.setWidth(2)
            painter.setPen(pen)
            if self.drop_indicator_position == -2:
                painter.drawRect(1, 1, self.width()-2, self.height()-2)
            else:
                if self.drop_indicator_position >= 0:
                    if self.drop_indicator_position == 0:
                        y = 2
                    elif self.drop_indicator_position >= len(self.items):
                        y = self.items[-1].geometry().bottom() + 2 if self.items else self.height()//2
                    else:
                        y = self.items[self.drop_indicator_position].geometry().top() - 2
                    w = self.width()-4
                    painter.drawLine(2, y, w, y)
                    arrow = 5
                    painter.setBrush(QColor(0, 120, 215))
                    left = [QPoint(2,y), QPoint(2+arrow,y-arrow), QPoint(2+arrow,y+arrow)]
                    painter.drawPolygon(left)
                    right = [QPoint(w,y), QPoint(w-arrow,y-arrow), QPoint(w-arrow,y+arrow)]
                    painter.drawPolygon(right)


    def get_container_position(self, grid_widget):
        if not grid_widget or not hasattr(grid_widget, 'containers'):
            return -1, -1

        for row_idx, row in enumerate(grid_widget.containers):
            for col_idx, container in enumerate(row):
                if container == self:
                    return row_idx, col_idx
        return -1, -1

    """
    그리드 위치를 기반으로 Line과 Time 계산
    """
    def calculate_new_position(self, grid_widget, row_idx, col_idx):
        if not grid_widget or not hasattr(grid_widget, 'row_headers'):
            return None, None

        # 행 헤더에서 Line과 교대 정보 추출
        if row_idx < len(grid_widget.row_headers):
            row_key = grid_widget.row_headers[row_idx]
            if '_(' in row_key:
                line_part = row_key.split('_(')[0]
                shift_part = row_key.split('_(')[1].rstrip(')')

                # Time 계산
                is_day_shift = shift_part == "Night"
                new_time = (col_idx * 2) + (1 if is_day_shift else 2)

                return line_part, new_time

        return None, None

    """
    삭제 요청 처리 메서드
    """
    def on_item_delete_requested(self, item):
        print("DEBUG: ItemsContainer.on_item_delete_requested 호출됨")
        # EnhancedMessageBox를 사용하여 확인 다이얼로그 표시
        from app.views.components.common.enhanced_message_box import EnhancedMessageBox

        reply = EnhancedMessageBox.show_confirmation(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this item?"
        )

        # 확인한 경우에만 삭제 진행
        if reply:
            print("DEBUG: 사용자가 삭제 확인함")
            if item in self.items:
                # 아이템 ID 정보 추출 (삭제 시 전달)
                item_id = ItemKeyManager.extract_item_id(item)

                # 선택된 아이템을 삭제하는 경우 선택 상태 초기화
                if self.selected_item == item:
                    self.selected_item = None

                item_id = ItemKeyManager.extract_item_id(item)
                pos_line = item.item_data.get('Line') if hasattr(item, 'item_data') else None
                pos_time = item.item_data.get('Time') if hasattr(item, 'item_data') else None

                # 아이템 제거
                print("DEBUG: ItemsContainer에서 아이템 제거 시작")
                self.remove_item(item)
                print("DEBUG: ItemsContainer에서 아이템 제거 완료")

                payload = {
                    'itemId': item_id,
                    'Line': pos_line,
                    'Time': pos_time
                }
                self._emit_items_changed('remove', payload)

    def get_container_position(self, grid_widget):
        if not grid_widget or not hasattr(grid_widget, 'containers'):
            return -1, -1

        for row_idx, row in enumerate(grid_widget.containers):
            for col_idx, container in enumerate(row):
                if container == self:
                    return row_idx, col_idx
        return -1, -1

    """
    그리드 위치를 기반으로 Line과 Time 계산
    """
    def calculate_new_position(self, grid_widget, row_idx, col_idx):
        if not grid_widget or not hasattr(grid_widget, 'row_headers'):
            return None, None

        # 행 헤더에서 Line과 교대 정보 추출
        if row_idx < len(grid_widget.row_headers):
            row_key = grid_widget.row_headers[row_idx]
            if '_(' in row_key:
                line_part = row_key.split('_(')[0]
                shift_part = row_key.split('_(')[1].rstrip(')')

                # Time 계산
                is_day_shift = shift_part == "Night"
                new_time = (col_idx * 2) + (1 if is_day_shift else 2)

                return line_part, new_time

        return None, None

    """
    삭제 요청 처리 메서드
    """
    def on_item_delete_requested(self, item):
        print("DEBUG: ItemsContainer.on_item_delete_requested 호출됨")
        # EnhancedMessageBox를 사용하여 확인 다이얼로그 표시
        from app.views.components.common.enhanced_message_box import EnhancedMessageBox

        reply = EnhancedMessageBox.show_confirmation(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this item?"
        )

        # 확인한 경우에만 삭제 진행
        if reply:
            print("DEBUG: 사용자가 삭제 확인함")
            if item in self.items:
                # 아이템 ID 정보 추출 (삭제 시 전달)
                item_id = ItemKeyManager.extract_item_id(item)

                # 선택된 아이템을 삭제하는 경우 선택 상태 초기화
                if self.selected_item == item:
                    self.selected_item = None

                item_id = ItemKeyManager.extract_item_id(item)
                pos_line = item.item_data.get('Line') if hasattr(item, 'item_data') else None
                pos_time = item.item_data.get('Time') if hasattr(item, 'item_data') else None

                # 아이템 제거
                print("DEBUG: ItemsContainer에서 아이템 제거 시작")
                self.remove_item(item)
                print("DEBUG: ItemsContainer에서 아이템 제거 완료")

                payload = {
                    'itemId': item_id,
                    'Line': pos_line,
                    'Time': pos_time
                }
                self._emit_items_changed('remove', payload)