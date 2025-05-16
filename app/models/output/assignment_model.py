from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd
from typing import List, Optional

"""
내부에 DataFrame을 들고 다니며,수량 변경, 이동, 리셋, 적용 같은 모든 로직을 한곳에서 처리
시그널:
    - dataChanged: 모델의 데이터가 바뀌었음을 뷰(View)에 알림 
    - validationFailed: 검증 오류 메시지를 뷰에 전달 
"""
class AssignmentModel(QObject):
    dataChanged = pyqtSignal()  # 모델의 데이터가 바뀌었음을 뷰(View)에 알리는 시그널
    validationFailed = pyqtSignal(dict, str)  # 검증(validation) 오류가 발생했을 때 오류 메시지를 전달하는 시그널

    """
    assignment_df: 최적화 결과로 넘어온 전체 DataFrame
    pre_assigned: 사전할당된 아이템 리스트
    validator: PlanAdjustmentValidator 인스턴스
    """
    def __init__(self, assignment_df: pd.DataFrame, pre_assigned: List[str], validator):
        super().__init__()
        self._original_df = assignment_df.copy()  # 리셋 가능하게 복사
        self._df = assignment_df.copy()  # 실제 뷰로 전달되고 수정할 데이터
        self.pre_assigned = set(pre_assigned)  # 사전할당된 아이템 집합
        self.validator = validator  # 검증 인스턴스

    """
    현재 할당 결과 반환
    """
    def get_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    """
    수량 변경 업데이트
    1) 해당 아이템의 AssignedQty 컬럼을 new_qty로 수정
    2) 검증(validate) → 문제가 있으면 validationFailed 방출
    3) 변경 완료 후 dataChanged 방출
    """
    def update_qty(self, item: str, line: str, time: int, new_qty: int):
        # 1) 라인, 시간, 아이템으로 정확한 행 찾기
        mask = (
            (self._df['Item'] == item) & 
            (self._df['Line'] == str(line)) & 
            (self._df['Time'] == int(time))
        )

        if not mask.any():
            print(f"Model: 해당 아이템({item}, {line}, {time})을 찾을 수 없습니다.")
            return
        
        # 2) 해당 행의 수량만 업데이트
        self._df.loc[mask, 'Qty'] = int(new_qty)
        print(f"Model: {item} @ {line}-{time} 수량 변경: {new_qty}")

        # 3) 수정된 아이템에 대해 검증 수행
        error_msg = self._validate_item(item)
        if error_msg:
            row = self._df.loc[mask].iloc[0].to_dict()  # 현재 행 전체 정보
            self.validationFailed.emit(row, error_msg)  # 검증 실패 시 오류 메시지 시그널 방출
        
        # 4) 모든 처리 후 뷰에 데이터 변경 알림
        self.dataChanged.emit()

    """
    아이템을 new_line, new_shift로 이동
    """
    def move_item(self, item: str, new_line: str, new_shift: str):
        # 아이템의 Line 및 Shift(Time) 업데이트
        idx = self._df['Item'] == item
        if not idx.any():
            return
        
        # Line/Shift 컬럼 업데이트
        self._df.loc[idx, 'Line'] = new_line
        self._df.loc[idx, 'Time'] = new_shift

        # 이동 후 검증 실행
        error_msg = self._validate_item(item)
        if error_msg:
            row = self._df.loc[idx].iloc[0].to_dict()
            self.validationFailed.emit(row, error_msg)
        
        # 데이터 변경 알림
        self.dataChanged.emit()

    """
    원본 상태로 복원
    """
    def reset(self):
        self._df = self._original_df.copy()
        self.dataChanged.emit()

    """
    현재 상태를 원본에 반영
    """
    def apply(self):
        self._original_df = self._df.copy()
        self.dataChanged.emit()

    """
    PlanAdjustmentValidator로 검증, 오류 메시지 반환
    """
    def _validate_item(self, item: str) -> Optional[str]:
        # 검증할 행을 하나 선택
        row = self._df[self._df['Item'] == item].iloc[0]
        valid, message = self.validator.validate_adjustment(
            row.get('Line'),
            row.get('Time'), 
            row.get('Item', ''),
            row.get('Qty', 0)
        )
        return None if valid else message 

