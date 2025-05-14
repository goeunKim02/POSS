from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
import pandas as pd
from app.views.components.common.custom_table import CustomTable

"""유지율 표시를 위한 테이블 위젯 기본 클래스"""
class MaintenanceTableWidget(CustomTable):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 라인별 배경색 정의
        self.group_colors = [
            QColor('#ffffff'),  # 흰색
            QColor('#f5f5f5'),  # 연한 회색
        ]
        self.setup_maintenance_style()
        
    """유지율 테이블 전용 스타일 설정"""
    def setup_maintenance_style(self):
        # CustomTable의 기본 스타일에 유지율 테이블 특화 스타일 추가
        additional_style = """
            QHeaderView::section {
                font-size: 20px;
            }
        """
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + additional_style)

    """헤더 설정 (CustomTable의 setup_header 메서드 오버라이드)"""
    def setup_header(self, header_labels):
        # CustomTable의 setup_header 호출
        super().setup_header(
            header_labels,
            fixed_columns={0: 80, 1: 80},  # Line과 Shift 열을 고정 너비로 설정
            resizable=False  # 나머지는 균등 분할
        )
        
    """그룹 헤더 행 생성"""
    def create_group_row(self, line, shift, prev_sum, curr_sum, maintenance_sum, group_index):
        # CustomTable의 add_custom_row 사용
        row_data = [
            line,
            shift,
            "",  # Item/RMC는 비워둠
            f"{prev_sum:,.0f}",
            f"{curr_sum:,.0f}",
            f"{maintenance_sum:,.0f}"
        ]
        
        # 라인별 그룹 헤더 배경색 선택
        group_header_colors = [
            QColor('#ffffff'),  # 흰색
            QColor('#f5f5f5'),  # 연한 회색
        ]
        bg_color = group_header_colors[group_index % len(group_header_colors)]

        # 스타일 정의
        styles = {}
        for col in range(6):
            style = {'background': bg_color}
            if col >= 3:  # 숫자 열은 우측 정렬
                style['alignment'] = Qt.AlignRight | Qt.AlignVCenter
            else:
                style['alignment'] = Qt.AlignCenter | Qt.AlignVCenter
            styles[col] = style
        
        self.add_custom_row(row_data, styles, is_header=True)
        
    """일반 데이터 행 생성"""
    def create_data_row(self, line="", shift="", item_text="", prev_plan=0, 
                       curr_plan=0, maintenance=0, is_modified=False, group_index=0):
        # CustomTable의 add_custom_row 사용
        row_data = [
            line,
            shift,
            item_text,
            f"{prev_plan:,.0f}",
            f"{curr_plan:,.0f}",
            f"{maintenance:,.0f}"
        ]
        
        # 라인별 배경색 선택
        bg_color = self.group_colors[group_index % len(self.group_colors)]
        
        # 스타일 정의
        styles = {}
        for col in range(6):
            style = {'background': bg_color}
            if col >= 3:  # 숫자 열은 우측 정렬
                style['alignment'] = Qt.AlignRight | Qt.AlignVCenter
            else:
                style['alignment'] = Qt.AlignCenter | Qt.AlignVCenter
            
            # 변경된 항목 강조
            if is_modified and col == 4:  # curr_plan 열
                style['foreground'] = QColor('#F8AC59')
                # 폰트 굵게 만들기
                font = QFont()
                font.setBold(True)
                style['font'] = font
            
            styles[col] = style
        
        self.add_custom_row(row_data, styles)
        
    """총계 행 생성"""
    def create_total_row(self, total_prev, total_curr, total_maintenance):
        row_data = [
            "Total",
            "",
            "",
            f"{total_prev:,.0f}",
            f"{total_curr:,.0f}",
            f"{total_maintenance:,.0f}"
        ]
        
        self.add_custom_row(row_data, is_total=True)
    
    """테이블에 데이터 채우기"""
    def _populate_table(self, df_data, modified_item_keys, item_field='Item'):
        """데이터를 테이블에 표시"""
        # 기존 데이터 초기화
        self.setRowCount(0)
        
        # Line-Shift별 그룹화
        groups = {}
        total_prev = 0
        total_curr = 0
        total_maintenance = 0

        # Line별로 그룹화
        line_shift_groups = {}
        
        for idx, row in df_data.iterrows():
            line = str(row['Line'])
            shift = str(row['Shift'])
            item_value = str(row[item_field])
            prev_plan = row['prev_plan'] if not pd.isna(row['prev_plan']) else 0
            curr_plan = row['curr_plan'] if not pd.isna(row['curr_plan']) else 0
            maintenance = row['maintenance'] if not pd.isna(row['maintenance']) else 0
            
            # 그룹 키 생성 (Line-Shift)
            group_key = f"{line}_{shift}" if shift else line
            
            if group_key not in groups:
                groups[group_key] = {
                    'line': line,
                    'shift': shift,
                    'items': [],
                    'prev_sum': 0,
                    'curr_sum': 0,
                    'maintenance_sum': 0
                }
            
            # 항목 추가
            groups[group_key]['items'].append({
                item_field.lower(): item_value,
                'prev_plan': prev_plan,
                'curr_plan': curr_plan, 
                'maintenance': maintenance
            })
            
            # 그룹 합계 업데이트
            groups[group_key]['prev_sum'] += prev_plan
            groups[group_key]['curr_sum'] += curr_plan
            groups[group_key]['maintenance_sum'] += maintenance
            
            # 전체 합계 업데이트
            total_prev += prev_plan
            total_curr += curr_plan
            total_maintenance += maintenance

            # 라인-교대 조합별 색상 인덱스 추적
            line_shift_key = f"{line}_{shift}"
            if line_shift_key not in line_shift_groups:
                line_shift_groups[line_shift_key] = len(line_shift_groups)  # 라인-교대 조합이 처음 나올 때 인덱스 부여
        
        # 테이블 행 추가
        for group_key, group_data in sorted(groups.items()):
            # 라인별 그룹 인덱스 사용
            line = group_data['line']
            shift = group_data['shift']
            line_shift_key = f"{line}_{shift}"  
            line_group_index = line_shift_groups[line_shift_key]

            # 그룹 헤더 행 추가
            self.create_group_row(
                group_data['line'],
                group_data['shift'],
                group_data['prev_sum'],
                group_data['curr_sum'],
                group_data['maintenance_sum'],
                line_group_index
            )
            
            # 데이터 행 추가
            item_key = item_field.lower()
            for item_data in sorted(group_data['items'], key=lambda x: x[item_key]):
                # 수정 여부 확인
                item_value = item_data[item_key]
                line = group_data['line']
                shift = group_data['shift']
                
                is_modified = False
                for key in modified_item_keys:
                    parts = key.split('_')
                    if len(parts) >= 3:
                        # 라인 코드 처리
                        if parts[0] in ["I", "D", "K", "M"] and len(parts) > 3:
                            key_line = f"{parts[0]}_{parts[1]}"
                            key_shift = parts[2]
                            key_item = "_".join(parts[3:])  # 나머지 모든 부분이 아이템
                        else:
                            key_line = parts[0]
                            key_shift = parts[1]
                            key_item = "_".join(parts[2:])  # 나머지 모든 부분이 아이템
                        
                        if item_field == 'Item' and key_line == line and key_shift == shift and key_item == item_value:
                            is_modified = True
                            break
                        elif item_field == 'RMC':
                            # RMC 비교는 부분 문자열 일치 검사
                            if key_line == line and key_shift == shift and (key_item == item_value or item_value in key_item or key_item in item_value):
                                is_modified = True
                                break
                
                # 데이터 행 생성
                self.create_data_row(
                    "",  # line은 그룹 헤더에만 표시
                    "",  # shift는 그룹 헤더에만 표시
                    item_value,
                    item_data['prev_plan'],
                    item_data['curr_plan'],
                    item_data['maintenance'],
                    is_modified,
                    line_group_index
                )
        
        # 총계 행 추가
        self.create_total_row(total_prev, total_curr, total_maintenance)


"""Item별 유지율 테이블 위젯"""
class ItemMaintenanceTable(MaintenanceTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "Item", "Previous", "Current", "Maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """아이템별 데이터 표시"""
        if df is None or df.empty:
            return
            
        df_data = df[df['Line'] != 'Total']  # Total 행만 필터링
        
        # 테이블에 데이터 표시
        self._populate_table(df_data, modified_item_keys, item_field='Item')


"""RMC별 유지율 테이블 위젯"""
class RMCMaintenanceTable(MaintenanceTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "RMC", "Previous", "Current", "Maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """RMC별 데이터 표시"""
        if df is None or df.empty:
            return
            
        df_data = df[df['Line'] != 'Total']  # Total 행만 필터링
        
        # 테이블에 데이터 표시
        self._populate_table(df_data, modified_item_keys, item_field='RMC')