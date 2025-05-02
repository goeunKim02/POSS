import pandas as pd
from app.models.input.material import process_material_data

class MaterialAnalyzer :
    def __init__(self) :
        self.material_data = None
        self.material_df = None
        self.date_columns = []
        self.weekly_columns = []
        self.weekly_shortage_materials = None
        self.full_period_shortage_materials = None
        self.shortage_materials = None

    # 자재 데이터 분석 후 결과 저장
    def analyze(self) :
        self.material_data = process_material_data()

        if not self.material_data or 'material_df' not in self.material_data :
            print('자재 데이터 처리에 실패했습니다')
            return False
        
        self.material_df = self.material_data['material_df']
        self.date_columns = self.material_data.get('date_columns', [])
        self.weekly_columns = self.material_data.get('weekly_columns', [])

        self.calculate_shortage_amounts()
        self.analyze_shortage_materials()

        return True
    
    # 자재별 부족량 계산
    def calculate_shortage_amounts(self) :
        if self.material_df is None or 'On-Hand' not in self.material_df.columns :
            return
        
        self.material_df['Weekly_Sum'] = self.material_df['On-Hand'].copy()

        for col in self.weekly_columns :
            self.material_df['Weekly_Sum'] += self.material_df[col]

        self.material_df['Full_Period_Sum'] = self.material_df['On-Hand'].copy()

        for col in self.date_columns :
            self.material_df['Full_Period_Sum'] += self.material_df[col]

        self.material_df['Weekly_Shortage'] = self.material_df['Weekly_Sum'].apply(
            lambda x : abs(x) if x < 0 else 0
        )
        self.material_df['Full_Period_Shortage'] = self.material_df['Full_Period_Sum'].apply(
            lambda x : abs(x) if x < 0 else 0
        )

        self.material_df['Shortage_Rate'] = 0.0
        mask = (self.material_df['On-Hand'] > 0) & (self.material_df['Weekly_Shortage'] > 0)
        self.material_df.loc[mask, 'Shortage_Rate'] = (
            self.material_df.loc[mask, 'Weekly_Shortage'] / self.material_df.loc[mask, 'On-Hand'] * 100
        )

    # 부족한 자재 식별하고 분석
    def analyze_shortage_materials(self) :
        if self.material_df is None or 'Weekly_Sum' not in self.material_df.columns :
            return
        
        self.weekly_shortage_materials = self.material_df[self.material_df['Weekly_Sum'] < 0].copy()

        self.full_period_shortage_materials = self.material_df[self.material_df['Full_Period_Sum'] < 0].copy()

        self.shortage_materials = pd.concat([
            self.weekly_shortage_materials,
            self.full_period_shortage_materials[~self.full_period_shortage_materials['Material'].isin(
                self.weekly_shortage_materials['Material'])]
        ]).drop_duplicates(subset = ['Material'])

        if not self.weekly_shortage_materials.empty :
            self.weekly_shortage_materials = self.weekly_shortage_materials.sort_values(
                by = 'Full_Period_Shortage', ascending=False)
            
        if not self.shortage_materials.empty :
            self.shortage_materials = self.shortage_materials.sort_values(
                by='Weekly_Shortage', ascending=False)
            
    # 4/7 ~ 4/13 동안 부족한 자재 리포트 반환
    def get_weekly_shortage_report(self) :
        report = []
        report.append(f'[일주일 내 부족한 자재 리포트 (총 {len(self.weekly_shortage_materials)}개)]')
        report.append('=' * 70)
        report.append(f'{'자재코드':<15} {'Active':<6} {'On-Hand':<10} {'부족량':<10} {'부족률 (%)':<10}')
        report.append('-' * 70)

        for _, row in self.weekly_shortage_materials.iterrows() :
            material = row['Material']
            active = row['Active_OX']
            on_hand = row['On-Hand']
            shortage = row['Weekly_Shortage']

            shortage_rate = row.get('Shortage_Rate', 0)

            report.append(f"{material:<15} {active:<6} {on_hand:<10.0f} {shortage:<10.0f} {shortage_rate:<10.1f}")

        return '\n'.join(report)
    
    # 가장 심각하게 부족한 자재 목록 반환(10개)
    def get_critical_shortage_materials(self, limit=10) :
        if self.weekly_shortage_materials is None or self.weekly_shortage_materials.empty :
            return []
        
        critical_materials = self.weekly_shortage_materials.sort_values(
            by='Weekly_Shortage', ascending=False).head(limit)
        
        return critical_materials
    
    # 커스텀한 기준에 따라 부족한 자재 정렬 후 반환
    def get_shortage_materials_by_criteria(self, criteria='quantity', limit=None) :
        if self.weekly_shortage_materials is None or self.weekly_shortage_materials.empty :
            return pd.DataFrame()
        
        sorted_materials = self.weekly_shortage_materials.copy()

        if criteria == 'quantity' :
            sorted_materials = sorted_materials.sort_values(by='Weekly_Shortage', ascending=False)
        elif criteria == 'rate' :
            sorted_materials = sorted_materials.sort_values(by='Shortage_Rate', ascending=False)
        elif criteria == 'code' :
            sorted_materials = sorted_materials.sort_values(by='Material')

        if limit :
            sorted_materials = sorted_materials.head(limit)

        return sorted_materials
    
    # 일별 부족 추이 계산
    def get_daily_shortage_trend(self, material_code = None) :
        if self.material_df is None :
            return None
        
        if material_code :
            material_df = self.material_df[self.material_df['Material'] == material_code]

            if material_df.empty :
                return None
            
            material_row = material_df.iloc[0]
            daily_trend = {'Date' : [], 'Cumulative' : []}

            cumulative = material_row['On-Hand'] if 'On-Hand' in material_row else 0
            daily_trend['Date'].append('Current')
            daily_trend['Cumulative'].append(cumulative)

            for date_col in self.date_columns :
                if date_col in material_row :
                    cumulative += material_row[date_col]
                    daily_trend['Date'].append(date_col)
                    daily_trend['Cumulative'].append(cumulative)

            return pd.DataFrame(daily_trend)
        else :
            critical_materials = self.get_critical_shortage_materials(5)
            
            if critical_materials.empty :
                return None
            
            date_shortage_count = {'Date' : ['Current'] + self.date_columns, 'Shortage_Count' : [0] * (len(self.date_columns) + 1)}

            for _, material_row in critical_materials.iterrows() :
                cumulative = material_row['On-Hand'] if 'On-Hand' in material_row else 0

                if cumulative < 0 :
                    date_shortage_count['Shortage_Count'][0] += 1

                for i, date_col in enumerate(self.date_columns) :
                    if date_col in material_row :
                        cumulative += material_row[date_col]

                        if cumulative < 0 :
                            date_shortage_count['Shortage_Count'][i + 1] += 1

                return pd.DataFrame(date_shortage_count)
            
    # 부족한 자재 상세 정보 로그 출력
    def print_shortage_details(self, detailed=False) :
        if self.weekly_shortage_materials is None or self.weekly_shortage_materials.empty :
            print('부족한 자재가 없습니다')
            return
        
        print(self.get_weekly_shortage_report())
        print('\n')

        if detailed and not self.weekly_shortage_materials.empty :
            print('부족 자재 상세 정보')
            
            critical_materials = self.weekly_shortage_materials.head(10)

            for idx, (_, row) in enumerate(critical_materials.iterrows(), 1) :
                material = row['Material']
                on_hand = row['On-Hand']
                weekly_sum = row['Weekly_Sum']
                weekly_shortage = row['Weekly_Shortage']

                print(f"\n{idx}. 자재코드: {material} (부족량: {weekly_shortage:.0f})")
                print(f"   현재고(On-Hand): {on_hand:.0f}")
                print(f"   주간합계(Weekly_Sum): {weekly_sum:.0f}")

                print('일별 누적 추이')
                cumulative = on_hand
                print(f'{cumulative:.0f}')

                for date_col in self.weekly_columns :
                    if date_col in row :
                        daily_value = row[date_col]
                        cumulative += daily_value
                        status = '부족' if cumulative < 0 else '정상'

                        print(f"   - {date_col}: {daily_value:.0f} (누적: {cumulative:.0f}, {status})")

    # 결과를 로그에 띄우는 함수
    def analyze_material_shortage() :
        analyzer = MaterialAnalyzer()

        if analyzer.analyze() :
            analyzer.print_shortage_details(detailed=True)

            if analyzer.weekly_shortage_materials is not None :
                weekly_count = len(analyzer.weekly_shortage_materials)
                print(f"\n주간(4/7~4/13) 부족 자재 총 {weekly_count}개")

            if analyzer.full_period_shortage_materials is not None :
                full_count = len(analyzer.full_period_shortage_materials)
                print(f"전체 기간(4/7~4/20) 부족 자재 총 {full_count}개")

            return {
                'weekly_shortage' : analyzer.weekly_shortage_materials,
                'full_period_shortage' : analyzer.full_period_shortage_materials,
                'all_materials' : analyzer.material_df
            }
        else :
            print('자재 분석에 실패했습니다')
            return None