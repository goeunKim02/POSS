import pandas as pd
from app.core.input.capaValidator import validate_distribution_ratios
from app.models.common.fileStore import DataStore, FilePaths
from app.utils.fileHandler import load_file

"""결과 조정 시 제약사항 점검 클래스"""
class PlanAdjustmentValidator:
    def __init__(self, result_data):
        # Args:
        #     result_data (DataFrame): 조정할 결과 데이터

        self.result_data = result_data

        # DataStore에서 필요한 파일 로드
        self.organized_dataframes = DataStore.get("organized_dataframes")
        self.master_data = self.organized_dataframes.get("master", {})
        self.demand_data = self.organized_dataframes.get("demand", {})

        self.capa_qty_data = self.master_data.get("capa_qty", pd.DataFrame())

        # 제약사항 추출 및 캐싱
        self._extract_constraints()
        self._cache_reference_data()

    """제약사항 추출"""
    def _extract_constraints(self):
        # 초기화
        self.line_capacities = {}    # 라인별 용량
        self.due_dates = {}          # 아이템/프로젝트별 납기일
        self.building_constraints = {}  # 제조동 제약
        self.line_item_compatibility = {}  # 라인-아이템 호환성

        # master_data 추출
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

        # 라인 가용성 추출
        if 'line_available' in self.master_data:
            df_line_available = self.master_data['line_available']
            for _, row in df_line_available.iterrows():
                if 'Project' in row:
                    project = row['Project']
                    self.line_item_compatibility[project] = []

                    for col in df_line_available.columns:
                        if col != 'Project' and row[col] == 1:
                            self.line_item_compatibility[project].append(col)

        # 납기일 추출
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

         # 제조동 제약 추출
        if 'capa_portion' in self.master_data:
            df_portion = self.master_data['capa_portion']
            if not df_portion.empty and 'name' in df_portion.columns:
                for _, row in df_portion.iterrows():
                    if 'name' in row and 'lower_limit' in row and 'upper_limit' in row:
                        building = row['name']
                        self.building_constraints[building] = {
                            'lower_limit': float(row['lower_limit']),
                            'upper_limit': float(row['upper_limit'])
                        }

    """결과에서 참조 정보 추출"""
    def _cache_reference_data(self):
        if self.result_data is None or self.result_data.empty:
            return
        
        # 라인별 시프트별 현재 할당량 계산
        self.line_shift_allocation = {}

        for _, row in self.result_data.iterrows():
            line = row.get('Line')
            time = row.get('Time')
            qty = row.get('Qty', 0)
            
            if line and time is not None:
                key = f"{line}_{time}"
                if key not in self.line_shift_allocation:
                    self.line_shift_allocation[key] = 0
                self.line_shift_allocation[key] += qty
                
        # 라인별 사용 가능한 아이템 목록 캐싱
        self.line_available_items = {}
        
        # 결과 데이터에서 라인-아이템 호환성 정보 추출
        for _, row in self.result_data.iterrows():
            line = row.get('Line')
            item = row.get('Item')
            
            if line and item:
                if line not in self.line_available_items:
                    self.line_available_items[line] = set()
                self.line_available_items[line].add(item)

    """capaValidator에 전달할 데이터"""
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

        # project_to_buildings 설정
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


    """라인과 아이템의 호환성 검증"""
    def validate_line_item_compatibility(self, line, item):
        # 아이템 코드에서 프로젝트 추출 
        project = item[3:7] if len(item) >= 7 else ""
        
        # 마스터 데이터의 호환성 정보 확인
        if project in self.line_item_compatibility:
            compatible_lines = self.line_item_compatibility[project]
            if line not in compatible_lines:
                return False, f"아이템 '{item}'(프로젝트 {project})은(는) 라인 '{line}'에서 생산할 수 없습니다."
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
        # (이 부분은 실제 비즈니스 로직에 따라 다를 수 있음)
        return True, ""
    
    """라인 용량 초과 여부 검증"""
    def validate_capacity(self, line, time, new_qty, item=None, is_move=False):
        
        # 라인-시프트 키 생성
        key = f"{line}_{time}"

        # 시프트의 현재 할당량 확인
        current_allocation = self.line_shift_allocation.get(key, 0)
        
        # 이동인 경우 해당 아이템의 기존 할당량 제외
        if is_move and item:
            for _, row in self.result_data.iterrows():
                if row.get('Line') == line and row.get('Time') == time and row.get('Item') == item:
                    current_allocation -= row.get('Qty', 0)
                    break

        # 마스터 데이터에서 라인과 시프트 용량 가져오기
        capacity = self.get_line_capacity(line, time)
        
        print(f"검증: 라인={line}, 시프트={time}, 현재 할당량={current_allocation}, 신규 수량={new_qty}")
        print(f"용량 정보: {capacity}")
        print(f"검증 결과: {current_allocation + new_qty} <= {capacity} = {current_allocation + new_qty <= capacity}")
        # 용량 검증
        if capacity is not None:
            if current_allocation + new_qty > capacity:
                return False, f"라인 '{line}'의 시프트 {time} 용량({capacity})을 초과합니다. 현재 {current_allocation}, 추가 {new_qty}"
        
        return True, ""
    
    """납기일 준수 여부 검증"""
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
            return False, f"아이템 '{item}'의 납기일(시프트 {due_time})을 초과했습니다."
            
        return True, ""
    
    """요일별 가동률 제약 검증"""
    def validate_utilization_rate(self, line, time, new_qty):
        # 시프트별 최대 가동률 설정 (각 시프트마다 다른 값 설정 가능)
        max_utilization_by_shift = {
            1: 110,  # 1번 시프트 최대 가동률
            2: 110, 
            3: 110,  
            4: 110,  
            5: 110,  
            6: 80,  
            7: 60,   
            8: 110,  
            9: 110, 
            10: 110, 
            11: 110, 
            12: 110, 
            13: 110, 
            14: 110, 
        }

        # 라인-시프트 키 생성
        key = f"{line}_{time}"
        current_allocation = self.line_shift_allocation.get(key, 0)
        
        # 라인의 기본 용량 확인
        line_capacity = None
        if line in self.line_capacities and time in self.line_capacities[line]:
            line_capacity = self.line_capacities[line][time]

        # 용량 정보가 없는 경우 처리
        if line_capacity is None or line_capacity <= 0:
            # 용량 정보가 없으면 다른 방법으로 제약 조건 확인
            # 예: 해당 라인/시프트의 capacity 값 직접 조회
            capacity = self.get_line_capacity(line, time)
            if capacity is not None and capacity > 0:
                line_capacity = capacity
            else:
                # 용량 정보를 찾을 수 없는 경우
                print(f"경고: 라인 '{line}'의 시프트 {time}에 대한 용량 정보를 찾을 수 없습니다.")
                # 용량 정보가 없으면 제약 조건을 검증할 수 없으므로 통과
                return True, ""
    
        new_total = current_allocation + new_qty
        utilization_rate = (new_total / line_capacity) * 100

        # 해당 시프트의 최대 가동률 가져오기
        max_rate = max_utilization_by_shift.get(time, 100)  # 기본값 100%
        
        if utilization_rate > max_rate:
            return False, f"시프트 {time}의 최대 가동률({max_rate}%)을 초과합니다. 현재 계획: {utilization_rate:.1f}%"
    
        return True, ""
    
    """모든 검증 로직을 통합 실행"""
    def validate_adjustment(self, line, time, item, new_qty, source_line=None, source_time=None):
        print("validate_adjustment 호출됨")
        # 이동 여부 확인
        is_move = source_line is not None and source_time is not None

        # 타입 변환 (문자열 -> 숫자)
        try:
            if isinstance(time, str):
                time = int(time)
            if isinstance(new_qty, str):
                new_qty = int(float(new_qty))
            if isinstance(source_time, str) and source_time is not None:
                source_time = int(source_time)
        except (ValueError, TypeError) as e:
            return False, f"입력값 변환 중 오류 발생: {str(e)}"
        
        # 물량 비율 검증은 기존 함수 재사용
        # processed_data = self._prepare_data_for_validator()
        # distribution_result = validate_distribution_ratios(processed_data)
        
        # if not distribution_result['current_valid'] and not distribution_result['alternative_possible']:
        #     return False, "제조동별 물량 비율 제약을 만족하지 않습니다."
        
        # 라인-아이템 호환성 검증
        valid, message = self.validate_line_item_compatibility(line, item)
        if not valid:
            return False, message
        
        # 용량 검증
        valid, message = self.validate_capacity(line, time, new_qty, item, is_move)
        if not valid:
            return False, message
        
        # 납기일 검증
        valid, message = self.validate_due_date(item, time)
        if not valid:
            return False, message
        
        # 가동률 검증
        valid, message = self.validate_utilization_rate(line, time, new_qty)
        if not valid:
            return False, message
        
        return True, "조정 가능합니다."
    
    def get_line_capacity(self, line, time):
        """
        특정 라인과 시프트의 생산 용량을 반환합니다.
        
        Args:
            line (str): 라인 코드 (예: 'I_01')
            time (int or str): 시프트 번호 (예: 1, 2, ...)
            
        Returns:
            int or None: 해당 라인과 시프트의 생산 용량, 없으면 None
        """
        # 숫자형 time 문자열로 변환 (마스터 데이터와 형식 일치를 위해)
        print(f"디버깅 - get_line_capacity 시작: 라인={line}, 시프트={time}")
        
        # # 이미 캐싱된 capa_qty_data 사용
        # if self.capa_qty_data is None or self.capa_qty_data.empty:
        #     print("capa_qty 데이터가 비어 있습니다.")
        #     return None

            # capa_qty_data 확인
        if self.capa_qty_data is None:
            print("디버깅 - capa_qty_data가 None입니다.")
            return None
        elif self.capa_qty_data.empty:
            print("디버깅 - capa_qty_data가 비어 있습니다.")
            return None
            
        # capa_qty_data의 기본 정보 출력
        print(f"디버깅 - capa_qty_data 컬럼: {self.capa_qty_data.columns.tolist()}")
        print(f"디버깅 - capa_qty_data 'Line' 컬럼 존재: {'Line' in self.capa_qty_data.columns}")
        print(f"디버깅 - capa_qty_data {time} 컬럼 존재: {time in self.capa_qty_data.columns}")
        

        try:
            # # 라인이 인덱스에 있는 경우
            # if 'Line' in self.capa_qty_data.columns and time in self.capa_qty_data.columns:
            #     line_rows = self.capa_qty_data[self.capa_qty_data['Line'] == line]
            #     if not line_rows.empty:
            #         capacity = line_rows.iloc[0][time]
            #         if pd.notna(capacity):
            #             return float(capacity)
            if 'Line' in self.capa_qty_data.columns:
                print(f"디버깅 - Line 값 예시: {self.capa_qty_data['Line'].head(5).tolist()}")
                line_rows = self.capa_qty_data[self.capa_qty_data['Line'] == line]
                print(f"디버깅 - 라인 '{line}'에 해당하는 행 수: {len(line_rows)}")
                
                if not line_rows.empty and time in self.capa_qty_data.columns:
                    capacity = line_rows.iloc[0][time]
                    print(f"디버깅 - 찾은 용량 값: {capacity}, 타입: {type(capacity)}")
                    if pd.notna(capacity):
                        return float(capacity)
                    else:
                        print(f"디버깅 - 용량 값이 NaN입니다.")
            
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
    

    def get_factory_allocation(self, factory, time):
        """
        특정 제조동의 현재 생산 할당량을 계산합니다.
        
        Args:
            factory (str): 제조동 코드 (예: 'I', 'D', 'K', 'M')
            time (int or str): 시프트 번호
            
        Returns:
            float: 현재 할당된 생산량
        """
        if not hasattr(self, 'result_data') or self.result_data is None:
            return 0
        
        # 숫자로 변환
        if isinstance(time, str) and time.isdigit():
            time = int(time)
        
        # 해당 제조동의 라인만 필터링
        factory_lines = [line for line in self.result_data['Line'].unique() 
                        if isinstance(line, str) and line.startswith(f'{factory}_')]
        
        # 해당 제조동 및 시프트의 할당량 합계
        allocation = 0
        for _, row in self.result_data.iterrows():
            if row.get('Line') in factory_lines and row.get('Time') == time:
                allocation += row.get('Qty', 0)
        
        return allocation





