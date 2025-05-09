import pandas as pd
import numpy as np
import re
import os
from app.models.common.fileStore import FilePaths, DataStore

"""자재 부족량 분석 클래스

결과 파일과 동적 파일을 분석하여 자재 부족 모델을 식별합니다.
"""
class MaterialShortageAnalyzer:

    def __init__(self):
        self.result_df = None          # 최적화 결과 데이터프레임
        self.demand_df = None          # 수요 데이터프레임
        self.material_item_df = None   # 자재-모델 매핑 데이터프레임
        self.material_qty_df = None    # 자재 수량 데이터프레임
        self.material_equal_df = None  # 공용자재 데이터프레임
        
        self.shortage_results = {}     # 분석 결과 저장소

    """필요한 데이터 로드
    
    Args:
        result_data: 직접 전달된 결과 데이터프레임 (선택적)
    """   
    def load_data(self, result_data=None):

        try:
            # 직접 전달된 데이터 로드
            if result_data is not None:
                self.result_df = result_data
                print("직접 제공된 결과 데이터 사용")
            
            # 여러 소스에서 데이터 로드 시도
            self._load_from_multiple_sources()
            
            # 데이터 유효성 검증
            if self.result_df is None or self.material_item_df is None or self.material_qty_df is None:
                # print("필요한 데이터를 로드하지 못했습니다. 누락된 데이터:")
                # print(f"- 결과 데이터: {'로드됨' if self.result_df is not None else '누락됨'}")
                # print(f"- 자재-모델 데이터: {'로드됨' if self.material_item_df is not None else '누락됨'}")
                # print(f"- 자재-수량 데이터: {'로드됨' if self.material_qty_df is not None else '누락됨'}")
                return False
                
            # 데이터프레임 전처리
            self._preprocess_data()
            # print("자재 부족량 분석을 위한 데이터 로드 성공")
            return True
            
        except Exception as e:
            print(f"데이터 로드 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    """여러 방법을 시도하여 필요한 데이터 로드"""
    def _load_from_multiple_sources(self):
        # 1. 먼저 DataStore에서 직접 시도
        self._try_load_from_datastore()
        
        # 2. 아직 데이터가 누락된 경우 파일 경로 시도
        if self.result_df is None or self.material_item_df is None or self.material_qty_df is None:
            self._try_load_from_filepaths()
        
        # 3. 구조화된 데이터프레임 구조 시도
        if self.result_df is None or self.material_item_df is None or self.material_qty_df is None:
            self._try_load_from_organized_dataframes()
    
    """DataStore에서 직접 로드 시도"""
    def _try_load_from_datastore(self):
        # print("DataStore에서 로드 시도 중...")
        
        # 저장된 모든 데이터프레임 가져오기
        stored_dataframes = DataStore.get("simplified_dataframes", {})
        
        # 내용으로 결과, 수요, 동적 파일 식별 시도
        for path, data in stored_dataframes.items():
            if isinstance(data, dict):
                # 결과 데이터 확인
                if 'result' in data and self.result_df is None:
                    self.result_df = data['result']
                    # print(f"{path}에서 결과 데이터 찾음")
                
                # 자재 데이터 확인
                if 'material_item' in data and self.material_item_df is None:
                    self.material_item_df = data['material_item']
                    # print(f"{path}에서 material_item 데이터 찾음")
                
                if 'material_qty' in data and self.material_qty_df is None:
                    self.material_qty_df = data['material_qty']
                    # print(f"{path}에서 material_qty 데이터 찾음")
                
                if 'material_equal' in data and self.material_equal_df is None:
                    self.material_equal_df = data['material_equal']
                    # print(f"{path}에서 material_equal 데이터 찾음")
            
            # 직접 데이터프레임 확인
            elif isinstance(data, pd.DataFrame):
                # 열 이름으로 타입 결정 시도
                columns = data.columns.tolist()
                
                # 결과 데이터 식별 (Line, Time, Item 열이 있어야 함)
                if all(col in columns for col in ['Line', 'Time', 'Item']) and self.result_df is None:
                    self.result_df = data
                    # print(f"{path}에서 결과 데이터 식별됨")
    
    """FilePaths에서 로드 시도"""
    def _try_load_from_filepaths(self):
        # print("FilePaths에서 로드 시도 중...")
        
        # 데이터 로드 경로 확인
        result_path = FilePaths.get("result_file")
        dynamic_path = FilePaths.get("dynamic_excel_file")
        
        # print(f"파일 경로 발견: result={result_path}, dynamic={dynamic_path}")
        
        # 아직 로드되지 않은 경우 결과 데이터 로드
        if self.result_df is None and result_path and os.path.exists(result_path):
            try:
                self.result_df = pd.read_excel(result_path, sheet_name='result')
                print(f"{result_path}에서 결과 데이터 로드함")
            except Exception as e:
                print(f"결과 데이터 로드 오류: {str(e)}")
        
        # 아직 로드되지 않은 경우 동적 데이터 로드
        if (self.material_item_df is None or self.material_qty_df is None) and dynamic_path and os.path.exists(dynamic_path):
            try:
                # material_item 시트 로드
                if self.material_item_df is None:
                    self.material_item_df = pd.read_excel(dynamic_path, sheet_name='material_item')
                    # print(f"{dynamic_path}에서 material_item 데이터 로드함")
                
                # material_qty 시트 로드
                if self.material_qty_df is None:
                    self.material_qty_df = pd.read_excel(dynamic_path, sheet_name='material_qty')
                    # print(f"{dynamic_path}에서 material_qty 데이터 로드함")
                
                # material_equal 시트 로드 시도
                if self.material_equal_df is None:
                    try:
                        self.material_equal_df = pd.read_excel(dynamic_path, sheet_name='material_equal')
                        # print(f"{dynamic_path}에서 material_equal 데이터 로드함")
                    except:
                        # print(f"{dynamic_path}에서 material_equal 시트를 찾을 수 없음")
                        self.material_equal_df = pd.DataFrame()
            except Exception as e:
                print(f"동적 데이터 로드 오류: {str(e)}")
    
    """organized_dataframes 구조에서 로드 시도"""
    def _try_load_from_organized_dataframes(self):
        # print("organized_dataframes에서 로드 시도 중...")
        
        organized_dataframes = DataStore.get("organized_dataframes", {})
        
        # 결과 데이터 로드 시도
        if self.result_df is None and "result" in organized_dataframes:
            result_data = organized_dataframes["result"]
            # 시트 딕셔너리인지 직접 데이터프레임인지 확인
            if isinstance(result_data, dict):
                for sheet_name, df in result_data.items():
                    self.result_df = df
                    # print(f"organized_dataframes[result][{sheet_name}]에서 결과 데이터 로드함")
                    break
            else:
                self.result_df = result_data
                # print("organized_dataframes[result]에서 결과 데이터 로드함")
        
        # 동적 데이터 로드 시도
        if (self.material_item_df is None or self.material_qty_df is None) and "dynamic" in organized_dataframes:
            dynamic_data = organized_dataframes["dynamic"]
            # 시트 딕셔너리인지 확인
            if isinstance(dynamic_data, dict):
                # material_item 시트 로드
                if self.material_item_df is None and "material_item" in dynamic_data:
                    self.material_item_df = dynamic_data["material_item"]
                    # print("organized_dataframes[dynamic][material_item]에서 material_item 데이터 로드함")
                
                # material_qty 시트 로드
                if self.material_qty_df is None and "material_qty" in dynamic_data:
                    self.material_qty_df = dynamic_data["material_qty"]
                    # print("organized_dataframes[dynamic][material_qty]에서 material_qty 데이터 로드함")
                
                # material_equal 시트 로드
                if self.material_equal_df is None and "material_equal" in dynamic_data:
                    self.material_equal_df = dynamic_data["material_equal"]
                    # print("organized_dataframes[dynamic][material_equal]에서 material_equal 데이터 로드함")

    """데이터프레임 전처리"""       
    def _preprocess_data(self):
        # print("\n=== 전처리 시작 ===")
        
        # Active_OX가 'X'인 자재 제외 (관리 대상 아님)
        if self.material_item_df is not None:
            # print(f"material_item_df 전처리 전 크기: {self.material_item_df.shape}")
            
            if 'Active_OX' in self.material_item_df.columns:
                excluded_count = (self.material_item_df['Active_OX'] == 'X').sum()
                self.material_item_df = self.material_item_df[self.material_item_df['Active_OX'] != 'X']
                print(f"Active_OX가 'X'인 {excluded_count}개 행 제외됨")
            
            # print(f"material_item_df 전처리 후 크기: {self.material_item_df.shape}")
            
            # # Top_Model_* 컬럼들을 하나로 통합
            # 컬럼 이름 확인 먼저 진행
            all_columns = list(self.material_item_df.columns)
            # print(f"전체 컬럼 목록: {all_columns}")
            
            # Top_Model 관련 컬럼 찾기
            top_model_columns = [col for col in all_columns if col.startswith('Top_Model_')]
            # print(f"Top_Model 관련 컬럼: {top_model_columns}")
            
            if top_model_columns:
                # Top_Model_* 컬럼들을 하나의 통합된 'Top_Model' 컬럼으로 만들기
                # 각 행에서 비어있지 않은 첫 번째 값을 사용
                def get_first_non_null(row):
                    for col in top_model_columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            return str(row[col]).strip()
                    return None
                
                self.material_item_df['Top_Model'] = self.material_item_df.apply(get_first_non_null, axis=1)
                # print(f"Top_Model 컬럼 생성 완료")
                
                # 원래 Top_Model_* 컬럼들은 제거하지 않음 (나중에 필요할 수 있음)
            else:
                print("Top_Model 관련 컬럼을 찾을 수 없음")
            
            # Top Model 컬럼의 값들 분포 확인
            # if 'Top_Model' in self.material_item_df.columns:
            #     print("\nTop Model 값 분포:")
            #     print(f"  - 전체: {len(self.material_item_df)}")
            #     print(f"  - Non-null: {self.material_item_df['Top_Model'].notna().sum()}")
            #     print(f"  - 문자열 타입: {sum(isinstance(x, str) for x in self.material_item_df['Top_Model'])}")
                
                # # 샘플 값 출력
                # print("\nTop_Model 샘플 값 (처음 10개):")
                # for i, val in enumerate(self.material_item_df['Top_Model'].dropna().head(10)):
                #     print(f"  {i+1}. {val}")
        
        # material_qty_df도 동일하게 전처리
        if self.material_qty_df is not None:
            print(f"\nmaterial_qty_df 전처리 전 크기: {self.material_qty_df.shape}")
            
            if 'Active_OX' in self.material_qty_df.columns:
                excluded_count = (self.material_qty_df['Active_OX'] == 'X').sum()
                self.material_qty_df = self.material_qty_df[self.material_qty_df['Active_OX'] != 'X']
                # print(f"Active_OX가 'X'인 {excluded_count}개 행 제외됨")
            
            # print(f"material_qty_df 전처리 후 크기: {self.material_qty_df.shape}")
        
        # print("=== 전처리 완료 ===\n")
    
    """아이템 코드와 일치하는 자재 목록 찾기 (벡터화된 패턴 매칭)"""
    def _find_matching_materials(self, item_code):
        if self.material_item_df is None or 'Top_Model' not in self.material_item_df.columns:
            return []
        
        # print(f"\n=== 아이템 코드 매칭 시작: {item_code} ===")
        
        matched_materials = []
        
        # 데이터프레임 상태 확인
        # print(f"material_item_df 크기: {self.material_item_df.shape}")
        # print(f"Top_Model 컬럼의 non-null 값 개수: {self.material_item_df['Top_Model'].notna().sum()}")
        
        # 모든 패턴 확인 및 디버깅
        # print("\nmaterial_item_df의 패턴 목록 (상위 20개):")
        count = 0
        for idx, row in self.material_item_df.iterrows():
            if pd.notna(row['Top_Model']) and count < 20:
                # print(f"  {count+1}. 패턴: '{row['Top_Model']}' -> 자재: {row['Material']}")
                count += 1
        
        # print("\n매칭 시도 중...")
        
        # 모든 패턴 확인
        for idx, row in self.material_item_df.iterrows():
            if pd.isna(row['Top_Model']) or not isinstance(row['Top_Model'], str):
                continue
                
            pattern = row['Top_Model'].strip()
            material = row['Material']
            
            # 정확한 매치 먼저 시도
            if pattern.upper() == item_code.upper():
                # print(f"  ✓ 정확한 매치 발견: {pattern} == {item_code} -> 자재: {material}")
                matched_materials.append(material)
                continue
            
            # 와일드카드 패턴 매치
            if '*' in pattern:
                # 패턴에 공백이나 특수 문자가 있는지 확인
                # print(f"  시도 중: 패턴 '{pattern}' vs 아이템 '{item_code}'")
                
                # 패턴을 정규식으로 변환
                # 예: "AB*P495WZJ*" -> "^AB.*P495WZJ.*$"
                regex_pattern = re.escape(pattern).replace(r'\*', '.*')
                regex_pattern = f"^{regex_pattern}$"
                
                # print(f"    변환된 정규식: '{regex_pattern}'")
                
                try:
                    is_match = re.match(regex_pattern, item_code, re.IGNORECASE)
                    if is_match:
                        # print(f"  ✓ 와일드카드 매치 발견: {pattern} matches {item_code} -> 자재: {material}")
                        matched_materials.append(material)
                    # else:
                    #     print(f"  ✗ 매치 실패: {pattern} ≠ {item_code}")
                    #     # 왜 매칭이 안되는지 더 자세히 분석
                    #     if pattern.startswith('AB') and item_code.startswith('AB'):
                    #         print(f"    패턴 문자들: {list(pattern)}")
                    #         print(f"    아이템 문자들: {list(item_code)}")
                except re.error as e:
                    print(f"  ! 정규식 오류: {e} (패턴: {pattern})")
                    import traceback
                    traceback.print_exc()
        
        # print(f"최종 매칭 결과: {matched_materials}")
        # print("=" * 60)
        return matched_materials
    
    """자재의 총 가용량 계산 (재고 + 2주간 입출고량)"""
    def _calculate_material_availability(self, material_code):
        if self.material_qty_df is None:
            print(f"material_qty_df가 없음 - {material_code}")
            return 0
            
        # 해당 자재 찾기
        material_row = self.material_qty_df[self.material_qty_df['Material'] == material_code]
        
        if material_row.empty:
            # print(f"자재 {material_code}를 찾을 수 없음")
            return 0
            
        # print(f"\n=== 자재 {material_code} 가용량 계산 ===")
        
        # 재고량(On-Hand) + 2주간 입출고량
        availability = 0
        
        # On-Hand 값 추가
        if 'On-Hand' in material_row.columns:
            on_hand = material_row['On-Hand'].iloc[0]
            if pd.notna(on_hand):
                availability += on_hand
                # print(f"On-Hand: {on_hand}")
        else:
            print("On-Hand 컬럼이 없음")
                
        # 날짜 형식 열인지 확인하는 정규식 패턴 (예: 4/7(월), 4/8(화) 등)
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        
        # 정해진 날짜 수 (2주 = 14일)
        days_to_include = 14
        day_count = 0
        daily_total = 0
        
        # 모든 열에 대해 날짜 패턴 확인 및 값 합산
        for col in material_row.columns:
            # 날짜 형식인지 확인
            if date_pattern.match(str(col)):
                day_count += 1
                
                # 지정된 날짜 수 내에서만 계산
                if day_count <= days_to_include:
                    value = material_row[col].iloc[0]
                    if pd.notna(value):
                        daily_total += value
                        # print(f"  {col}: {value}")
                else:
                    # 지정된 날짜 수를 초과하면 중단
                    break
        
        availability += daily_total
        # print(f"총 일별 입출고 합계 (2주간): {daily_total}")
        # print(f"자재 {material_code} 총 가용량: {availability}")
        # print("===============================\n")
                
        return availability

    """자재 부족량 분석 실행
    
    Args:
        result_data: 직접 전달된 결과 데이터프레임 (선택적)
    
    Returns:
        자재 부족 결과를 담은 딕셔너리
    """
    def analyze_material_shortage(self, result_data=None):
        if not self.load_data(result_data):
            print("데이터 로드 실패, 자재 부족량 분석을 수행할 수 없습니다.")
            return {}
        
        # 결과 저장할 딕셔너리
        shortage_results = {}
        
        # 아이템별 MFG 합계 계산 (결과 파일 기준)
        item_mfg = {}
        
        # 결과 파일에서 MFG 추출
        if self.result_df is not None and 'Item' in self.result_df.columns:
            # print(f"결과 파일에서 아이템별 MFG 총합 계산 중 (총 {len(self.result_df)} 행)...")
            
            # MFG 컬럼 확인 및 사용
            if 'MFG' in self.result_df.columns:
                # print("MFG 컬럼 발견 - MFG 컬럼을 사용하여 필요량 계산")
                
                # 모든 아이템에 대한 MFG 총합 계산
                mfg_sums = self.result_df.groupby('Item')['MFG'].sum().to_dict()
                item_mfg = mfg_sums
                
            else:
                # print("결과 파일에서 'MFG' 컬럼을 찾을 수 없습니다.")
                return {}
                
            # print(f"\n아이템별 MFG 총합 계산 완료. 총 {len(item_mfg)}개 아이템")
        else:
            # print("결과 파일에서 'Item' 컬럼을 찾을 수 없습니다.")
            return {}
                    
        # 모든 아이템에 대해 자재 부족 체크
        for item, mfg_total in item_mfg.items():
            # 해당 아이템에 사용되는 자재 목록 찾기
            materials = self._find_matching_materials(item)
            
            item_shortages = []
            
            for material in materials:
                # 자재 가용량 계산
                availability = self._calculate_material_availability(material)
                
                # 부족량 계산 (필요량 - 가용량)
                shortage = mfg_total - availability
                
                # 부족한 경우 결과에 추가
                if shortage > 0:
                    item_shortages.append({
                        'Material': material,
                        'Required': mfg_total,
                        'Available': availability,
                        'Shortage': shortage
                    })
            
            # 부족한 자재가 있으면 해당 아이템을 결과에 추가
            if item_shortages:
                shortage_results[item] = item_shortages
        
        # 결과 저장
        self.shortage_results = shortage_results
        
        # 요약 출력
        if shortage_results:
            print(f"\n자재 부족 모델 {len(shortage_results)}개 발견")
            print("\n=== 자재 부족 요약 ===")
            for item, shortages in shortage_results.items():
                print(f"\n아이템: {item}")
                for shortage in shortages:
                    print(f"  - 자재: {shortage['Material']}")
                    print(f"    * 필요량(MFG 총합): {shortage['Required']:,}")
                    print(f"    * 가용량: {shortage['Available']:,}")
                    print(f"    * 부족량: {shortage['Shortage']:,}")
        else:
            print("자재 부족 모델 없음")
            
        return shortage_results

    def get_shortage_items(self):
        """자재 부족이 있는 아이템 목록 반환"""
        return list(self.shortage_results.keys())
    
    def get_item_shortages(self, item_code):
        """특정 아이템의 자재 부족 세부 정보 반환"""
        return self.shortage_results.get(item_code, [])
    
    def get_all_shortage_data(self):
        """모든 부족 데이터를 테이블 형식으로 반환"""
        result_rows = []
        
        for item, shortages in self.shortage_results.items():
            for shortage in shortages:
                result_rows.append({
                    'Item': item,
                    'Material': shortage['Material'],
                    'Required': shortage['Required'],
                    'Available': shortage['Available'],
                    'Shortage': shortage['Shortage']
                })
        
        return pd.DataFrame(result_rows)
    
    def get_shortage_chart_data(self):
        """차트 표시용 형식의 데이터 가져오기"""
        if not self.shortage_results:
            return {}
            
        # 아이템별 부족률 계산
        item_shortage_pct = {}
        
        for item, shortages in self.shortage_results.items():
            max_shortage_pct = 0
            
            for shortage in shortages:
                required = shortage['Required']
                shortage_amt = shortage['Shortage']
                
                if required > 0:
                    shortage_pct = (shortage_amt / required) * 100
                    max_shortage_pct = max(max_shortage_pct, shortage_pct)
            
            item_shortage_pct[item] = max_shortage_pct
        
        return item_shortage_pct