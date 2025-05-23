from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

"""
모든 컴포넌트의 기본 클래스
"""
class BaseComponent(QWidget):
    # 공통 시그널
    component_ready = pyqtSignal()     # 컴포넌트 준비 완료
    component_error = pyqtSignal(str)  # 컴포넌트 에러

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_section = parent
        self._data = None
        self._ready = None

    """
    데이터 설정
    """
    def set_data(self, data):
        self._data = data
        self.update_display()

    """
    데이터 반환
    """
    def get_data(self):
        return self._data
    
    """
    화면 업데이트 : 서브 클래스에서 구현
    """
    def update_displya(self):
        pass 


    """
    데이터 초기화
    """
    def clear_data(self):
        self._data = None
        self.update_displya()

    """
    준비 상태 설정
    """
    def set_ready(self, ready: bool = True):
        self._ready = ready
        if ready:
            self.component_ready.emit()

    """
    준비상태 반환
    """
    def is_ready(self):
        return self._ready
    
    """
    부모 섹션 반환
    """
    def get_parent_section(self):
        return self._parent_section
    