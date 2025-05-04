"""결과 조정 시 제약사항 점검 클래스"""
class PlanAdjustmentValidator:
    def __init__(self, result_data, master_data=None, demand_data=None):
        # Args:
        #     result_data (DataFrame): 조정할 결과 데이터
        #     master_data (dict): 마스터 데이터 파일에서 추출한 라인/용량 정보
        #     demand_data (dict): 수요 데이터 파일에서 추출한 납기일 등 정보

        self.result_data = result_data
        self.master_data = master_data
        self.demand_data = demand_data

        # 제약사항 추출 및 캐싱
        self._extract_constraints()

        # 참조 데이터 캐싱
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
        
        # 이 부분은 실제 라인-아이템 호환성 데이터에서 추출
        for _, row in self.result_data.iterrows():
            line = row.get('Line')
            item = row.get('Item')
            
            if line and item:
                if line not in self.line_available_items:
                    self.line_available_items[line] = set()
                self.line_available_items[line].add(item)


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
    
    def validate_capacity(self, line, time, new_qty, item=None, is_move=False):
        """라인 용량 초과 여부 검증"""
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
        
        # 최대 용량 확인 (우선순위: 마스터 데이터 > 기본값)
        max_capacity = 6000  # 기본값
        
        if line in self.line_capacities and time in self.line_capacities[line]:
            max_capacity = self.line_capacities[line][time]
        
        # 용량 검증
        if current_allocation + new_qty > max_capacity:
            return False, f"라인 '{line}'의 시프트 {time} 용량({max_capacity})을 초과합니다. 현재 {current_allocation}, 추가 {new_qty}"
            
        return True, ""
    
    def validate_due_date(self, item, time):
        """납기일 준수 여부 검증"""
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
    
    def validate_utilization_rate(self, line, time, new_qty):
        """요일별 가동률 제약 검증"""
        # 시프트를 요일로 변환 (예시 로직, 실제 매핑은 다를 수 있음)
        time_to_day = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 2}  # 0: 평일, 1: 토요일, 2: 일요일
        day_names = ["Weekday", "Saturday", "Sunday"]
        
        day_index = time_to_day.get(time, 0)
        day_of_week = day_names[day_index]
        
        # 요일별 최대 가동률 설정
        max_utilization = {
            "Weekday": 110,
            "Saturday": 80,
            "Sunday": 60
        }
        
        # 라인-시프트 키 생성
        key = f"{line}_{time}"
        current_allocation = self.line_shift_allocation.get(key, 0)
        
        # 라인의 기본 용량 확인
        line_capacity = 6000  # 기본값
        if line in self.line_capacities and time in self.line_capacities[line]:
            line_capacity = self.line_capacities[line][time]
            
        new_total = current_allocation + new_qty
        utilization_rate = (new_total / line_capacity) * 100
        
        if utilization_rate > max_utilization[day_of_week]:
            return False, f"{day_of_week}의 최대 가동률({max_utilization[day_of_week]}%)을 초과합니다. 현재 계획: {utilization_rate:.1f}%"
            
        return True, ""
    
    def validate_adjustment(self, line, time, item, new_qty, source_line=None, source_time=None):
        """모든 검증 로직을 통합 실행"""
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





