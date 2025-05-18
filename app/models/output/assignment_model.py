from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd
from typing import List, Optional
from app.utils.item_key import ItemKeyManager

"""
내부에 DataFrame을 들고 다니며,수량 변경, 이동, 리셋, 적용 같은 모든 로직을 한곳에서 처리
시그널:
    - modelDataChanged: 모델의 데이터가 바뀌었음을 뷰(View)에 알림 
    - validationFailed: 검증 오류 메시지를 뷰에 전달 
"""
class AssignmentModel(QObject):
    modelDataChanged = pyqtSignal()  # 모델의 데이터가 바뀌었음을 뷰(View)에 알리는 시그널
    validationFailed = pyqtSignal(dict, str)  # 검증(validation) 오류가 발생했을 때 오류 메시지를 전달하는 시그널

    """
    assignment_df: 최적화 결과로 넘어온 전체 DataFrame
    pre_assigned: 사전할당된 아이템 리스트
    validator: PlanAdjustmentValidator 인스턴스
    """
    def __init__(self, assignment_df: pd.DataFrame, pre_assigned: List[str], validator):
        super().__init__()
        # 초기 데이터프레임에 타입 강제 적용
        assignment_df = self._ensure_correct_types(assignment_df.copy())

        self._original_df = assignment_df.copy()  # 리셋 가능하게 복사
        self._df = assignment_df.copy()  # 실제 뷰로 전달되고 수정할 데이터
        self.pre_assigned = set(pre_assigned)  # 사전할당된 아이템 집합
        self.validator = validator  # 검증 인스턴스
    
    def _ensure_correct_types(self, df):
        """DataFrame의 타입을 올바르게 강제 변환"""
        if df is not None and not df.empty:
            # Line은 항상 문자열
            if 'Line' in df.columns:
                df['Line'] = df['Line'].astype(str)
            
            # Time은 항상 정수
            if 'Time' in df.columns:
                df['Time'] = pd.to_numeric(df['Time'], errors='coerce').fillna(0).astype(int)
            
            # Item은 항상 문자열
            if 'Item' in df.columns:
                df['Item'] = df['Item'].astype(str)
            
            # Qty는 항상 정수
            if 'Qty' in df.columns:
                df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
        
        return df

    """
    현재 할당 결과 반환
    """
    def get_dataframe(self) -> pd.DataFrame:
        df = self._df.copy()
        return self._ensure_correct_types(df)

    """
    수량 변경 업데이트
    1) 해당 아이템의 AssignedQty 컬럼을 new_qty로 수정
    2) 검증(validate) → 문제가 있으면 validationFailed 방출
    3) 변경 완료 후 modelDataChanged 방출
    """
    def update_qty(self, item: str, line: str, time: int, new_qty: int):
        # 1) 라인, 시간, 아이템으로 정확한 행 찾기
        mask = ItemKeyManager.create_mask_for_item(self._df, line, time, item)

        if not mask.any():
            print(f"Model: 해당 아이템({item}, {line}, {time})을 찾을 수 없습니다.")
            return
        
        # 변경이 필요한지 확인
        current_qty = self._df.loc[mask, 'Qty'].iloc[0]
        if current_qty == new_qty:
            return True  # 이미 동일한 값이면 변경 없이 성공으로 처리

        # 2) 해당 행의 수량만 업데이트
        self._df.loc[mask, 'Qty'] = int(new_qty)
        print(f"Model: {item} @ {line}-{time} 수량 변경: {new_qty}")

        # 3) 수정된 아이템에 대해 검증 수행
        error_msg = self._validate_item(item, line, time)
        if error_msg:
            row = self._df.loc[mask].iloc[0].to_dict()  # 현재 행 전체 정보
            self.validationFailed.emit(row, error_msg)  # 검증 실패 시 오류 메시지 시그널 방출
        
        # 4) 모든 처리 후 뷰에 데이터 변경 알림
        self.modelDataChanged.emit()

        return True

    """
    아이템을 new_line, new_shift로 이동
    """
    def move_item(self, item: str, old_line: str, old_time: int, new_line: str, new_time: int):
        # ItemKeyManager를 사용하여 마스크 생성
        mask = ItemKeyManager.create_mask_for_item(self._df, old_line, old_time, item)

        if not mask.any():
            print(f"Model: 해당 아이템({item}, {old_line}, {old_time})을 찾을 수 없습니다.")
            return
        
        # 변경 사항이 없으면 업데이트하지 않음
        if str(old_line) == str(new_line) and int(old_time) == int(new_time):
            return  # 변경 없음, 조기 종료
    
        # Line/Time 컬럼 업데이트
        self._df.loc[mask, 'Line'] = str(new_line)
        self._df.loc[mask, 'Time'] = int(new_time)


        # 이동 후 검증 실행
        error_msg = self._validate_item(item, new_line, new_time)
        if error_msg:
            row = self._df.loc[mask].iloc[0].to_dict()
            self.validationFailed.emit(row, error_msg)
        
        # 데이터 변경 알림
        self.modelDataChanged.emit()

    """
    원본 상태로 복원

    """
    def reset(self):
        self._df = self._original_df.copy()
        self.modelDataChanged.emit()

    """
    현재 상태를 원본에 반영
    """
    def apply(self):
        self._original_df = self._df.copy()
        self.modelDataChanged.emit()

    """
    PlanAdjustmentValidator로 검증, 오류 메시지 반환
    """
    def _validate_item(self, item: str, line: str = None, time: int = None) -> Optional[str]:
        try:
            # 라인과 시간이 지정되지 않은 경우, DataFrame에서 해당 아이템 검색
            if line is None or time is None:
                # 마스크를 사용하여 첫 번째 항목 찾기
                mask = self._df['Item'] == item
                if not mask.any():
                    return f"아이템 {item}을 찾을 수 없습니다."
                    
                row = self._df.loc[mask].iloc[0]
                line = row.get('Line')
                time = row.get('Time')
            
            # 실제 검증 수행
            valid, message = self.validator.validate_adjustment(
                line,
                time, 
                item,
                self.get_item_qty(item, line, time)
            )
            return None if valid else message
        
        except Exception as e:
            print(f"검증 오류: {e}")
            return f"검증 중 오류 발생: {str(e)}"
        

    def get_item_qty(self, item: str, line: str, time: int) -> int:
        """
        특정 위치의 아이템 수량 가져오기
        """
        mask = ItemKeyManager.create_mask_for_item(self._df, line, time, item)
        if mask.any():
            return int(self._df.loc[mask, 'Qty'].iloc[0])
        return 0