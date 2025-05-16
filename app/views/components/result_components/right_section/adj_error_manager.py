from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt

"""
조정 시 에러 메세지 관리 클래스
"""
class AdjErrorManager():
    def __init__(self, parent_widget, error_scroll_area, navigate_callback, left_section):
        self.parent_widget = parent_widget
        self.error_scroll_area = error_scroll_area
        self.navigate_callback = navigate_callback
        self.left_section = left_section

        # 에러 표시 위젯 초기화
        self.error_display_widget = QWidget()
        self.error_display_layout = QVBoxLayout(self.error_display_widget)
        self.error_display_layout.setContentsMargins(5, 5, 5, 5)
        self.error_display_layout.setSpacing(5)
        self.error_display_layout.setAlignment(Qt.AlignTop)
        
        self.error_scroll_area.setWidget(self.error_display_widget)
        self.error_scroll_area.hide()  # 초기에는 숨김

        # 에러 저장소
        self.validation_errors = {}
        self.error_items = set()


    """
    에러 관리
    """
    def add_validation_error(self, item_info, error_message):
        error_key = f"{item_info.get('Line')}_{item_info.get('Time')}_{item_info.get('Item')}"

        # 에러 저장
        self.validation_errors[error_key] = {
            'item_info' : item_info,
            'message' : error_message
        }

        # 에러가 있는 아이템 목록에 추가
        item_key = item_info.get('Item')
        if item_key:
            self.error_items.add(item_key)

        # left_section에 정보 전달
        if hasattr(self.left_section, 'set_current_validation_errors'):
            self.left_section.set_current_validation_errors(self.validation_errors)

        # 에러표시 업데이트
        self.update_error_display()

        # 해당 아이템 카드 강조
        self.highlight_error_item(item_info)

        return self.validation_errors

    
    """
    에러 제거
    """
    def remove_validation_error(self, item_info):
        error_key = f"{item_info.get('Line')}_{item_info.get('Time')}_{item_info.get('Item')}"

        if error_key in self.validation_errors:
            del self.validation_errors[error_key]

            # 해당 아이템에 더 이상 에러가 없다면 목록에서 제거
            item_key = item_info.get('Item')
            if item_key and not any(error['item_info'].get('Item') == item_key for error in self.validation_errors.values()):
                self.error_items.discard(item_key)
        
        # 왼쪽 섹션에 업데이트된 검증 에러 정보 전달
        if hasattr(self.left_section, 'set_current_validation_errors'):
            self.left_section.set_current_validation_errors(self.validation_errors)

        # 에러 표시 업데이트
        self.update_error_display()
        
        # 아이템 카드 강조 해제
        self.remove_item_highlight(item_info)

        return self.validation_errors
    

    """
    에러 표시 위젯 업데이트
    """
    def update_error_display(self):
        # 기존 에러 위젯 제거
        for i in reversed(range(self.error_display_layout.count())):
            child = self.error_display_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        # 에러가 없으면 숨김
        if not self.validation_errors:
            self.error_scroll_area.hide()
            return
        
        # 에러가 있으면 표시
        self.error_scroll_area.show()

        # 에러 제목
        title_label = QLabel("Constraint Violations")
        title_label.setStyleSheet("""
            QLabel {
            background-color: #FF6B6B;
            color: white;
            padding: 5px;
            border-radius: 5px;
            font-weight: bold;
            border: none;
            }
        """)
        self.error_display_layout.addWidget(title_label)

        # 각 에러 표시
        for error_key, error_info in self.validation_errors.items():
            error_widget = self.create_error_item_widget(error_info)
            self.error_display_layout.addWidget(error_widget)

        
    """
    에러 항목 위젯 생성
    """
    def create_error_item_widget(self, error_info):
        class ClickableErrorFrame(QFrame):
            def __init__(self, error_info, navigate_callback):
                super().__init__()
                self.error_info = error_info
                self.navigate_callback = navigate_callback
                
            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    self.navigate_callback(self.error_info)
                super().mousePressEvent(event)

        widget = ClickableErrorFrame(error_info, self.navigate_callback)
        widget.setStyleSheet("""
            QFrame {
                background-color: #FFF5F5;
                border: 3px solid #FEB2B2;
                border-radius: 5px;
                padding: 3px;
                margin: 3px;
                min-height: 30px;
            }
            QFrame:hover {
                background-color: #FFE9E9;
                border-color: #FF8888;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        item_info = error_info['item_info']
        item_location_text = f"Item: {item_info.get('Item', 'N/A')} | Line: {item_info.get('Line', 'N/A')}, Time: {item_info.get('Time', 'N/A')}"

        item_location_label = QLabel(item_location_text)
        item_location_label.setStyleSheet("""
            font-weight: bold; 
            color: #333;
            font-size: 22px;
            border: none;
            background: transparent;
        """)
        item_location_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(item_location_label)

        message_label = QLabel(error_info['message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            color: #D53030; 
            font-size: 22px;
            font-weight: 700;
            border: none;
            background: transparent;
            line-height: 1.5;
        """)
        message_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(message_label)

        return widget
    
    """
    현재 검증 에러 반환
    """
    def get_validation_errors(self):
        return self.validation_errors.copy()

    """
    에러가 있는 아이템 목록 반환
    """
    def get_error_items(self):
        return self.error_items.copy()
    
    """
    에러 여부 확인
    """
    def has_errors(self):
        return bool(self.validation_errors)
    
    """에러가 있는 아이템 카드 강조"""
    def highlight_error_item(self, item_info):
        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드에서 해당 아이템 찾기
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if (hasattr(item, 'item_data') and item.item_data and 
                        item.item_data.get('Line') == item_info.get('Line') and 
                        item.item_data.get('Time') == item_info.get('Time') and 
                        item.item_data.get('Item') == item_info.get('Item')):

                        # 에러 스타일 적용 대신 그냥 선택 상태로만 변경
                        item.set_selected(True)
                        return


    """아이템 카드 강조 해재"""
    def remove_item_highlight(self, item_info):
        error_key = f"{item_info.get('Line')}_{item_info.get('Time')}_{item_info.get('Item')}"
        print(f"에러 해결 시도: {error_key}")
        print(f"현재 에러 목록: {list(self.validation_errors.keys())}")

        if not hasattr(self, 'left_section') or not hasattr(self.left_section, 'grid_widget'):
            return
        
        # 그리드에서 해당 아이템 찾기
        for row_containers in self.left_section.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if (hasattr(item, 'item_data') and item.item_data and 
                        item.item_data.get('Line') == item_info.get('Line') and 
                        item.item_data.get('Time') == item_info.get('Time') and 
                        item.item_data.get('Item') == item_info.get('Item')):

                        # 에러 상태 해제 대신 그냥 선택 해제
                        item.set_selected(False)
                        return
    

