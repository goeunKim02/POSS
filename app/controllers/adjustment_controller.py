from PyQt5.QtCore import QObject
from typing import Any, Dict

"""
Controller 역할:
    - View에서 발생한 사용자 액션을 Model에 전달
    - Model에서 발생한 변경/오류 시그널을 View에 전달

model: AssignmentModel 인스턴스
view: AdjustmentView 인스턴스
"""
class AdjustmentController(QObject):

    def __init__(self, model: Any, view: Any, error_manager):
        super().__init__()
        self.model = model
        self.view = view
        self.error_manager = error_manager

        # Controller에서 모든 시그널 연결 관리
        self._connect_signals()

    def _connect_signals(self):
        """시그널 연결"""
        # Model -> Error Manager
        self.model.validationFailed.connect(self.error_manager.add_validation_error)
        
        # Model -> Controller (데이터 변경 시)
        self.model.dataChanged.connect(self._on_model_data_changed)
        
        # View -> Controller (아이템 데이터 변경)
        if hasattr(self.view, 'item_data_changed'):
            self.view.item_data_changed.connect(self._on_item_data_changed)
        
        # View -> Controller (셀 이동)  
        if hasattr(self.view, 'cell_moved'):
            self.view.cell_moved.connect(self._on_cell_moved)

        # 최초 한 번, 뷰에 초기 데이터 설정
        self.view.set_data_from_external(self.model.get_dataframe())
        
        print("Controller: 시그널 연결 완료")

    def _on_item_data_changed(self, item: object, new_data: Dict, changed_fields=None):
        """
        아이템 데이터 변경 처리
        • Qty만 바뀌었으면 update_qty 호출
        • Line/Time이 바뀌었으면 move_item 호출
        """
        code = new_data.get('Item')
        line = new_data.get('Line')
        time = new_data.get('Time')
        
        if not code or not line or time is None:
            print(f"Controller: 필수 데이터 누락 - Item: {code}, Line: {line}, Time: {time}")
            return
        
        # changed_fields를 활용한 더 정확한 판단
        if changed_fields:
            # Line 또는 Time 변경 = 이동
            if 'Line' in changed_fields or 'Time' in changed_fields:
                print(f"Controller: 아이템 이동 {code}")
                self.model.move_item(code, line, time)
                return
        
        # 수량 변경 - 라인과 시간 정보도 함께 전달
        if 'Qty' in new_data and line and time is not None:
            qty = new_data['Qty']
            print(f"Controller: 수량 변경 {code} @ {line}-{time} -> {qty}")
            # 수정된 모델의 update_qty 메서드 호출 (라인, 시간 포함)
            self.model.update_qty(code, line, time, qty)

    def _on_model_data_changed(self):
        """
        모델 데이터가 바뀔 때마다 뷰를 업데이트
        • 전체 덮어쓰기보다는 델타 업데이트가 더 효율적일 수 있음
        """
        print("Controller: Model 변경 감지, View 업데이트")
        df = self.model.get_dataframe()
        
        # 방법 1: 전체 데이터 새로고침 (안전하지만 비효율적)
        self.view.set_data_from_external(df)
        
        # 방법 2: 델타 업데이트 (효율적이지만 복잡)
        # self.view.update_specific_items(changed_items)

    def _on_cell_moved(self, item: object, old_data: Dict, new_data: Dict):
        """
        드래그·드롭으로 위치 이동했을 때
        • Controller가 모든 셀 이동 로직 처리
        • 필요시 추가 로직 (시각화 업데이트 등) 수행
        """
        code = new_data.get('Item')
        if code:
            print(f"Controller: 셀 이동 {code} -> {new_data.get('Line')}-{new_data.get('Time')}")
            
            # 1. Model에 데이터 변경 알림
            self.model.move_item(code, new_data['Line'], new_data['Time'])
            
            # 2. 필요시 추가 작업 (시각화 업데이트, 분석 등)
            # 예: 부모 컴포넌트에 셀 이동 이벤트 전달
            if hasattr(self.view, 'parent') and hasattr(self.view.parent(), 'on_cell_moved_from_controller'):
                self.view.parent().on_cell_moved_from_controller(item, old_data, new_data)
            
            print(f"Controller: 셀 이동 처리 완료")
        
    # 추가 유틸리티 메서드들
    def get_current_data(self):
        """현재 모델 데이터 반환"""
        return self.model.get_dataframe()

    def reset_data(self):
        """데이터 리셋"""
        self.model.reset()

    def apply_changes(self):
        """변경사항 적용"""
        self.model.apply()
