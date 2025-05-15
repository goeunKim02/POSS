import os
import pandas as pd
from app.models.common.file_store import DataStore, FilePaths
from app.analysis.output.capa_ratio import CapaRatioAnalyzer
from app.utils.conversion import convert_value

"""
결과 조정 시 제약사항 점검 클래스

- 라인과 아이템 호환성
- 라인 시프트별 용량 제약
- 납기일 준수 여부
- 요일별 가동률 제약
- 제조동 비율 제약
"""
class PlanAdjustmentValidator:
    """
    validator 초기화
    
    Args:
        result_data (DataFrame): 현재 생산 계획 결과 데이터
    """
    def __init__(self, result_data):
        self.result_data = result_data

         # 1. 먼저 DataStore에서 organized_dataframes 조회
        organized = DataStore.get("organized_dataframes", {})

        # 2. master 데이터 로딩
        self.master_data = organized.get("master", {})
        if not self.master_data:  # 없으면 FilePaths로 시도
            master_path = FilePaths.get("master_excel_file")
            if master_path and os.path.exists(master_path):
                try:
                    self.master_data = {
                        "capa_qty": pd.read_excel(master_path, sheet_name="capa_qty"),
                        # 필요한 시트가 더 있다면 여기에 추가
                    }
                    print(f"[로드] master 파일에서 데이터 로드: {master_path}")
                except Exception as e:
                    print(f"[오류] master 파일 로드 실패: {e}")
            else:
                print(f"[경고] master 파일 경로가 유효하지 않음")

        # 3. demand 데이터 로딩
        self.demand_data = organized.get("demand", {})
        if not self.demand_data:
            demand_path = FilePaths.get("demand_excel_file")
            if demand_path and os.path.exists(demand_path):
                try:
                    self.demand_data = {
                        "demand": pd.read_excel(demand_path, sheet_name="demand"),
                    }
                    print(f"[로드] demand 파일에서 데이터 로드: {demand_path}")
                except Exception as e:
                    print(f"[오류] demand 파일 로드 실패: {e}")
            else:
                print(f"[경고] demand 파일 경로가 유효하지 않음")

        self.capa_qty_data = self.master_data.get("capa_qty", pd.DataFrame())

        # 제약사항 추출 및 캐싱
        self._extract_constraints()
        self._cache_reference_data()


    """
    마스터 데이터에서 각종 제약사항 추출하여 메모리에 캐싱

    - line_capacities: 라인 및 시프트별 용량
    - due_dates: 아이템/프로젝트별 납기일
    - building_constraints: 제조동별 상/하한 비율
    - line_item_compatibility: 라인-아이템 호환성
    """
    def _extract_constraints(self):
        # 초기화
        self.line_capacities = {}    # 라임 및 shift별 용량
        self.due_dates = {}          # 아이템/프로젝트별 납기일
        self.building_constraints = {}  # 제조동 제약
        self.line_item_compatibility = {}  # 라인-아이템 호환성

        # capa_qty 시트에서 라인 용량 추출
        if 'capa_qty' in self.master_data:
            df_capa_qty = self.master_data['capa_qty']
            for _, row in df_capa_qty.iterrows():
                if 'Line' in row:
                    line = row['Line']
                    self.line_capacities[line] = {}

                    # shift별 용량 추출
                    for col in df_capa_qty.columns:
                        if isinstance(col, (int, str)) and col not in ['Line', 'Capacity']:
                            try:
                                time = int(col) if isinstance(col, str) else col
                                self.line_capacities[line][time] = row[col]
                            except (ValueError, TypeError):
                                pass

        # line_available 시트에서 라인 가용성 추출
        if 'line_available' in self.master_data:
            df_line_available = self.master_data['line_available']
            for _, row in df_line_available.iterrows():
                if 'Project' in row:
                    project = row['Project']
                    self.line_item_compatibility[project] = []

                    for col in df_line_available.columns:
                        if col != 'Project' and row[col] == 1:
                            self.line_item_compatibility[project].append(col)

        # demand 시트에서 납기일 추출
        if 'demand' in self.demand_data:
            df_demand = self.demand_data['demand']
            for _, row in df_demand.iterrows():
                if 'Item' in row and 'Due_date_LT' in row:
                    item = row['Item']
                    due_date = row['Due_date_LT']
                    self.due_dates[item] = due_date

                # 프로젝트별 납기일 추출
                if 'Project' in row and 'Due_date_LT' in row:
                    project = row['Project']
                    due_date = row['Due_date_LT']
                    if project not in self.due_dates:
                        self.due_dates[project] = due_date

         # capa_portion 시트에서 제조동 비율 제약 추출
        if 'capa_portion' in self.master_data:
            df_portion = self.master_data['capa_portion']
            if not df_portion.empty and 'name' in df_portion.columns:
                for _, row in df_portion.iterrows():
                    if 'name' in row and 'lower_limit' in row and 'upper_limit' in row:
                        building = row['name']
                        self.building_constraints[building] = {
                            'lower_limit': convert_value(row['lower_limit'], float, 0.0),
                            'upper_limit': convert_value(row['upper_limit'], float, 0.0)
                        }


    """
    현재 결과 데이터에서 참조 정보 추출하여 캐싱
    - 라인별 시프트별 현재 할당량
    - 라인별 사용 가능한 아이템 목록
    """
    def _cache_reference_data(self):
        if self.result_data is None or self.result_data.empty:
            return
        
        # 라인별 시프트별 현재 할당량 계산
        self.line_shift_allocation = {}

        grouped_data = self.result_data.groupby(['Line', 'Time'])['Qty'].sum()
        self.line_shift_allocation = {f"{line}_{time}": qty for (line, time), qty in grouped_data.items()}
                
        # 라인별 사용 가능한 아이템 목록 캐싱
        self.line_available_items = self.result_data.groupby('Line')['Item'].apply(set).to_dict()
        

    """
    현재 결과 데이터를 capaValidator 형식으로 변환
    
    Returns:
        dict: capaValidator에 사용할 데이터 구조
    """
    def _prepare_data_for_validator(self):
        # 결과 데이터를 capaValidator 형식으로 변환
        processed_data = {
            'demand_items': [],
            'project_to_buildings': {},
            'building_constraints': self.building_constraints,
            'line_available_df': self.master_data.get('line_available', pd.DataFrame()),
            'capa_qty_df': self.master_data.get('capa_qty', pd.DataFrame())
        }

        # 결과 데이터를 demand_items 형식으로 변환
        for _, row in self.result_data.iterrows():
            item_dict = {
                'Item': row.get('Item', ''),
                'MFG': row.get('Qty', 0),
                'Project': row.get('Project', ''),
                'RMC': row.get('RMC', '')
            }

            # Item에서 Project, Basic2, Tosite_group 추출
            if 'Item' in item_dict and item_dict['Item']:
                item = item_dict['Item']
                if len(item) >= 7:
                    if not item_dict.get('Project'):
                        item_dict['Project'] = item[3:7]
                    item_dict['Basic2'] = item[3:8] if len(item) >= 8 else item[3:7]
                    item_dict['Tosite_group'] = item[7:8] if len(item) >= 8 else ''
                    item_dict['RMC'] = item[3:-3] if len(item) >= 7 else ''
            
            processed_data['demand_items'].append(item_dict)

        # project_to_buildings 설정 (프로젝트별 생산 가능 제조동)
        if 'line_available' in self.master_data:
            df_line_available = self.master_data['line_available']
            if not df_line_available.empty and 'Project' in df_line_available.columns:
                # 라인 코드에서 제조동 추출
                for _, row in df_line_available.iterrows():
                    project = row['Project']
                    project_buildings = []
                    
                    for col in df_line_available.columns:
                        if col != 'Project' and row[col] == 1 and len(col) > 0:
                            building = col[0]  # 라인 코드의 첫 글자 (예: 'I'_01 -> 'I')
                            if building not in project_buildings:
                                project_buildings.append(building)
                    
                    processed_data['project_to_buildings'][project] = project_buildings
                    
                    # Basic2 기반으로도 매핑
                    for item_dict in processed_data['demand_items']:
                        if 'Basic2' in item_dict and item_dict['Basic2'].startswith(project):
                            processed_data['project_to_buildings'][item_dict['Basic2']] = project_buildings
        
        return processed_data


    """
    라인과 아이템의 호환성 검증
    
    Args:
        line (str): 라인 코드
        item (str): 아이템 코드
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    def validate_line_item_compatibility(self, line, item):
        # 아이템 코드에서 프로젝트 추출 
        project = item[3:7] if len(item) >= 7 else ""
        
        # 마스터 데이터의 호환성 정보 확인
        if project in self.line_item_compatibility:
            compatible_lines = self.line_item_compatibility[project]
            if line not in compatible_lines:
                return False, f"Item '{item}' (Project {project}) cannot be produced on line '{line}'."
            return True, ""
        
        # 마스터 데이터가 없으면 결과 데이터에서 추론
        if line in self.line_available_items:
            # 이미 해당 라인에 할당된 적이 있는 아이템이면 호환 가능
            if item in self.line_available_items[line]:
                return True, ""
                
            # 아니라면 아이템 프로젝트 코드 비교 (추가 검증)
            for existing_item in self.line_available_items[line]:
                existing_project = existing_item[3:7] if len(existing_item) >= 7 else ""
                if project == existing_project:
                    # 같은 프로젝트의 아이템이 이미 있으면 호환 가능
                    return True, ""
        
        # 마스터 데이터도 없고 결과 데이터에서도 확인 불가능한 경우 기본 통과
        return True, ""
    
    
    """
    라인과 시프트의 용량 초과 여부 검증
    
    Args:
        line (str): 라인 코드
        time (int): 시프트 번호
        new_qty (int): 추가할 생산량
        item (str, optional): 아이템 코드 (이동인 경우)
        is_move (bool): 이동 여부 플래그
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    def validate_capacity(self, line, time, new_qty, item=None, is_move=False):
        # 라인-시프트 키 생성
        key = f"{line}_{time}"

        # 시프트의 현재 할당량 확인
        current_allocation = self.line_shift_allocation.get(key, 0)

        # 같은 위치에서 수량만 변경인 경우 기존 할당량 제외
        existing_qty = 0
        if not is_move and item:
            existing_mask = (
                (self.result_data['Line'] == line) &
                (self.result_data['Time'] == time) &
                (self.result_data['Item'] == item)
            )
            if existing_mask.any():
                existing_qty = self.result_data.loc[existing_mask, 'Qty'].iloc[0]
                current_allocation -= existing_qty
        
        # 이동인 경우 해당 아이템의 기존 할당량 제외
        if is_move and item:
            source_mask = (
                (self.result_data['Line'] == line) &
                (self.result_data['Time'] == time) &
                (self.result_data['Item'] == item)
            )
            if source_mask.any():
                current_allocation -= self.result_data.loc[source_mask, 'Qty'].iloc[0]
    
        # 마스터 데이터에서 라인과 시프트 용량 가져오기
        capacity = self.get_line_capacity(line, time)
        
        # 용량 검증
        if capacity is not None:
            if current_allocation + new_qty > capacity:
                return False, f"Exceeds capacity for line '{line}' shift {time} ({capacity}). Current: {current_allocation}, Adding: {new_qty}"
        
        return True, ""
    
    
    """
    납기일 준수 여부 검증
    
    Args:
        item (str): 아이템 코드
        time (int): 시프트 번호
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    def validate_due_date(self, item, time):
        # 아이템 또는 프로젝트의 납기일 확인
        due_time = None
        item_project = item[3:7] if len(item) >= 7 else ""
        
        # 직접 아이템에 대한 납기일 확인
        if item in self.due_dates:
            due_time = self.due_dates[item]
        # 프로젝트에 대한 납기일 확인
        elif item_project in self.due_dates:
            due_time = self.due_dates[item_project]
            
        # 납기일 검증
        if due_time is not None and time > due_time:
            return False, f"Item '{item}' exceeds due date (shift {due_time})."
            
        return True, ""
    
    
    """
    요일별/시프트별 가동률 제약 검증
    
    Args:
        line (str): 라인 코드
        time (int): 시프트 번호
        new_qty (int): 추가할 생산량
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    def validate_utilization_rate(self, line, time, item, new_qty):
        # 시프트별 최대 가동률 설정 
        max_utilization_by_shift = {
            1: 100, 2: 100, 3: 100,  4: 100,  5: 100,  6: 100,
            7: 100,  8: 100,  9: 100, 10: 100, 11: 100, 12: 100, 13: 100, 14: 100, 
        }

        # 1. 해당 라인/시프트의 전체 현재 할당량 가져오기 (이동하는 라인/시프트)
        current_total_allocation = self.get_current_allocation(line=line, time=time)

        # 2. 해당 아이템의 현재 위치에서의 기존 수량 (같은 아이템이 있을 수 있음.)
        existing_item_qty = self.get_item_qty_at_position(line, time, item)

        # 3. 라인 용량 조회 (이동하는 라인/시프트) 
        line_capacity = self.get_line_capacity(line, time)
        if line_capacity is None or line_capacity <= 0:
            return True, "용량 정보 없음"
    
        # 4. 새로운 총 할당량 계산
        new_total_allocation = current_total_allocation - existing_item_qty + new_qty
        
        # 5. 가동률 계산
        utilization_rate = (new_total_allocation / line_capacity) * 100
        
        # print(f"[DEBUG] 가동률 계산:")
        # print(f"  - 아이템: {item}")
        # print(f"  - 전체할당: {current_total_allocation}")
        # print(f"  - 기존수량: {existing_item_qty}")
        # print(f"  - 새수량: {new_qty}")
        # print(f"  - 새총할당: {new_total_allocation}")
        # print(f"  - 용량: {line_capacity}")
        # print(f"  - 가동률: {utilization_rate:.1f}%")
        
        # 6. 최대 가동률 검증
        max_rate = max_utilization_by_shift.get(int(time), 100)
        
        if utilization_rate > max_rate:
            return False, f"시프트 {time}의 최대 가동률 {max_rate}% 초과\n현재: {utilization_rate:.1f}%"
        
        return True, "가동률 제약 만족"


        # # 라인-시프트 키 생성
        # key = f"{line}_{time}"
        # current_allocation = self.line_shift_allocation.get(key, 0)
        
        # # 라인의 기본 용량 확인
        # line_capacity = None
        # if line in self.line_capacities and time in self.line_capacities[line]:
        #     line_capacity = self.line_capacities[line][time]

        # # 용량 정보가 없는 경우 처리
        # if line_capacity is None or line_capacity < 0:
        #     # 용량 정보가 없으면 다른 방법으로 제약 조건 확인 : 해당 라인/시프트의 capacity 값 직접 조회
        #     capacity = self.get_line_capacity(line, time)
        #     if capacity is not None and capacity >= 0:
        #         line_capacity = capacity
        #     else:
        #         # 용량 정보를 찾을 수 없는 경우
        #         print(f"경고: 라인 '{line}'의 시프트 {time}에 대한 용량 정보를 찾을 수 없습니다.")
        #         # 용량 정보가 없으면 제약 조건을 검증할 수 없으므로 통과
        #         return True, ""
    
        # adjusted_qty = new_qty - old_qty
        # print(f"adj : {adjusted_qty}")
        # new_total = current_allocation + adjusted_qty
        # print(f"new: {new_total}")
        # utilization_rate = (new_total / line_capacity) * 100 if line_capacity > 0 else 0
        # print(f"가동률 : {utilization_rate}")

        # # 해당 시프트의 최대 가동률 가져오기
        # max_rate = max_utilization_by_shift.get(time, 100)  # 기본값 100%
        
        # if utilization_rate > max_rate:
        #     return False, f"Maximum utilization rate for shift {time} exceeded ({max_rate}%).\nCurrent: {utilization_rate:.1f}%"
    
        # return True, ""
    
    

    """
    모든 검증 로직을 통합 실행 - 외부 호출용 메인 함수
    
    Args:
        line (str): 목표 라인 코드
        time (int/str): 목표 시프트 번호
        item (str): 아이템 코드
        new_qty (int/str): 새 생산량
        source_line (str, optional): 이동 시 원래 라인
        source_time (int/str, optional): 이동 시 원래 시프트
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    def validate_adjustment(self, line, time, item, new_qty, source_line=None, source_time=None):
        # 이동 여부 확인
        is_move = source_line is not None and source_time is not None

        # 기존 수량 조회 (현재 위치에서)
        old_qty = self.get_item_qty_at_position(line, time, item)
        print(f"[DEBUG] validate_adjustment: {item} at {line}-{time}, old_qty={old_qty}, new_qty={new_qty}, is_move={is_move}")

        # 타입 변환 (문자열 -> 숫자)
        time = convert_value(time, int, None)
        new_qty = convert_value(new_qty, int, 0, special_values={'ALL'})
        source_time = convert_value(source_time, int, None) if source_time is not None else None

        # 필수값 검증
        if line is None or time is None or item is None:
            return False, "라인, 시프트, 아이템 정보는 필수입니다."
        
        if new_qty == 'ALL' or new_qty == 'All':
            # 해당 아이템의 전체 수량 가져오기
            new_qty = self._get_total_demand_for_item(item)
            if new_qty <= 0:
                return False, f"아이템 '{item}'의 Qty를 찾을 수 없습니다."
            
        # 각 제약 요소 검증
        validations = [
            self.validate_line_item_compatibility(line, item),
            self.validate_capacity(line, time, new_qty, item, is_move),
            self.validate_due_date(item, time),
            self.validate_utilization_rate(line, time, item, new_qty)
        ]

        # 개별 검증 결과 확인
        for valid, message in validations:
            if not valid: 
                return False, message
        
        # 제조동 비율 제약조건 검증 (임시 데이터셋 생성 후 검증)
        temp_result_data = self._calculate_adjusted_data(line, time, item, new_qty, source_line, source_time)
        valid, message = self.validate_building_ratios(temp_result_data)
   
        if not valid:
            return False, message
        
        return True, "조정 가능합니다."

    
    """
    특정 라인과 시프트의 생산 용량을 반환
    
    Args:
        line (str): 라인 코드 
        time (int or str): 시프트 번호 
        
    Returns:
        int or None: 해당 라인과 시프트의 생산 용량, 없으면 None
    """
    def get_line_capacity(self, line, time):
        # 이미 캐싱된 capa_qty_data 사용
        if self.capa_qty_data is None or self.capa_qty_data.empty:
            print("capa_qty 데이터가 비어 있습니다.")
            return None

        try:
            # 라인이 인덱스에 있는 경우
            if 'Line' in self.capa_qty_data.columns and time in self.capa_qty_data.columns:
                line_rows = self.capa_qty_data[self.capa_qty_data['Line'] == line]
                if not line_rows.empty:
                    capacity = line_rows.iloc[0][time]
                    if pd.notna(capacity):
                        return float(capacity)
            
            # 제조동 제약 확인 (I, D, K, M)
            if len(line) >= 1:
                factory = line[0]  # 라인 코드의 첫 글자 (예: 'I'_01 -> 'I')
                
                # 최대 라인 수 제약
                max_line_rows = self.capa_qty_data[self.capa_qty_data['Line'] == f'Max_line_{factory}']
                if not max_line_rows.empty and time in max_line_rows.columns:
                    max_line = max_line_rows.iloc[0][time]
                    
                    # 해당 공장 라인들 가져오기
                    factory_lines = self.capa_qty_data[
                        self.capa_qty_data['Line'].str.startswith(f'{factory}_', na=False)
                    ]['Line'].tolist()

                    # 최대 라인 수 제약이 있고, 현재 라인이 해당 제약 내에 있는지 확인
                    if pd.notna(max_line) and factory_lines:
                        # 용량 기준으로 정렬
                        line_capacities = []
                        for l in factory_lines:
                            line_rows = self.capa_qty_data[self.capa_qty_data['Line'] == l]
                            if not line_rows.empty and time in line_rows.columns:
                                capacity = line_rows.iloc[0][time]
                                if pd.notna(capacity):
                                    line_capacities.append((l, float(capacity)))

                        line_capacities.sort(key=lambda x: x[1], reverse=True)
                        
                        # 사용 가능한 라인 목록
                        usable_lines = [l for l, _ in line_capacities[:int(max_line)]]
                        
                        # 현재 라인이 사용 가능한 라인 목록에 없으면 용량 제한
                        if line not in usable_lines:
                            return 0
                
                 # 최대 수량 제약
                max_qty_rows = self.capa_qty_data[self.capa_qty_data['Line'] == f'Max_qty_{factory}']
                if not max_qty_rows.empty and time in max_qty_rows.columns:
                    max_qty = max_qty_rows.iloc[0][time]
                    
                    # 최대 수량 제약이 있는 경우
                    if pd.notna(max_qty):
                        # 현재 할당량 계산
                        factory_allocation = self.get_factory_allocation(factory, time)
                        
                        # 현재 라인의 용량
                        line_capacity = 0
                        line_rows = self.capa_qty_data[self.capa_qty_data['Line'] == line]
                        if not line_rows.empty and time in line_rows.columns:
                            capacity = line_rows.iloc[0][time]
                            if pd.notna(capacity):
                                line_capacity = float(capacity)
                        
                        # 용량 제한 계산
                        remaining_capacity = max(0, float(max_qty) - factory_allocation)
                        return min(line_capacity, remaining_capacity)
        
        except Exception as e:
            print(f"라인 용량 확인 중 오류 발생: {str(e)}")
        
        # 용량 정보를 찾지 못한 경우
        return None
    

    """
    특정 제조동의 현재 생산 할당량을 계산
    
    Args:
        factory (str): 제조동 코드 (예: 'I', 'D', 'K', 'M')
        time (int or str): 시프트 번호
        
    Returns:
        float: 현재 할당된 생산량
    """
    def get_factory_allocation(self, factory, time):
        return self.get_current_allocation(factory=factory, time=time)
    
    def get_existing_qty(self, line, time):
        return self.get_current_allocation(line=line, time=time)

    def get_current_allocation(self, line=None, time=None, item=None, factory=None):
        """
        현재 할당량을 계산하는 통합 함수
        
        Args:
            line: 특정 라인의 할당량 (line + time)
            time: 시프트 번호
            item: 특정 아이템의 할당량 (line + time + item)
            factory: 제조동 전체 할당량 (factory + time)
        """
        
        # 1. 특정 아이템의 할당량
        if line and time and item:
            mask = (
                (self.result_data['Line'] == line) &
                (self.result_data['Time'] == time) &
                (self.result_data['Item'] == item)
            )
            matched = self.result_data[mask]
            return float(matched.iloc[0]['Qty']) if not matched.empty else 0
        
        # 2. 특정 라인-시프트의 총 할당량
        elif line and time:
            mask = (
                (self.result_data['Line'] == line) &
                (self.result_data['Time'] == time)
            )
            return self.result_data[mask]['Qty'].sum()
        
        # 3. 제조동 전체의 할당량
        elif factory and time:
            mask = (
                self.result_data['Line'].str.startswith(f'{factory}_', na=False) &
                (self.result_data['Time'] == time)
            )
            return self.result_data[mask]['Qty'].sum()
        
        return 0
    

    """특정 라인/시프느에서 특정 아이템의 수량 조회"""
    def get_item_qty_at_position(self, line, time, item):
        try:
            mask = (
                (self.result_data['Line'] == str(line)) &
                (self.result_data['Time'] == int(time)) &
                (self.result_data['Item'] == str(item))
            )

            matched_rows = self.result_data[mask]

            if not matched_rows.empty:
                qty = matched_rows.iloc[0]['Qty']
                return float(qty)
            else:
                return 0

        except Exception as e:
            print(f"[ERROR] get_item_qty_at_position 오류: {e}")
            return 0

    """
    제조동별 생산량 비율 제약 검증
    
    Args:
        result_data (DataFrame, optional): 검증할 데이터
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    def validate_building_ratios(self, result_data=None):
        data_df = result_data if result_data is not None else self.result_data

        building_ratios = CapaRatioAnalyzer.analyze_capa_ratio(
            data_df=data_df,
            is_initial=True
        )
    
        if not building_ratios:
            return True, "No production volume or unable to calculate plant capacity ratios."
        
        violations = []

        # 각 제조동 별 비율이 제약조건을 만족하는지 검증
        for building, ratio in building_ratios.items():
            # 제약 조건이 있는 제조동만 검증
            if building not in self.building_constraints:
                print(f"제조동 {building}의 제약 조건이 없습니다. 검증 스킵.")
                continue
            
            constraints = self.building_constraints[building]
            lower_limit = constraints.get('lower_limit', 0) * 100
            upper_limit = constraints.get('upper_limit', 0) * 100

            if ratio < lower_limit:
                violations.append(
                    f"Plant '{building}' production ratio {ratio:.2f}% is below "
                    f"minimum limit ({lower_limit:.2f}%)."
                )
            elif ratio > upper_limit:
                violations.append(
                    f"Plant '{building}' production ratio {ratio:.2f}% exceeds "
                    f"maximum limit ({upper_limit:.2f}%)."
                )

        # 위반 사항이 있는지 확인
        if violations:
            return False, "\n".join(violations)
        else:
            return True, "Plant production capacity ratio constraints are satisfied."


    
    """
    아이템의 총 수요량(MFG) 반환
    
    Args:
        item (str): 아이템 코드
        
    Returns:
        int: 총 수요량, 정보 없으면 0
    """
    def _get_total_demand_for_item(self, item):
        if 'demand' in self.demand_data:
            df_demand = self.demand_data['demand']
            item_rows = df_demand[df_demand['Item'] == item]
            if not item_rows.empty and 'MFG' in item_rows.columns:
                return item_rows['MFG'].sum()
            
        # 결과 데이터에서도 확인
        if self.result_data is not None and not self.result_data.empty:
            item_rows = self.result_data[self.result_data['Item'] == item]
            if not item_rows.empty and 'MFG' in item_rows.columns:
                return item_rows['MFG'].iloc[0]
            
        return 0
    

    
    """
    조정된 결과 데이터를 계산 (제약조건 검증용 임시 데이터)
    
    Args:
        line (str): 목표 라인 코드
        time (int): 목표 시프트 번호
        item (str): 아이템 코드
        new_qty (int): 새 생산량
        source_line (str, optional): 이동 시 원래 라인
        source_time (int, optional): 이동 시 원래 시프트
        
    Returns:
        DataFrame: 조정된 결과 데이터
    """
    def _calculate_adjusted_data(self, line, time, item, new_qty, source_line=None, source_time=None):
        # 제조동별 검증
        temp_result_data = self.result_data.copy()

        # 이동인 경우 원본 위치에서 제거
        if source_line and source_time:
            mask = (
                (temp_result_data['Line'] == source_line) & 
                (temp_result_data['Time'] == source_time) & 
                (temp_result_data['Item'] == item)
            )
            if mask.any():
                # 원본 데이터 삭제
                temp_result_data = temp_result_data[~mask].reset_index(drop=True)

        # 새 위치에 할당
        target_mask = (
            (temp_result_data['Line'] == line) &
            (temp_result_data['Time'] == time) &
            (temp_result_data['Item'] == item)
        )

        # 대상 위치에 있으면 업데이트, 없으면 추가
        if target_mask.any():
            temp_result_data.loc[target_mask, 'Qty'] = new_qty
        else:
            # 새 행 생성
            new_row = {
                'Line': line,
                'Time': time,
                'Item': item,
                'Qty': new_qty
            }

            # 프로젝트, rmc 등 필요한 정보 복사
            item_data = self.result_data[self.result_data['Item'] == item]
            if not item_data.empty:
                for col in ['Project', 'RMC', 'To_site', 'SOP', 'MFG', 'Due_LT']:
                    if col in item_data and item_data[col].notna().any():
                        new_row[col] = item_data[col].iloc[0]  # 첫 번째 행의 값만 사용

            # 새 행 추가
            temp_result_data = pd.concat([temp_result_data, pd.DataFrame([new_row])], ignore_index=True)

        return temp_result_data
    
