"""
아이템 식별을 위한 유틸리티 함수들
"""
import pandas as pd
from typing import Dict, Any, Optional, Tuple

class ItemKeyManager:
    """아이템 고유 키 관리 클래스"""
    
    @staticmethod
    def get_item_key(line: Any, time: Any, item: Any) -> str:
        """
        아이템의 고유 키 생성
        Args:
            line: 라인 정보 (문자열/숫자)
            time: 시간 정보 (문자열/숫자)
            item: 아이템 코드
        Returns:
            고유 키 문자열
        """
        # None이나 빈 값 처리
        line_str = str(line) if line is not None else ""
        time_str = str(time) if time is not None else ""
        item_str = str(item) if item is not None else ""
        
        return f"{line_str}_{time_str}_{item_str}"
    
    @staticmethod
    def parse_item_key(item_key: str) -> Tuple[str, str, str]:
        """
        아이템 키를 파싱하여 line, time, item 반환
        Args:
            item_key: 고유 키 문자열
        Returns:
            (line, time, item) 튜플
        """
        parts = item_key.split('_', 2)  # 최대 3개로 분할
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        return "", "", ""
    
    @staticmethod
    def find_item_in_dataframe(df: pd.DataFrame, line: Any, time: Any, item: Any) -> pd.Series:
        """
        DataFrame에서 특정 아이템 찾기
        Args:
            df: 검색할 DataFrame
            line: 라인 정보
            time: 시간 정보
            item: 아이템 코드
        Returns:
            해당하는 행(Series) 또는 빈 Series
        """
        if df.empty:
            return pd.Series()
        
        mask = (
            (df['Line'].astype(str) == str(line)) &
            (df['Time'].astype(str) == str(time)) &
            (df['Item'].astype(str) == str(item))
        )
        
        matching_rows = df[mask]
        return matching_rows.iloc[0] if not matching_rows.empty else pd.Series()
    
    @staticmethod
    def create_mask_for_item(df: pd.DataFrame, line: Any, time: Any, item: Any) -> pd.Series:
        """
        특정 아이템에 대한 마스크 생성
        Args:
            df: 대상 DataFrame
            line: 라인 정보
            time: 시간 정보
            item: 아이템 코드
        Returns:
            boolean mask Series
        """
        print(f"[DEBUG] 마스크 생성: line={line} ({type(line).__name__}), time={time} ({type(time).__name__}), item={item} ({type(item).__name__})")
        
        # DataFrame에 필요한 컬럼이 있는지 확인
        if not all(col in df.columns for col in ['Line', 'Time', 'Item']):
            print(f"[DEBUG] DataFrame에 필요한 컬럼이 없음: {df.columns.tolist()}")
            return pd.Series(dtype=bool)
        
        # 타입 변환 보장
        line_str = str(line) if line is not None else ""
        time_val = int(time) if time is not None else 0
        item_str = str(item) if item is not None else ""
        
        # 마스크 생성
        mask = (
            (df['Line'].astype(str) == line_str) &
            (df['Time'].astype(int) == time_val) &
            (df['Item'].astype(str) == item_str)
        )
        
        print(f"[DEBUG] 마스크 결과: {mask.sum()}개 행 일치")
        return mask
    
    @staticmethod
    def get_item_from_data(item_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        아이템 데이터 딕셔너리에서 line, time, item 추출
        Args:
            item_data: 아이템 데이터 딕셔너리
        Returns:
            (line, time, item) 튜플
        """
        if not item_data:
            return None, None, None
        
        line = item_data.get('Line')
        time = item_data.get('Time')
        item = item_data.get('Item')
        
        return line, time, item