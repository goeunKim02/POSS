import os
import re
import glob
import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QDate
from openpyxl.styles import Font, PatternFill, Alignment

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
        os.makedirs(output_dir, exist_ok=True)  # 결과 디렉토리 생성


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
    
    """선택한 날짜 범위를 기반으로 이전 계획 파일 탐색"""
    def detect_previous_plan(self, start_date, end_date):
        # Parameters:
        #     start_date (QDate): 사용자가 선택한 시작일
        #     end_date (QDate): 사용자가 선택한 종료일
            
        # Returns:
        #     tuple: (is_first_plan, previous_plan_path, message)

        # 주차 정보 계산
        week_info, week_start, week_end = self.get_week_info(start_date, end_date)

        # 관련 계획 파일 검색
        plan_pattern = os.path.join(self.output_dir, f"*_plan_*.xlsx")
        existing_plans = glob.glob(plan_pattern)

        if not existing_plans:
            return True, None, f"First Plan ({week_info}) - 유지율 비교 없음"
        
        # 파일 정보 수집
        plan_info = []
        for plan_file in existing_plans:
            file_name = os.path.basename(plan_file)
            mod_time = os.path.getmtime(plan_file)

            # 파일명에서 주차 정보 추출
            week_pattern = r'W(\d+\d)'
            week_match = re.search(week_pattern, file_name)

            if week_match:
                file_week = week_match.group(0)  # 전체 주차 문자열(예: W021)
                plan_info.append({
                    'path' :plan_file,
                    'week': file_week,
                    'mod_time' : mod_time
                })
            else:
                # 주차 정보가 없는 경우 수정 시간만 기록
                plan_info.append({
                    'path': plan_file,
                    'week': None,
                    'mod_time': mod_time
                })

        if not plan_info:
            return True, None, f"First Plan ({week_info}) - 유지율 비교 없음"
        
        # 이전 계획 선택 로직
        # 1) 같은 주차 내 이전 버전 찾기
        same_week_plans = [p for p in plan_info if p['week'] == week_info]
        if same_week_plans:
            # 같은 주차 내 시간순 정렬
            same_week_plans.sort(key=lambda x:x['mod_time'], reverse=True)
            prev_plan = same_week_plans[0]
            prev_date = datetime.fromtimestamp(prev_plan['mod_time'])
            date_str = prev_date.strftime("%Y-%m-%d")
            prev_week = prev_plan['week'] if prev_plan['week'] else "None"
            return False, prev_plan['path'], f"pre_plan({prev_week}, {date_str})과 비교"
        
        # 2) 가장 최근 계획 선택 (이 부분이 누락됨)
        plan_info.sort(key=lambda x: x['mod_time'], reverse=True)
        prev_plan = plan_info[0]
        prev_date = datetime.fromtimestamp(prev_plan['mod_time'])
        date_str = prev_date.strftime("%Y-%m-%d")
        prev_week = prev_plan['week'] if prev_plan['week'] else "None"
        return False, prev_plan['path'], f"pre_plan({prev_week}, {date_str})과 비교"
        
        
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

        # 파일명 생성
        file_name = f"Result_{week_info}_{date_str}_{time_str}.xlsx"

        # 전체 경로
        file_path = os.path.join(self.output_dir, file_name)

        # 포함된 demand 목록 추출
        demands = []
        if 'demand' in plan_df.columns:
            demands = sorted(plan_df['demand'].unique().tolist())

        # demands 목록 생성
        demands_str = ", ".join(demands[:10])
        if len(demands) > 10:
            demands_str += f" 외 {len(demands) - 10}개"

        # 엑셀 작성자 생성
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 계획 데이터 저장
            plan_df.to_excel(writer, sheet_name='Result', index=False)

            # 메타데이터 시트 생성
            metadata = {
                '속성': [
                    'week_info',
                    'week_start',
                    'week_end',
                    'demands',
                    'mod_time',
                    'result_type',
                    'prev_result'
                ],
                '값': [
                    week_info,
                    week_start.strftime("%Y-%m-%d"),
                    week_end.strftime("%Y-%m-%d"),
                    demands_str,
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    "수정계획" if previous_plan else "초기계획",
                    os.path.basename(previous_plan) if previous_plan else "없음"
                ]
            }

            metadata_df = pd.DataFrame(metadata)
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

        return file_path
    


        




