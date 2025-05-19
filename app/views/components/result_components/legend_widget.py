from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QCheckBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from app.resources.fonts.font_manager import font_manager
from app.models.common.screen_manager import *

"""범례 및 필터 위젯"""
class LegendWidget(QWidget):

    # 필터 변경 시그널
    filter_changed = pyqtSignal(dict)  # {status_type: is_checked}
    
    # 특정 필터 활성화 요청 시그널 추가
    filter_activation_requested = pyqtSignal(str)  # status_type

    
    def on_filter_changed(self, status_type, is_checked):
        self.filter_states[status_type] = is_checked
        self.filter_changed.emit(self.filter_states.copy())
        
        # 필터가 활성화되면 해당 상태 분석 요청 시그널 발생
        if is_checked:
            self.filter_activation_requested.emit(status_type)

    def __init__(self, parent=None):
        super().__init__(parent)
        font = font_manager.get_just_font("SamsungOne-700").family()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
                font-family: {font};
            }}
        """)
        
        self.init_ui()

        # 필터 상태 추적
        self.filter_states = {
            'shortage': True,      # 자재부족은 기본 체크 
            'shipment': False,      # 출하실패  
            'pre_assigned': False   # 사전할당
        }

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(h(40))
        
        # 범례 항목들
        self.checkbox_map = {}  # 체크박스 참조 저장
        self.create_legend_item(main_layout, "shortage", "#ff6e63", 'shortage')
        self.create_legend_item(main_layout, "shipment", "#fcc858", 'shipment')  
        self.create_legend_item(main_layout, "pre_assigned", "#a8bbf0", 'pre_assigned')
        
        # 스페이서 추가
        main_layout.addStretch(1)
        
        # 위젯 스타일
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
    """개별 범례 항목 생성"""
    def create_legend_item(self, layout, label_text, color, status_type):
        item_frame = QFrame()
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(5)
        
        # 체크박스
        checkbox = QCheckBox()
        checkbox.setChecked(True if status_type == 'shortage' else False)  # 기본값(자재부족) 
        checkbox.stateChanged.connect(lambda state, st=status_type: 
                                    self.on_filter_changed(st, state == Qt.Checked))
        # 체크박스 참조 저장
        self.checkbox_map[status_type] = checkbox
        item_layout.addWidget(checkbox)
        
        # 색상 표시
        color_frame = QFrame()
        color_frame.setFixedSize(w(15), h(15))
        color_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
            }}
        """)
        item_layout.addWidget(color_frame)
        
        # 라벨
        label = QLabel(label_text)
        item_layout.addWidget(label)
        layout.addWidget(item_frame)

    """필터 상태 재설정 (강제 업데이트)"""
    def refresh_filters(self):
        # 현재 상태 백업
        current_states = self.filter_states.copy()
        
        # 모든 체크박스 강제 업데이트
        for status_type, checkbox in self.checkbox_map.items():
            is_checked = current_states.get(status_type, False)
            
            # 체크 상태가 이미 맞으면 변경하지 않음
            if checkbox.isChecked() == is_checked:
                continue
                
            # 상태가 다르면 체크박스 상태 변경 (강제로 이벤트 발생)
            checkbox.setChecked(is_checked)