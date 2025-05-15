import pandas as pd
import os
from app.models.common.file_store import FilePaths
from app.models.common.project_grouping import ProjectGroupManager

"""
파일 유형 감지하는 함수
"""
def detect_file_type(file_path):
    if not file_path:
        return 'unknown'
    
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext in ['.xlsx', '.xls', '.xlsm']:
        return 'excel'
    elif file_ext == '.csv':
        return 'csv'
    else :
        return 'unknown'

"""
파일의 시트를 로드하는 함수
"""
def load_file(file_path, sheet_name=None, **kwargs) :
    try:
        if not os.path.exists(file_path):
            print(f"파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame() if sheet_name is not None and not isinstance(sheet_name, list) else {}
        
        file_type = detect_file_type(file_path)

        if file_type == 'excel':
            return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        elif file_type == 'csv':
            df = pd.read_excel(file_path, **kwargs)

            if sheet_name is None or isinstance(sheet_name, list):
                return {"Sheet1": df}
            return df
        else:
            print(f"지원되지 않는 파일 형식입니다: {file_path}")
            return pd.DataFrame() if sheet_name is not None and not isinstance(sheet_name, list) else {}

    except Exception as e :
        print(f"엑셀 파일 시트 로드 중 오류 발생: {e}")
        return pd.DataFrame() if sheet_name is not None and not isinstance(sheet_name, list) else {}
    
"""
엑셀 파일의 이름 목록을 반환하는 함수
"""
def get_sheet_names(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"파일이 존재하지 않습니다: {file_path}")
            return []
        
        file_type = detect_file_type(file_path)

        if file_type != 'excel':
            print(f"시트 이름 확인은 엑셀 파일만 지원합니다: {file_path}")
            return []
        
        xlsx = pd.ExcelFile(file_path)

        return xlsx.sheet_names
    except Exception as e:
        print(f"시트 이름 목록 가져오기 중 오류 발생: {e}")
        return []

"""
프로젝트 그룹화
"""
def create_from_master():
    path = FilePaths.get('master_excel_file')

    if not path:
        raise FileNotFoundError("master_excel_file 경로가 설정되어 있지 않습니다.")
    
    df = pd.read_excel(path, sheet_name='line_available')
    
    return ProjectGroupManager.create_project_groups(df)