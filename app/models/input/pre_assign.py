import pandas as pd
from app.utils.fileHandler import load_file
from app.models.common.file_store import FilePaths
from dataclasses import dataclass
from typing import Any, List, Tuple, Dict


class DataLoader:
    @staticmethod
    def load_dynamic_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        dynamic_excel_file에서 'fixed_option' 및 'pre_assign' 시트를 로드
        """
        path = FilePaths.get("dynamic_excel_file")
        if not path:
            return pd.DataFrame()
        raw = load_file(path)
        fixed_opt  = raw.get('fixed_option', pd.DataFrame())
        fixed_opt['Fixed_Time'] = fixed_opt['Fixed_Time'].astype(str)
        pre_assign = raw.get('pre_assign',   pd.DataFrame())
        return fixed_opt, pre_assign

    @staticmethod
    def load_demand_data() -> pd.DataFrame:
        """
        demand_excel_file에서 'demand' 시트를 로드
        """
        path = FilePaths.get("demand_excel_file")
        if not path:
            return pd.DataFrame()
        raw = load_file(path)
        return raw.get('demand', pd.DataFrame())

    @staticmethod
    def load_master_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        dynamic_excel_file에서 'line_available', 'capa_qty' 시트를 로드
        """
        path = FilePaths.get("master_excel_file")
        if not path:
            return pd.DataFrame()
        raw = load_file(path)
        line_avail = raw.get('line_available', pd.DataFrame())
        capa_qty   = raw.get('capa_qty',       pd.DataFrame())
        return line_avail, capa_qty


@dataclass
class Request:
    """
    :param idx: 요청 인덱스
    :param lines: 할당 가능한 라인 목록
    :param times: 할당 가능한 시간(슬롯) 목록
    :param qty: 요청 수량
    """
    idx: Any
    lines: List[str]
    times: List[int]
    qty: float

# 할당 결과 모델
type PreAssignSolution = Dict[Any, List[Tuple[str, int, float]]]
type PreAssignFailures = Dict[Any, List[str]]
