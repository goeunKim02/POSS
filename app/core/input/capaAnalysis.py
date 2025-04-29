import pandas as pd
from app.models.common.projectGrouping import ProjectGroupManager

# 분석 테이블 생성
class PjtGroupAnalyzer:
    def __init__(self, processed_data):
        self.processed_data = processed_data
        self.demand_items = processed_data['demand_items']
        self.project_to_buildings = processed_data.get('project_to_buildings', {})
        self.line_capacities = processed_data.get('line_capacities', {})
        self.building_constraints = processed_data.get('building_constraints', {})
        self.line_available_df = processed_data.get('line_available_df', pd.DataFrame())
        self.capa_qty_df = processed_data.get('capa_qty_df', pd.DataFrame())
        self.group_manager = ProjectGroupManager()

    # 그룹 내의 프로젝트들이 사용할 수 있는 라인의 총 용량 계산
    def calculate_capa_for_group(self, group_projects, line_available_df=None, capa_qty_df=None):
        if line_available_df is None:
            line_available_df = self.line_available_df
        if capa_qty_df is None:
            capa_qty_df = self.capa_qty_df
        
        total_capa = 0
        
        used_lines = self.group_manager.get_group_lines(group_projects, line_available_df)
        
        for line in used_lines:
            line_capa = 0
            
            if 'Line' in capa_qty_df.columns:
                line_row = capa_qty_df[capa_qty_df['Line'] == line]
                
                if not line_row.empty:
                    numeric_cols = [col for col in capa_qty_df.columns 
                                  if isinstance(col, int) or 
                                     (isinstance(col, str) and col.isdigit())]
                    
                    for col in numeric_cols:
                        if pd.notna(line_row[col].iloc[0]) and line_row[col].iloc[0] > 0:
                            line_capa += float(line_row[col].iloc[0])
                            
            total_capa += line_capa

        return total_capa

    # 분석 테이블 생성
    def create_analysis_table(self, line_available_df=None, capa_qty_df=None):
        if line_available_df is None:
            line_available_df = self.line_available_df
        if capa_qty_df is None:
            capa_qty_df = self.capa_qty_df
            
        project_groups = self.group_manager.create_project_groups(line_available_df)
        
        results = []
        
        for group_name, group_projects in project_groups.items():
            group_capa = self.calculate_capa_for_group(group_projects, line_available_df, capa_qty_df)
            group_total_mfg = 0
            group_total_sop = 0
            
            for project in group_projects:
                project_mfg = 0
                project_sop = 0
                
                for item in self.demand_items:
                    item_project = item.get('Project', '')
                    
                    if item_project == project:
                        project_mfg += float(item.get('MFG', 0))
                        sop_value = float(item.get('SOP', 0))
                        project_sop += max(0, sop_value)
                
                group_total_mfg += project_mfg
                group_total_sop += project_sop
                
                results.append({
                    'PJT Group': group_name,
                    'PJT': project,
                    'MFG': project_mfg,
                    'SOP': project_sop,
                    'CAPA': '',
                    'MFG/CAPA': '',
                    'SOP/CAPA': ''
                })
            
            mfg_capa_ratio = group_total_mfg / group_capa if group_capa > 0 else 0
            sop_capa_ratio = group_total_sop / group_capa if group_capa > 0 else 0
            
            results.append({
                'PJT Group': group_name,
                'PJT': 'Total',
                'MFG': group_total_mfg,
                'SOP': group_total_sop,
                'CAPA': group_capa,
                'MFG/CAPA': mfg_capa_ratio,
                'SOP/CAPA': sop_capa_ratio,
                'isOverMFG': mfg_capa_ratio > 1,
                'isOverSOP': sop_capa_ratio > 1
            })
        
        results_df = pd.DataFrame(results)
        
        sorted_results = []
        for group in results_df['PJT Group'].unique():
            group_data = results_df[results_df['PJT Group'] == group]
            total_row = group_data[group_data['PJT'] == 'Total']
            other_rows = group_data[group_data['PJT'] != 'Total'].sort_values('PJT')
            
            sorted_results.append(pd.concat([other_rows, total_row], ignore_index=True))
        
        final_df = pd.concat(sorted_results, ignore_index=True)
        
        final_df['status'] = ''
        for idx in final_df.index:
            if final_df.loc[idx, 'PJT'] == 'Total' and 'isOverMFG' in final_df.columns:
                if final_df.loc[idx, 'isOverMFG']:
                    final_df.loc[idx, 'status'] = '이상'
        
        return final_df

    # 요약 정보 생성
    def create_summary(self, analysis_df):
        total_rows = analysis_df[analysis_df['PJT'] == 'Total']
        
        summary = {
            '총 그룹 수': len(total_rows),
            '이상 그룹 수': len(total_rows[total_rows['status'] == '이상']),
            '전체 MFG': total_rows['MFG'].sum(),
            '전체 SOP': total_rows['SOP'].sum(),
            '전체 CAPA': total_rows['CAPA'].sum(),
            '전체 MFG/CAPA 비율': f"{total_rows['MFG'].sum() / total_rows['CAPA'].sum():.1%}"
                if total_rows['CAPA'].sum() > 0 else '0%',
            '전체 SOP/CAPA 비율': f"{total_rows['SOP'].sum() / total_rows['CAPA'].sum():.1%}"
                if total_rows['CAPA'].sum() > 0 else '0%'
        }
        return pd.Series(summary)

    # 결과를 데이터프레임 형식으로 출력
    def format_results_for_display(self, analysis_df):
        display_df = analysis_df.copy()
        
        for idx in display_df.index:
            if display_df.loc[idx, 'PJT'] == 'Total':
                if pd.notna(display_df.loc[idx, 'MFG/CAPA']):
                    display_df.loc[idx, 'MFG/CAPA'] = f"{display_df.loc[idx, 'MFG/CAPA']:.2f}"
                if pd.notna(display_df.loc[idx, 'SOP/CAPA']):
                    display_df.loc[idx, 'SOP/CAPA'] = f"{display_df.loc[idx, 'SOP/CAPA']:.2f}"
            else:
                display_df.loc[idx, 'MFG/CAPA'] = ''
                display_df.loc[idx, 'SOP/CAPA'] = ''
        
        for idx in display_df.index:
            if pd.notna(display_df.loc[idx, 'MFG']):
                mfg_value = int(display_df.loc[idx, 'MFG'])
                display_df.loc[idx, 'MFG'] = f"{mfg_value:,}"
                if display_df.loc[idx, 'PJT'] == 'Total' and 'isOverMFG' in analysis_df.columns:
                    if analysis_df.loc[idx, 'isOverMFG']:
                        display_df.loc[idx, 'MFG'] += " (초과)"
            
            if pd.notna(display_df.loc[idx, 'SOP']):
                sop_value = int(display_df.loc[idx, 'SOP'])
                display_df.loc[idx, 'SOP'] = f"{sop_value:,}"
                if display_df.loc[idx, 'PJT'] == 'Total' and 'isOverSOP' in analysis_df.columns:
                    if analysis_df.loc[idx, 'isOverSOP']:
                        display_df.loc[idx, 'SOP'] += " (초과)"
        
        for idx in display_df.index:
            if display_df.loc[idx, 'PJT'] == 'Total' and pd.notna(display_df.loc[idx, 'CAPA']):
                capa_value = int(display_df.loc[idx, 'CAPA'])
                display_df.loc[idx, 'CAPA'] = f"{capa_value:,}"
            else:
                display_df.loc[idx, 'CAPA'] = ''
        
        result_cols = ['PJT Group', 'PJT', 'MFG', 'SOP', 'CAPA', 'MFG/CAPA', 'SOP/CAPA']
        if 'status' in display_df.columns:
            result_cols.append('status')
        
        return display_df[result_cols]

    # 분석 결과를 로그로 출력
    def print_analysis_results(self, analysis_df=None, summary=None, display_df=None):
        if analysis_df is None:
            analysis_df = self.create_analysis_table()
        
        if display_df is None:
            display_df = self.format_results_for_display(analysis_df)
        
        if summary is None:
            summary = self.create_summary(analysis_df)
        
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        
        print("\n===== PJT Group / PJT별 MFG, SOP, CAPA 분석 테이블 =====")
        print(display_df.to_string(index=False))
        
        print("\n===== 요약 =====")
        print(summary.to_string())
        
        anomaly_groups = display_df[(display_df['PJT'] == 'Total') & (display_df['status'] == '이상')]
        if not anomaly_groups.empty:
            print('\n===== 이상 그룹 =====')

            for idx, row in anomaly_groups.iterrows():
                original_idx = analysis_df[(analysis_df['PJT Group'] == row['PJT Group']) & 
                                          (analysis_df['PJT'] == 'Total')].index[0]
                mfg = analysis_df.loc[original_idx, 'MFG']
                capa = analysis_df.loc[original_idx, 'CAPA']
                
                shortage = mfg - capa
                print(f"그룹: {row['PJT Group']}, MFG: {int(mfg):,}, CAPA: {int(capa):,}, 부족량: {int(shortage):,} (MFG-CAPA)")
            
            print(anomaly_groups.to_string(index=False))
        
        return {
            'analysis_df': analysis_df,
            'display_df': display_df,
            'summary': summary
        }

    # 전체 분석 수행 및 결과 반환
    def analyze(self):
        analysis_df = self.create_analysis_table()
        summary = self.create_summary(analysis_df)
        display_df = self.format_results_for_display(analysis_df)
        
        results = self.print_analysis_results(analysis_df, summary, display_df)
        
        return results