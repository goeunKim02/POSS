from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np

from app.models.common.settings_store import SettingsStore

"""
KPI Score 계산
"""
class KpiScore:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.opts = {}
        self.df = None  # 결과 데이터
        self.material_analyzer = None
        self.demand_df = None
        self.kpi_widget = None

    """
    설정값 가져오기
    """
    def get_options(self):
        # 설정값 가져오기
        all_settings = SettingsStore.get_all()

        # 필요한 설정값 추출
        self.opts = {
            'weight_sop_ox': all_settings.get('weight_sop_ox', 1.0),  # SOP 가중치
            'mat_use': all_settings.get('mat_use', 0),  # 자재제약 반영여부
            'weight_mat_qty': all_settings.get('weight_mat_qty', 1.0),  # 자재 가중치
            'weight_operation': all_settings.get('weight_operation', 1.0),  # 가동률 가중치
            'weight_day_ox': all_settings.get('weight_day_ox', 0),  # shift별 가중치 반영여부
            'weight_day': all_settings.get('weight_day', [1.0, 1.0, 1.0]),  # shift별 가중치
        }

        return self.opts
    
    """
    데이터 설정
    """
    def set_data(self, result_data, material_anaylsis=None, demand_df=None):
        self.df = result_data  # 참조를 저장하여 실시간 업데이트 가능 
        self.material_analyzer = material_anaylsis
        self.demand_df = demand_df

    """
    KPI 위젯 참조 저장
    """
    def set_kpi_widget(self, kpi_widget):
        self.kpi_widget = kpi_widget

    
    """
    자재 점수 계산
    """
    def calculate_material_score(self):
        if not self.material_analyzer or not hasattr(self.material_analyzer, 'shortage_results'):
            return 0
        
        # 총 할당량
        total_qty = self.df['Qty'].sum()
        
        # 자재부족량
        neg_shortage = 0
        for item_shortages in self.material_analyzer.shortage_results.values():
            for shortage_info in item_shortages:
                # 절대값으로 저장되어 있으므로 음수 변환
                shortage_amount = -abs(shortage_info.get('shortage', 0))
                neg_shortage += shortage_amount

        # 점수 계산 : 1 + (부족량 합계 / 총 수량)
        mat_score = (1 + neg_shortage / total_qty) * 100

        return mat_score


    """
    SOP 점수 계산
    """ 
    def calculate_sop_score(self):
        if self.df is None or self.demand_df is None:
            return 0
        
        # Due_LT 내에 모두 충족된 수요
        # Item과 To_site 조합으로 실제 생산량과 요구량 비교
        df = self.df
        # To_stie가 없다면 직접 추출
        if 'To_site' not in self.df.columns:
            df = df.copy()
            df['To_site'] = df['Item'].str[7:8]

        # demand_df에서도 To_site 컬럼 확인
        demand_copy = self.demand_df.copy()
        if 'To_site' not in demand_copy.columns:
            demand_copy['To_site'] = demand_copy['Item'].str[7:8]
        
        # 전체 모델/To_site 조합 수
        if 'SOP' in demand_copy.columns:
            demand_summary = demand_copy.groupby(['Item', 'To_site'])['SOP'].first().reset_index()
            demand_summary.rename(columns={'SOP':'DemandQty'}, inplace=True)

        total_demand = len(demand_summary)

        # Due_LT 내의 생산량만 집계
        due_lt_mask = df['Time'] <= df['Due_LT']
        due_lt_production = df[due_lt_mask].groupby(['Item', 'To_site'])['Qty'].sum().reset_index()
        due_lt_production.rename(columns={'Qty': 'ProducedQty'}, inplace=True)

        # 병합하여 비교
        comparison = pd.merge(demand_summary, due_lt_production, on=['Item', 'To_site'], how='left')
        comparison['ProducedQty'] = comparison['ProducedQty'].fillna(0)
        
        # SOP 성공한 모델/To_site 조합 수 (Due_LT 내 생산량 >= SOP 요구량)
        successful_combinations = len(comparison[comparison['ProducedQty'] >= comparison['DemandQty']]) 
        
        # SOP 점수 
        sop_score = (successful_combinations / total_demand * 100) if total_demand > 0 else 100.0
        
        return sop_score
    

    """
    가동률 점수 계산
    """
    def calculate_utilization_score(self):
        if self.df is None:
            return 0.0
        
        # Shift별 실제 생산량
        result_pivot = self.df.groupby('Time')['Qty'].sum()

        # 가중치 적용 : weight_day_ox가 켜져있으면 weight_day 사용
        if self.opts.get('weight_day_ox', 0):
            weights = self.opts.get('weight_day', [1.0] * 14)
        else:  # 아니면 균등 가중치
            weights = [1.0] * 14  

        # 실제 생산량에 가중치 적용
        weighted_result = 0
        weighted_capacity = 0

        for shift in range(1, 15):
            if shift <= len(weights):
                weight = weights[shift - 1]
                qty = result_pivot.get(shift, 0)
                
                # 최대 용량 계산 (마스터 데이터에서 가져와야 함)
                # 여기서는 실제 생산량을 기준으로 계산
                capacity = qty  # 임시로 실제값 사용

                weighted_result += qty * weight
                weighted_capacity += capacity * weight

        # 가동률 계산
        util_score = (weighted_result / weighted_capacity) * 100
        
        return util_score
    

    """
    총 점수 계산
    """
    def calculate_total_score(self, mat_score, sop_score, util_score):
        # 가중치 계산
        w_mat = self.opts['weight_mat_qty'] if self.opts['mat_use'] else 0.0  # 자재 가중치
        w_sop = self.opts['weight_sop_ox']  # SOP 가중치
        w_oper = self.opts['weight_operation']  # 가동률 가중치

        w_total = w_mat + w_sop + w_oper

        # 가중치 평균 계산
        total_score = (
            (mat_score * w_mat + sop_score * w_sop + util_score * w_oper) / w_total
        )

        return total_score
    

    """
    모든 점수 계산
    """
    def calculate_all_scores(self):
        self.get_options()

        # 각 점수 계산
        mat_score = self.calculate_material_score()
        sop_score = self.calculate_sop_score()
        util_score = self.calculate_utilization_score()
        total_score = self.calculate_total_score(mat_score, sop_score, util_score)
        
        return {
            'Mat': mat_score,
            'SOP': sop_score,
            'Util': util_score,
            'Total': total_score
        }


    """
    점수 새로고침 및 위젯 업데이트
    """
    def refresh_kpi_scores(self):
        if self.kpi_widget:
            scores = self.calculate_all_scores()
            self._update_kpi_labels(scores)
            return scores
        return None


    """
    KPI 라벨 업데이트
    """
    def _update_kpi_labels(self, scores):
        if not self.kpi_widget or not scores:
            return
            
        # 기존 위젯 제거
        layout = self.kpi_widget.layout()
        for i in reversed(range(layout.count())):
            child = layout.itemAt(i).widget()
            if child:
                child.setParent(None)
  
        # 점수에 따른 색상 결정
        def get_color(score):
            if score >= 90:
                return "color: #28a745;"  # 초록색
            elif score >= 70:
                return "color: #ffc107;"  # 노란색
            else:
                return "color: #dc3545;"  # 빨간색
        
        # Mat 점수 : 반올림하여 소수점 1자리
        mat_label = QLabel(f"Mat: {scores['Mat']:.1f}%")
        mat_label.setStyleSheet(f"font-weight: bold; {get_color(scores['Mat'])}")
        layout.addWidget(mat_label, 0, 0)
        
        # SOP 점수
        sop_label = QLabel(f"SOP: {scores['SOP']:.1f}%")
        sop_label.setStyleSheet(f"font-weight: bold; {get_color(scores['SOP'])}")
        layout.addWidget(sop_label, 0, 1)
        
        # Util 점수
        util_label = QLabel(f"Util: {scores['Util']:.1f}%")
        util_label.setStyleSheet(f"font-weight: bold; {get_color(scores['Util'])}")
        layout.addWidget(util_label, 0, 2)
        
        # Total 점수
        total_label = QLabel(f"Total: {scores['Total']:.1f}%")
        total_label.setStyleSheet(f"font-weight: bold; font-size: 14pt; {get_color(scores['Total'])}")
        total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(total_label, 1, 0, 1, 3)
    
    def update_kpi_widget(self, kpi_widget, layout_type='grid'):
        """KPI 위젯 업데이트 (기존 메서드와 호환성 유지)"""
        self.set_kpi_widget(kpi_widget)
        return self.refresh_kpi_scores() 



