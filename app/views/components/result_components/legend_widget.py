from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QCheckBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

"""범례 및 필터 위젯"""
class LegendWidget(QWidget):

    # 필터 변경 시그널
    filter_changed = pyqtSignal(dict)  # {status_type: is_checked}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        self.init_ui()
        
        # 필터 상태 추적
        self.filter_states = {
            'shortage': False,      # 자재부족
            'shipment': False,      # 출하실패  
            'pre_assigned': False   # 사전할당
        }
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 10, 5)
        main_layout.setSpacing(40)
        
        # 범례 항목들
        self.create_legend_item(main_layout, "shortage", "#f0afa8", 'shortage')
        self.create_legend_item(main_layout, "shipment", "#faf3b1", 'shipment')  
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
        checkbox.setChecked(False)  # 기본값 : 체크해제 
        checkbox.stateChanged.connect(lambda state, st=status_type: 
                                    self.on_filter_changed(st, state == Qt.Checked))
        item_layout.addWidget(checkbox)
        
        # 색상 표시
        color_frame = QFrame()
        color_frame.setFixedSize(30, 30)
        color_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
            }}
        """)
        item_layout.addWidget(color_frame)
        
        # 라벨
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 9))
        item_layout.addWidget(label)
        
        layout.addWidget(item_frame)
        
    """필터 상태 변경 처리"""
    def on_filter_changed(self, status_type, is_checked):
        self.filter_states[status_type] = is_checked
        self.filter_changed.emit(self.filter_states.copy())