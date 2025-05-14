from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
import pandas as pd
from app.analysis.output.capa_ratio import CapaRatioAnalyzer
from app.models.common.fileStore import FilePaths
from app.utils.fileHandler import load_file

"""결과 요약 정보 표시 위젯"""
class SummaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_capacity_data = {}  # 라인별 생산능력 
        self.line_utilization_data = {}  # 라인별 가동률 
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10 ,10, 10)
        main_layout.setSpacing(10)

        # 요약 테이블
        self.summary_table = QTableWidget()
        self.setup_table_style()
        main_layout.addWidget(self.summary_table)


    """테이블 스타일 설정"""
    def setup_table_style(self):
        self.summary_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                border: 1px solid #D0D0D0;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #1428A0;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #0C1A6B;
                font-size: 12px;
            }
            QTableWidget::item {
                background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
        """)
        
        # 헤더 설정
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.verticalHeader().setVisible(False)
        # self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)


    """master 파일에서 라인별 생산능력 로드"""
    def load_line_capacity_data(self):
        try:
            master_file = FilePaths.get('master_excel_file')
            if not master_file:
                print("마스터 파일 경로를 찾을 수 없습니다.")
                return
            
            # capa_qty 시트 로드
            capa_data = load_file(master_file, sheet_name='capa_qty')
            if isinstance(capa_data, dict):
                df_capa_qty = capa_data.get('capa_qty', pd.DataFrame())
            else:
                df_capa_qty = capa_data
            
            if df_capa_qty.empty:
                print("capa_qty 데이터가 비어있습니다.")
                return
            
            # 라인별 전체 생산능력 계산 (라인별 합계)
            for _, row in df_capa_qty.iterrows():
                if 'Line' in row:
                    line = row['Line']
                    total_capacity = 0
                    for col in df_capa_qty.columns:
                        if isinstance(col, (int, str)) and str(col).isdigit():
                            if pd.notna(row[col]):
                                total_capacity += row[col]
                    self.line_capacity_data[line] = total_capacity
            print(f"라인별 생산능력 로드 완료: {len(self.line_capacity_data)}개 라인")
            
        except Exception as e:
            print(f"라인별 생산능력 로드 오류: {e}")

    """라인별 가동률 계산"""
    def calculate_line_utilization(self, result_data):
        try:
            # 라인별 생산량 계산
            line_production = result_data.groupby('Line')['Qty'].sum()

            # 라인별 가동률 계산
            for line, production in line_production.items():
                if line in self.line_capacity_data:
                    capacity = self.line_capacity_data[line]
                    if capacity > 0:
                        utilization = (production / capacity) * 100
                        self.line_utilization_data[line] = utilization
                    else:
                        self.line_utilization_data[line] = 0
                else:
                    # 생산능력 정보가 없으면 0으로 설정 
                    self.line_utilization_data[line] = 0
            
            print(f"라인별 가동률 계산 완료: {len(self.line_utilization_data)}개 라인")
            
        except Exception as e:
            print(f"라인별 가동률 계산 오류: {e}")


    """결과 분석 및 테이블 업데이트"""
    def run_analysis(self, result_data):
        if result_data is None or result_data.empty:
            self.clear_table()
            return
        
        try:
            # 1. 라인별 생산능력 및 가동률 
            self.load_line_capacity_data()
            self.calculate_line_utilization(result_data)

            # 2. 제조동별 비율 계산
            capa_ratios = CapaRatioAnalyzer.analyze_capa_ratio(data_df=result_data, is_initial=True)

            # 3. 상세 정보 추출
            summary_data = self.create_summary(result_data, capa_ratios)
            
            # 4. 테이블 업데이트
            self.update_table(summary_data)

        except Exception as e:
            print(f"summary 요약 중 에러 : {e}")


    """요약 데이터 생성"""
    def create_summary(self, result_data, capa_ratios):
        # 제조동별 데이터 추출
        result_data = result_data.copy()
        result_data['Building'] = result_data['Line'].str.split('_').str[0]

        # 제조동별 생산량 집계
        building_qty = result_data.groupby('Building')['Qty'].sum()

        # 제조동별 라인 정보
        building_lines = result_data.groupby('Building')['Line'].nunique()

        # 전체 합계 계산
        total_qty = result_data['Qty'].sum()
        total_capacity = sum(self.line_capacity_data.values())
        total_utilization = (total_qty / total_capacity * 100) if total_capacity > 0 else 0

        # 제조동별 프로젝트-지역 정보 추출
        project_region_data = []

        # 전체 Total 행 먼저 추가
        project_region_data.append({
            'Building(Portion)': 'Total',
            'Line': '-',
            'Capa': f"{total_capacity:,}" if total_capacity > 0 else '',
            'Line_Qty': f"{total_qty:,}",  
            'Utilization(%)': f"{total_utilization:.1f}%" if total_utilization > 0 else '',
            'Project': '',
            'Region': '',
            'Pjt_Qty': '',  # 프로젝트별 수량은 총합행에서는 빈값
            'Qty_raw': total_qty,  # 정렬용
            'is_total': True  # Total 행 표시용
        })

        # 각 제조동별로 처리
        buildings = ['I', 'D', 'K', 'M']

        for building in buildings:
            building_data = result_data[result_data['Building'] == building]

            if building_data.empty:
                continue

            # 제조동 전체 정보
            total_qty = building_qty.get(building, 0)
            building_ratio = capa_ratios.get(building, 0)

            # 제조동별 총 생산능력
            building_total_capacity = 0
            building_lines_in_data = building_data['Line'].unique()
            for line in building_lines_in_data:
                if line in self.line_capacity_data:
                    building_total_capacity += self.line_capacity_data[line]
            
            # 제조동별 가동률 계산
            building_utilization = 0
            if building_total_capacity > 0:
                building_utilization = (total_qty / building_total_capacity) * 100

            # 제조동 별 total 행
            project_region_data.append({
                'Building(Portion)' : f"{building}({building_ratio:.1f})",
                'Line' : 'Total',
                'Capa' : f"{building_total_capacity:,}" if building_total_capacity > 0 else '', 
                'Line_Qty': f"{total_qty:,}",  # 라인별 총합 컬럼
                'Utilization(%)': f"{building_utilization:.1f}%" if building_utilization > 0 else '',
                'Project': '-',
                'Region': '-',
                'Pjt_Qty': '-',  # 프로젝트별 수량은 총합행에서는 빈값
                'Qty_raw': total_qty,  # 정렬용 
                'is_total': True  # Total 행 표시용
            })

            # 라인별 상세정보
            line_data = building_data.groupby('Line').agg({
                'Qty': 'sum',
                'Project' : lambda x: list(x.unique()),  # 해당 라인의 모든 프로젝트
                'Item': 'first'  # 지역 추출용
            }).reset_index()

            # 라인을 수량순으로 정렬
            line_data = line_data.sort_values('Qty', ascending=False)

            for _, row in line_data.iterrows():
                line = row['Line']
                line_qty = row['Qty']
                projects = sorted(row['Project'])  # 프로젝트명 정렬

                # 라인별 생산능력과 가동률
                line_capacity = self.line_capacity_data.get(line, 0)
                line_utilization = self.line_utilization_data.get(line, 0)

                # 프로젝트별 세부정보 
                for i, project in enumerate(projects):
                    project_data = building_data[
                        (building_data['Line'] == line) &
                        (building_data['Project'] == project)
                    ]

                    if not project_data.empty:
                        project_qty = project_data['Qty'].sum()

                        # 지역 추출 (첫번째 아이템에서)
                        first_item = str(project_data['Item'].iloc[0])
                        region = ''
                        try:
                            proj_idx = first_item.find(project)
                            if proj_idx >= 0 and proj_idx + len(project) < len(first_item):
                                region_char = first_item[proj_idx + len(project)]
                                if region_char.isupper() and region_char.isalpha():
                                    region = region_char
                        except:
                            region = ''

                        # 첫 번째 프로젝트에만 라인 정보와 Capa, Utilization 표시
                        if i == 0:
                            project_region_data.append({
                                'Building(Portion)': '',
                                'Line': f"  {line}",  # 들여쓰기
                                'Capa': f"{line_capacity:,}" if line_capacity > 0 else '',
                                'Line_Qty': f"{line_qty:,}",  # 라인별 총수량
                                'Utilization(%)': f"{line_utilization:.1f}%" if line_utilization > 0 else '',
                                'Project': project,
                                'Region': region,
                                'Pjt_Qty': f"{project_qty:,}",  # 프로젝트별 수량
                                'Qty_raw': project_qty,  # 정렬용
                                'is_total': False
                            })
                        else:
                            # 두 번째 프로젝트부터는 빈 라인으로 표시
                            project_region_data.append({
                                'Building(Portion)': '',
                                'Line': f"  {line}",  # 같은 라인임을 명시 (병합을 위해)
                                'Capa': '',
                                'Line_Qty': '',  # 두 번째 프로젝트부터는 빈값
                                'Utilization(%)': '',
                                'Project': project,
                                'Region': region,
                                'Pjt_Qty': f"{project_qty:,}",  # 프로젝트별 수량만 표시
                                'Qty_raw': project_qty,  # 정렬용
                                'is_total': False
                            })
            
        # DataFrame으로 변환 후 정렬
        summary_df = pd.DataFrame(project_region_data)

        if summary_df.empty:
            return pd.DataFrame()
        
        # 정렬용 컬럼 제거
        summary_df = summary_df.drop('Qty_raw', axis=1)
        
        return summary_df
    

    """테이블 업데이트"""
    def update_table(self, summary_df):
        if summary_df.empty:
            self.clear_table()
            return
        
        # 표시용 컬럼만 추출 (is_total은 제외하고 표시)
        display_columns = [col for col in summary_df.columns if col != 'is_total']
        display_df = summary_df[display_columns]

        # 테이블 설정
        self.summary_table.setRowCount(len(display_df))
        self.summary_table.setColumnCount(len(display_df.columns))

        # 헤더 설정
        self.summary_table.setHorizontalHeaderLabels(display_df.columns.tolist())

        # 제조동별 병합 
        building_spans = {}
        
        # 제조동별 행 범위 찾기
        for row_idx, (_, row) in enumerate(summary_df.iterrows()):
            building_portion = row['Building(Portion)']
            
            if building_portion and '(' in building_portion and building_portion != 'Total':
                # Building(Portion) 열에 값이 있는 경우 (제조동 Total 행)
                building_name = building_portion.split('(')[0]
                
                # 해당 제조동의 시작 행 저장
                building_spans[building_name] = {
                    'start_row': row_idx,
                    'end_row': row_idx,  # 일단 현재 행으로 설정
                    'rows': [row_idx]
                }
                
                # 다음 제조동이 나올 때까지의 모든 행 찾기
                for next_idx in range(row_idx + 1, len(summary_df)):
                    next_row = summary_df.iloc[next_idx]
                    next_building = next_row['Building(Portion)']
                    
                    # 다음 제조동의 Total 행이 나오면 중단
                    if next_building and '(' in next_building:
                        break
                    
                    # 현재 제조동에 속하는 행 추가
                    building_spans[building_name]['end_row'] = next_idx
                    building_spans[building_name]['rows'].append(next_idx)

        # 제조동별 셀 병합
        for building_name, span_info in building_spans.items():
            start_row = span_info['start_row']
            end_row = span_info['end_row']
            row_count = end_row - start_row + 1
            
            if row_count > 1:  # 2개 이상의 행이 있는 경우만 병합
                # Building(Portion) 컬럼 (컬럼 인덱스 0) 병합
                self.summary_table.setSpan(start_row, 0, row_count, 1)
                
                # 병합된 셀의 정렬을 중앙으로 설정
                item = self.summary_table.item(start_row, 0)
                if item:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # 라인별 행 정보 수집 (병합을 위해)
        line_spans = {}

        # 데이터 입력
        for row_idx, (_, row) in enumerate(summary_df.iterrows()):
            display_row = display_df.iloc[row_idx]

            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if pd.notna(value) else "")

                # 텍스트 정렬 설정
                if col_idx in [2, 3, 4]:  # Capa, Qty, Utilization 컬럼 (우측 정렬)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

                # Total 행 스타일 적용 (중요한 부분!)
                if row.get('is_total', False):
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                    # 배경색을 회색으로 설정
                    item.setBackground(QBrush(QColor("#E8E8E8")))
                    # 텍스트 색상도 진하게
                    item.setForeground(QBrush(QColor("#333333")))
                
                # 스타일 적용
                # self.apply_cell_style(item, row_idx, col_idx, row)
                
                self.summary_table.setItem(row_idx, col_idx, item)

        # 두 번째 패스: 라인별 정보 수집 (들여쓰기 제거된 실제 라인명으로)
        for row_idx, (_, row) in enumerate(summary_df.iterrows()):
            line_name = row['Line'].strip()  # 들여쓰기 제거
            
            # 실제 라인명인지 확인 (공백이 아니고, Total이 아니며, 실제 라인 형태인지)
            if line_name and line_name != 'Total' and '_' in line_name:
                if line_name not in line_spans:
                    line_spans[line_name] = {
                        'start_row': row_idx,
                        'rows': [row_idx],
                        'capa': row['Capa'],
                        'line_qty': row['Line_Qty'],
                        'utilization': row['Utilization(%)']
                    }
                else:
                    line_spans[line_name]['rows'].append(row_idx)

        # 셀 병합 적용
        for line_name, span_info in line_spans.items():
            rows = span_info['rows']
            
            if len(rows) > 1:  # 2개 이상의 행이 있는 라인만 병합
                start_row = min(rows)
                row_count = len(rows)
                
                # 연속된 행인지 확인
                if rows == list(range(start_row, start_row + row_count)):
                    # Line 컬럼 (컬럼 인덱스 1) 병합
                    self.summary_table.setSpan(start_row, 1, row_count, 1)
                    
                    # Capa 컬럼 (컬럼 인덱스 2) 병합
                    if span_info['capa']:  # Capa 값이 있는 경우만 병합
                        self.summary_table.setSpan(start_row, 2, row_count, 1)
                    
                    # Line_Qty 컬럼 (컬럼 인덱스 3) 병합
                    if span_info['line_qty']:  # Line_Qty 값이 있는 경우만 병합
                        self.summary_table.setSpan(start_row, 3, row_count, 1)
                    
                    # Utilization 컬럼 (컬럼 인덱스 4) 병합
                    if span_info['utilization']:  # Utilization 값이 있는 경우만 병합
                        self.summary_table.setSpan(start_row, 4, row_count, 1)
                    
                    # 병합된 셀의 정렬을 중앙으로 설정
                    for col_idx in [1, 2, 3, 4]:
                        item = self.summary_table.item(start_row, col_idx)
                        if item:
                            if col_idx == 1:  # Line 컬럼은 센터 정렬
                                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                            else:  # 나머지는 우측 정렬
                                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # 행 높이 조정
        for row in range(len(summary_df)):
            self.summary_table.setRowHeight(row, 30)
            
        # 첫 번째 컬럼은 조금 더 넓게
        self.summary_table.setColumnWidth(0, 150)


    # """셀 스타일 적용"""
    # def apply_cell_style(self, item, row_idx, col_idx, row_data):
    #     # Total 행에만 배경색과 폰트 적용
    #     if row_data.get('is_total', False):
    #         font = QFont()
    #         font.setBold(True)
    #         item.setFont(font)
    #         item.setBackground(QBrush(QColor("#F0F0F0")))
        

    """테이블 초기화"""
    def clear_table(self):
        self.summary_table.setRowCount(0)
        self.summary_table.setColumnCount(0)



