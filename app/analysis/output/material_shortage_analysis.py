import pandas as pd
import numpy as np
import re
import os
from app.utils.fileHandler import load_file
from app.models.common.fileStore import FilePaths, DataStore

"""
자재 부족량 분석 클래스
결과 파일의 "Material Detail" 시트를 분석하여 자재 부족 모델과 Shift를 식별합니다.
"""
class MaterialShortageAnalyzer:

    def __init__(self):
        self.result_df = None          # 결과 데이터프레임 (result 시트)
        self.material_detail_df = None # 자재 부족 정보 데이터프레임 (Material Detail 시트)
        self.shortage_results = {}     # 분석 결과 저장소: {item_code: [{shift, material, shortage}]}
        
    """
    필요한 데이터 로드
    """   
    def load_data(self, result_data=None):
        try:
            # 결과 데이터 직접 전달 시 사용
            if result_data is not None:
                self.result_df = result_data
            
            # Material Detail 시트 별도 로드 시도
            self._load_material_detail()
            
            # 데이터 유효성 검증
            if self.result_df is None or self.material_detail_df is None:
                return False
                
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    """
    Material Detail 시트 로드 및 처리
    """
    def _load_material_detail(self):
        try:
            # 결과 파일 경로 가져오기
            result_path = FilePaths.get("result_file")
            
            if result_path and os.path.exists(result_path):
                # 모든 시트 이름 가져오기
                try:
                    xl = pd.ExcelFile(result_path)
                    sheet_names = xl.sheet_names
                    
                    # 'material_detail'과 유사한 시트 찾기
                    material_detail_sheet = None
                    
                    # 1. 정확한 매칭 시도
                    for sheet in sheet_names:
                        normalized_sheet = sheet.lower().replace(" ", "").replace("_", "")
                        if normalized_sheet == 'materialdetail':
                            material_detail_sheet = sheet
                            break
                    
                    # 2. 부분 매칭 시도
                    if not material_detail_sheet:
                        for sheet in sheet_names:
                            normalized_sheet = sheet.lower()
                            if 'material' in normalized_sheet and ('detail' in normalized_sheet or 'dtl' in normalized_sheet):
                                material_detail_sheet = sheet
                                break
                    
                    # 3. 시트 순서로 시도
                    if not material_detail_sheet and len(sheet_names) > 1:
                        material_detail_sheet = sheet_names[1]  # 두 번째 시트 선택
                    
                    if material_detail_sheet:
                        # 찾은 시트 로드
                        self.material_detail_df = pd.read_excel(result_path, sheet_name=material_detail_sheet)
                    else:
                        # 4. 모든 시트를 로드해보고 적합한 시트 찾기
                        for sheet in sheet_names:
                            try:
                                temp_df = pd.read_excel(result_path, sheet_name=sheet)
                                
                                # 'index'와 'Items' 컬럼이 있거나 유사한 컬럼이 있는지 확인
                                cols = [col.lower() for col in temp_df.columns]
                                if any('index' in col or 'material' in col for col in cols) and any('item' in col for col in cols):
                                    self.material_detail_df = temp_df
                                    break
                            except Exception:
                                pass
                except Exception:
                    pass
                    
            else:
                # DataStore에서 시도
                stored_dataframes = DataStore.get("simplified_dataframes", {})
                
                for path, data in stored_dataframes.items():
                    if isinstance(data, dict):
                        # 정확한 키 이름으로 먼저 시도
                        material_detail_key = None
                        for key in data.keys():
                            normalized_key = key.lower().replace(" ", "").replace("_", "")
                            if normalized_key == 'materialdetail':
                                material_detail_key = key
                                break
                        
                        # 부분 일치로 시도
                        if not material_detail_key:
                            for key in data.keys():
                                key_lower = key.lower()
                                if 'material' in key_lower and ('detail' in key_lower or 'dtl' in key_lower):
                                    material_detail_key = key
                                    break
                        
                        if material_detail_key:
                            self.material_detail_df = data[material_detail_key]
                            break
            
            # 데이터프레임 전처리
            if self.material_detail_df is not None:
                self._preprocess_material_detail()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    """
    Material Detail 데이터프레임 전처리
    """
    def _preprocess_material_detail(self):
        if self.material_detail_df is None:
            return
            
        # 자재 코드를 담는 인덱스 컬럼 찾기
        index_col = None
        for col in self.material_detail_df.columns:
            if col.lower() == 'index' or 'material' in col.lower():
                index_col = col
                break
        
        if index_col is None:
            # 첫 번째 컬럼을 인덱스로 사용
            index_col = self.material_detail_df.columns[0]
        
        # Shift 컬럼 확인 (1-14)
        shift_cols = []
        for i in range(1, 15):
            shift_col = str(i)
            if shift_col in self.material_detail_df.columns:
                shift_cols.append(shift_col)
        
        if not shift_cols:
            # 수치형 컬럼을 시프트로 가정
            for col in self.material_detail_df.columns:
                if col != index_col and self.material_detail_df[col].dtype in (np.int64, np.float64):
                    shift_cols.append(col)
        
        # Items 컬럼 확인
        items_col = None
        for col in self.material_detail_df.columns:
            if 'items' in col.lower() or 'model' in col.lower() or 'product' in col.lower():
                items_col = col
                break
        
        if items_col is None:
            # 마지막 컬럼을 Items로 사용
            items_col = self.material_detail_df.columns[-1]
        
        # 데이터프레임 컬럼 이름 표준화
        col_mapping = {index_col: 'index'}
        
        # Shift 컬럼 매핑 유지
        for shift_col in shift_cols:
            col_mapping[shift_col] = shift_col
        
        # Items 컬럼 매핑
        col_mapping[items_col] = 'Items'
        
        # 필요한 컬럼만 선택하고 이름 변경
        self.material_detail_df = self.material_detail_df.rename(columns=col_mapping)
        selected_cols = ['index'] + shift_cols + ['Items']
        
        # 존재하는 컬럼만 선택
        existing_cols = [col for col in selected_cols if col in self.material_detail_df.columns]
        self.material_detail_df = self.material_detail_df[existing_cols]
        
        # index 컬럼을 문자열로 변환
        if 'index' in self.material_detail_df.columns:
            self.material_detail_df['index'] = self.material_detail_df['index'].astype(str)
            
        # Items 컬럼이 문자열 리스트인지 확인하고 변환
        if 'Items' in self.material_detail_df.columns:
            try:
                # 문자열 리스트일 경우
                self.material_detail_df['Items'] = self.material_detail_df['Items'].apply(
                    lambda x: eval(x) if isinstance(x, str) and ('[' in x or "'" in x) else 
                            [x] if isinstance(x, str) else 
                            x if isinstance(x, list) else []
                )
            except Exception:
                # 단순 문자열일 경우 쉼표로 구분하여 리스트로 변환 시도
                try:
                    self.material_detail_df['Items'] = self.material_detail_df['Items'].apply(
                        lambda x: x.split(',') if isinstance(x, str) else 
                                [x] if not isinstance(x, list) and not pd.isna(x) else 
                                [] if pd.isna(x) else x
                    )
                except Exception:
                    # 마지막 대안으로 빈 리스트로 설정
                    self.material_detail_df['Items'] = [[]] * len(self.material_detail_df)
    
    """
    자재 부족량 분석 실행
    """
    def analyze_material_shortage(self, result_data=None):
        # 데이터 로드 시도
        data_loaded = self.load_data(result_data)
        
        if not data_loaded:
            return {}
        
        # 결과 저장할 딕셔너리
        shortage_results = {}
        
        # Material Detail 시트에서 부족한 자재 찾기
        if self.material_detail_df is not None:
            if self.result_df is None:
                return {}
                
            # 'Time'과 'Item' 컬럼 확인
            if 'Time' not in self.result_df.columns or 'Item' not in self.result_df.columns:
                return {}
            
            # 각 행(자재)에 대해 순회
            for idx, row in self.material_detail_df.iterrows():
                material_code = row.get('index')
                items_list = row.get('Items', [])
                
                if not isinstance(items_list, list):
                    items_list = [items_list] if not pd.isna(items_list) else []
                
                if not items_list:
                    continue
                
                # 시프트 컬럼들(1-14) 확인
                for shift in range(1, 15):
                    shift_str = str(shift)
                    
                    # 해당 Shift 컬럼이 있는지 확인
                    if shift_str not in row:
                        continue
                        
                    shortage_amt = row.get(shift_str, 0)
                    
                    # 부족한 수량이 음수(결손)인 경우
                    if pd.notna(shortage_amt) and isinstance(shortage_amt, (int, float)) and shortage_amt < 0:
                        # 해당 자재를 사용하는 모든 아이템에 대해
                        for item in items_list:
                            # 빈 문자열이나 None인 경우 건너뛰기
                            if not item or pd.isna(item):
                                continue
                                
                            item = str(item).strip()  # 모델 코드 문자열로 변환 및 공백 제거
                            
                            # 해당 아이템과 Shift에 매칭되는 행이 result_df에 있는지 확인
                            matching_rows = self.result_df[
                                (self.result_df['Item'] == item) & 
                                (self.result_df['Time'] == int(shift))
                            ]
                            
                            # 매칭되는 행이 있으면 부족 정보 저장
                            if not matching_rows.empty:
                                # 아이템 코드로 항목 초기화 (없으면)
                                if item not in shortage_results:
                                    shortage_results[item] = []
                                
                                # 부족 정보 저장
                                shortage_info = {
                                    'shift': int(shift),
                                    'material': material_code,
                                    'shortage': abs(shortage_amt)  # 절대값으로 변환
                                }
                                
                                # 중복 추가 방지
                                if shortage_info not in shortage_results[item]:
                                    shortage_results[item].append(shortage_info)
        
        # 결과 저장
        self.shortage_results = shortage_results
        
        return shortage_results

    """
    자재 부족이 있는 아이템 목록 반환
    """
    def get_shortage_items(self):
        return list(self.shortage_results.keys())
    
    """
    특정 아이템의 자재 부족 세부 정보 반환
    """
    def get_item_shortages(self, item_code):
        return self.shortage_results.get(item_code, [])
    
    """
    모든 부족 데이터를 테이블 형식으로 반환
    """
    def get_all_shortage_data(self):
        result_rows = []
        
        # 부족이 발생한 모델 및 자재 정보 추가
        for item, shortages in self.shortage_results.items():
            for shortage in shortages:
                result_rows.append({
                    'Material': shortage.get('material', 'Unknown'),
                    'Item': item,
                    'Shortage': shortage.get('shortage', 0),
                    'Shift': shortage.get('shift', 0)
                })
        
        # 데이터프레임 변환 및 정렬
        df = pd.DataFrame(result_rows)
        if not df.empty:
            # Material로 정렬한 후 Item으로 정렬
            df = df.sort_values(['Material', 'Item'])
        
        return df
        
    """
    차트 표시용 형식의 데이터 가져오기
    """
    def get_shortage_chart_data(self):
        if not self.shortage_results:
            return {}
            
        # 아이템별 부족률 계산
        item_shortage_pct = {}
        
        for item, shortages in self.shortage_results.items():
            # 이 아이템이 Result 데이터에 있는지 확인
            if self.result_df is not None:
                item_rows = self.result_df[self.result_df['Item'] == item]
                
                if not item_rows.empty and 'Qty' in item_rows.columns:
                    # 전체 필요 수량 (모든 시프트 합)
                    total_qty = item_rows['Qty'].sum()
                    
                    # 총 부족 자재 개수
                    shortage_count = len(shortages)
                    
                    # 부족률 계산
                    if total_qty > 0:
                        shortage_pct = min(100, (shortage_count / total_qty) * 100)
                    else:
                        shortage_pct = 0
                else:
                    # 수량 정보가 없는 경우 부족 자재 개수로 점수 부여
                    shortage_pct = min(100, len(shortages) * 20)
            else:
                # Result 데이터가 없는 경우 부족 자재 개수로 점수 부여
                shortage_pct = min(100, len(shortages) * 20)
            
            item_shortage_pct[item] = shortage_pct
        
        return item_shortage_pct