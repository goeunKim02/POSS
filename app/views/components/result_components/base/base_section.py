from PyQt5.QtWidgets import QWidget, QObject
from PyQt5.QtCore import pyqtSignal

"""
모든 섹션의 기본 클래스
"""
class BaseSection(QWidget):
    # 공통 시그널
    data_changed = pyqtSignal(object)  # 데이터 변경 시그널
    error_occured = pyqtSignal(str)    # 에러 발생 시그널
    status_changed = pyqtSignal(str)   # 상태 변경 시그널

    def __init__(self, partent=None):
        super().__init__(partent)
        self._controller = None
        self._model = None
        self._initialized = False

    
    """
    컨트롤러 설정
    """
    def set_controller(self, controller):
        self._controller = controller

    """
    모델 설정
    """
    def set_model(self, model):
        self._model = model

    """
    컨트롤러 반환
    """
    def get_controller(self):
        return self._controller
    
    """
    모델 반환
    """
    def get_model(self):
        return self._model
    
    """
    섹션 초기화 : 서브 클래스에서 구현
    """
    def initialize(self):
        if self._initialized:
            return
        
        self.init_ui()
        self.connect_signals()
        self._initialized = True

    """
    UI 구성 : 서브 클래스에서 구현
    """
    def init_ui(self):
        return NotImplementedError("서브 클래스에서 init_ui를 구현해야 합니다.")

    """
    시그널 연결 : 서브 클래스에서 구현
    """
    def connect_signals(self):
        pass

    """
    정리 작업 : 서브 클래스에서 구현
    """
    def cleanup(self):
        self._controller = None
        self._model = None
        self._initialized = None

    """
    초기화 상태 반환
    """
    def is_initialized(self):
        return self._initialized
    

"""
시그널 연결 관리 클래스
"""
class SignalManager(QObject):
    
    def __init__(self):
        super().__init__()
        self._connections = []

    """
    시그널-슬롯 연결 및 추적
    """
    def connect(self, signal, slot):
        signal.connect(slot)
        self._connections.append((signal, slot))

    """
    모든 시그널 연결 해제
    """
    def disconnect_all(self):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except:
                pass
        self._connections.clear()

    """
    연결된 시그널 수 반환
    """
    def get_connect_count(self):
        return len(self._connections)