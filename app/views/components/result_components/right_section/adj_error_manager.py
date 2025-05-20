from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from app.utils.item_key_manager import ItemKeyManager

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
        self.error_display_layout.setContentsMargins(3, 3, 3, 3)
        self.error_display_layout.setSpacing(3)
        self.error_display_layout.setAlignment(Qt.AlignTop)
        
        self.error_scroll_area.setWidget(self.error_display_widget)

        # 에러 저장소
        self.validation_errors = {}

    """
    에러 관리
    """
    def add_validation_error(self, item_info, error_message):
        # 고유 키 생성
        error_key = ItemKeyManager.get_item_key(
            item_info.get('Line'),
            item_info.get('Time'), 
            item_info.get('Item')
        )

        # 기존 에러로그들을 유효한 에러로그들로만 필터링
        updated_errors = {}
        for key, value in self.validation_errors.items():
            info = value['item_info']
            line, time, item = info.get('Line'), info.get('Time'), info.get('Item')

            exists = any(
                (self.left_section.data['Line'] == line) &
                (self.left_section.data['Time'] == time) &
                (self.left_section.data['Item'] == item)
            )
            if exists:
                updated_errors[key] = value
        self.validation_errors = updated_errors

        # 새로운 에러 추가
        if error_message:
            self.validation_errors[error_key] = {
                'item_info': item_info,
                'message': error_message
            }

        # left_section에 정보 전달
        if hasattr(self.left_section, 'set_current_validation_errors'):
            self.left_section.set_current_validation_errors(self.validation_errors)

        # 에러 표시 업데이트
        self.update_error_display()

        # 해당 아이템 카드 강조
        self.highlight_error_item(item_info)

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

        # 에러가 없으면 기본 메시지 표시
        if not self.validation_errors:
            no_error_message = QLabel("No adjustment issues detected")
            no_error_message.setAlignment(Qt.AlignCenter)
            no_error_message.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 14px;
                    padding: 20px;
                    border: none;
                }
            """)
            self.error_display_layout.addWidget(no_error_message)
            return
        
        # 기존 에러로그들을 유효한 에러로그들로만 필터링
        updated_errors = {}
        for key, value in self.validation_errors.items():
            info = value['item_info']
            line, time, item = info.get('Line'), info.get('Time'), info.get('Item')
            exists = any(
                (self.left_section.data['Line'] == line) &
                (self.left_section.data['Time'] == time) &
                (self.left_section.data['Item'] == item)
            )
            if exists:
                updated_errors[key] = value
        self.validation_errors = updated_errors

        # 각 에러위젯 추가
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
                min-height: 10px;
            }
            QFrame:hover {
                background-color: #FFE9E9;
                border-color: #FF8888;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)

        item_info = error_info['item_info']
        item_location_text = f"Item: {item_info.get('Item', 'N/A')} | Line: {item_info.get('Line', 'N/A')}, Time: {item_info.get('Time', 'N/A')}"

        item_location_label = QLabel(item_location_text)
        item_location_label.setStyleSheet("""
            font-weight: bold; 
            color: #333;
            font-size: 12px;
            border: none;
            background: transparent;
            margin: 0px;
            padding: 0px;
        """)
        item_location_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(item_location_label)

        message_label = QLabel(error_info['message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            color: #D53030; 
            font-size: 11px;
            font-weight: 500;
            border: none;
            background: transparent;
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
    

