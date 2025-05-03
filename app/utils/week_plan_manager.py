import os
import re
import json
import glob
import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QDate
from app.analysis.output.plan_maintenance import PlanMaintenanceRate

"""
주차 정보 관리 클래스
사용자가 선택한 날짜를 기반으로 주차를 계산하고 파일명과 메타데이터에 포함
"""
class WeeklyPlanManager:

    """WeeklyPlanManager 초기화"""
    def __init__(self, output_dir="data/export"):
        # Parameters:
        #     output_dir (str): 결과 저장 디렉토리

        self.output_dir = output_dir
        self.registry_file = os.path.join("data", "plan_registry.json")

        os.makedirs(output_dir, exist_ok=True)  # 결과 디렉토리 생성
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)

        self.registry = self._load_registry()

    """레지스트리 로드"""
    def _load_registry(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {"plans" : []}
            
        else:
            return {"plans" : []}
        
    """레지스트리 저장"""
    def _save_registry(self):
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        
        # 레지스트리 저장
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    """선택한 날짜로부터 주차 정보 계산"""
    def get_week_info(self, start_date, end_date):
        # Parameters:
        #     start_date (QDate 또는 datetime): 사용자가 선택한 시작일
        #     end_date (QDate 또는 datetime): 사용자가 선택한 종료일
            
        # Returns:
        #     tuple: (week_info, week_start, week_end) - 주차 정보 문자열과 주 시작/종료일

        # QDate를 datetime으로 변환
        if isinstance(start_date, QDate):
            week_start = start_date.toPyDate()
        else:
            week_start = start_date.date() if hasattr(start_date, 'date') else start_date

        if isinstance(end_date, QDate):
            week_end = end_date.toPyDate() 
        else:
            week_end = end_date.date() if hasattr(end_date, 'date') else end_date

        # 해당 월의 주차 정보 생성
        month = week_start.month
        first_day_of_month = datetime(week_start.year, month, 1).date()  # 해당 월의 첫째 날(예: 5월 1일)
        day_of_month = (week_start - first_day_of_month).days + 1 # 시작일이 몇 번째 날인지 계산(예: 5월 15일 -> 15번쨰)
        week_of_month = (day_of_month -1) // 7 + 1  # 몇 번째 주인지 계산

        week_info = f"W{month:02d}{week_of_month:01d}"  # 예: W021(2월 1주차)

        return week_info, week_start, week_end
    
    """계획 등록"""
    def register_plan(self, file_path, week_info, start_date, end_date):
        # 계획 정보 생성
        plan_info = {
            "path" :file_path,
            "week" : week_info,
            "start_date": start_date.strftime("%Y-%m-%d") if hasattr(start_date, "strftime") else start_date,
            "end_date": end_date.strftime("%Y-%m-%d") if hasattr(end_date, "strftime") else end_date,
            "mod_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 레지스트리에 추가
        self.registry["plans"].append(plan_info)
        self._save_registry()
    
    """선택한 날짜 범위를 기반으로 이전 계획 파일 탐색"""
    def detect_previous_plan(self, start_date, end_date):
        # Parameters:
        #     start_date (QDate): 사용자가 선택한 시작일
        #     end_date (QDate): 사용자가 선택한 종료일
            
        # Returns:
        #     tuple: (is_first_plan, previous_plan_path, message)

        # 주차 정보 및 폴더 계산
        week_info, week_start, week_end = self.get_week_info(start_date, end_date)
        week_folder = os.path.join(self.output_dir, week_info)

        # 레지스트리에서 주차가 일치하는 계획 찾기
        week_plans = []
        for plan in self.registry["plans"]:
            if plan["week"] == week_info:
                if os.path.exists(plan["path"]):
                    week_plans.append(plan)

        if not week_plans:
            # 주차 폴더가 없으면 기본 output_dir에서 검색
            if not os.path.exists(week_folder):
                plan_pattern = os.path.join(self.output_dir, f"*_plan_*.xlsx")
            else:
                # 주차 폴더 내 파일 검색
                plan_pattern = os.path.join(week_folder, f"*.xlsx")

            existing_plans = glob.glob(plan_pattern)

            for plan_file in existing_plans:
                file_name = os.path.basename(plan_file)
                mod_time = os.path.getmtime(plan_file)

                # 파일명에서 주차 정보 추출
                week_pattern = r'W(\d+\d)'
                week_match = re.search(week_pattern, file_name)

                if week_match and week_match.group(0) == week_info:
                    # 레지스트리에 추가
                    self.register_plan(
                        plan_file, 
                        week_info, 
                        week_start, 
                        week_end
                    )
                    week_plans.append({
                        'path': plan_file,
                        'week': week_info,
                        'mod_time': datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    })

        if not week_info or not week_plans:
            return True, None, f"First Plan ({week_info}) - No maintenance rate comparison"
        
        # 시간순 정렬
        week_plans.sort(key=lambda x: x["mod_time"], reverse=True)
        
        # 가장 최근 계획 반환
        if len(week_plans) >= 2:
            prev_plan = week_plans[0]
            return False, prev_plan["path"], f"Comparing with previous plan ({prev_plan['week']}, {prev_plan['mod_time']})"
        else:
            # 첫 계획인 경우
            return True, None, f"First Plan ({week_info}) - No previous plan to compare"


    """계획 데이터 저장 및 메타데이터 추가"""
    def save_plan_with_metadata(self, plan_df, start_date, end_date, previous_plan=None):
        # Parameters:
        #     plan_df (DataFrame): 계획 데이터
        #     start_date (QDate): 사용자가 선택한 시작일
        #     end_date (QDate): 사용자가 선택한 종료일
        #     previous_plan (str): 이전 계획 파일 경로 (있는 경우)
        
        # Returns:
        #     str: 저장된 파일 경로

        # 주차 정보 계산
        week_info, week_start, week_end = self.get_week_info(start_date, end_date)

        # 현재 날짜 및 시간
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")

        # 주차별 폴더 경로 생성
        week_folder = os.path.join(self.output_dir, week_info)

        # 폴더가 없으면 생성
        os.makedirs(week_folder, exist_ok=True)

        # 파일명 생성
        file_name = f"Plan_{week_info}_{date_str}_{time_str}.xlsx"

        # 전체 경로
        file_path = os.path.join(week_folder, file_name)

         # 계획 유지율 계산
        plan_maintenance_rate = None
        is_first_plan = True
        
        if previous_plan and os.path.exists(previous_plan):
            is_first_plan = False
            plan_maintenance_rate = self._calculate_plan_maintenance(plan_df, previous_plan)

        # 엑셀 작성자 생성
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 계획 데이터 저장
            plan_df.to_excel(writer, sheet_name='result', index=False)

            # 메타데이터 시트 생성
            metadata = {
                '속성': [
                    'week_info',
                    'week_start',
                    'week_end',
                    'mod_time',
                    'result_type',
                    'prev_result'
                ],
                '값': [
                    week_info,
                    week_start.strftime("%Y-%m-%d"),
                    week_end.strftime("%Y-%m-%d"),
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    "Modified Plan" if previous_plan else "Initial Plan",
                    os.path.basename(previous_plan) if previous_plan else "Unknown"
                ]
            }

            metadata_df = pd.DataFrame(metadata)
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

        # 레지스트리에 새 계획 등록
        self.register_plan(file_path, week_info, week_start, week_end)

        return file_path
    

    """계획 유지율 계산"""
    def _calculate_plan_maintenance(self, current_df, previous_plan_path):
        # Parameters:
        #     current_df (DataFrame): 현재 계획 데이터
        #     previous_plan_path (str): 이전 계획 파일 경로
            
        # Returns:
        #     float: 계획 유지율 
   
        try:
            # 이전 계획 데이터 로드
            prev_df = pd.read_excel(previous_plan_path, sheet_name='Result')
            
            # 분석기 초기화
            analyzer = PlanMaintenanceRate()
            
            # 첫 번째 계획이 아님
            analyzer.set_first_plan(False)
            
            # 이전 계획 설정
            analyzer.set_original_plan(prev_df)
            
            # 현재 계획 설정
            analyzer.set_current_plan(current_df)
            
            # Item별 유지율 계산
            _, item_rate = analyzer.calculate_items_maintenance_rate(compare_with_adjusted=False)
            
            # RMC별 유지율 계산
            _, rmc_rate = analyzer.calculate_rmc_maintenance_rate(compare_with_adjusted=False)
            
            return {
                'item_rate': item_rate,
                'rmc_rate': rmc_rate
            }
        except Exception as e:
            print(f"계획 유지율 계산 오류: {e}")
            return {
                'item_rate': None,
                'rmc_rate': None
            }
    


        




