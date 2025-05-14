from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont
import pandas as pd
from app.views.components.common.custom_table_widget import CustomTableWidget

"""유지율 표시를 위한 테이블 위젯 기본 클래스"""
class MaintenanceTableWidget(CustomTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(self)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # 라인별 배경색 정의
        self.group_colors = [
            QColor('#ffffff'),  # 흰색
            QColor('#f5f5f5'),  # 연한 회색
        ]
        self.setup_appearance()
        self.make_read_only()
        
    """테이블 위젯의 기본 스타일 설정"""
    def setup_appearance(self):
        self.setStyleSheet("""
        QTableWidget {
            border: none;
            gridline-color: #f0f0f0;
            outline: none;
        }
        QHeaderView::section {
            background-color: #1428A0;
            color: white;
            padding: 8px;
            font-weight: bold;
            font-size: 20px;
        }
        """)

        self.setAlternatingRowColors(False)

    """테이블을 읽기 전용으로 설정"""
    def make_read_only(self):
        # 테이블 전체를 읽기 전용으로 설정
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 선택 모드 설정 (행 단위 선택)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        # 포커스 정책 설정
        self.setFocusPolicy(Qt.StrongFocus)
        
    """헤더 설정"""
    def setup_header(self, header_labels):
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        
        # 열 너비 설정
        header = self.horizontalHeader()

        # 헤더 클릭/호버/선택 비활성화
        header.setSectionsClickable(False)  # 클릭 불가
        header.setHighlightSections(False)  # 선택 시 강조 표시 비활성화
    

        # Line과 Shift 열은 고정 너비로 설정
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Line 열
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Shift 열
        header.resizeSection(0, 80)  
        header.resizeSection(1, 80)   

         # 나머지 열은 자동 크기 조정
        for i in range(2, len(header_labels)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 헤더 정렬 설정
        for i in range(len(header_labels)):
            item = self.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignCenter)
        
        # 행 헤더 숨기기
        self.verticalHeader().setVisible(False)
        
    """그룹 헤더 행 생성"""
    def create_group_row(self, row, line, shift, prev_sum, curr_sum, maintenance_sum, group_index):
        # 행 추가
        self.insertRow(row)
        
        # 그룹 헤더 스타일 아이템 생성
        items = [
            QTableWidgetItem(line),
            QTableWidgetItem(shift),
            QTableWidgetItem(""),  # Item/RMC는 비워둠
            QTableWidgetItem(f"{prev_sum:,.0f}"),
            QTableWidgetItem(f"{curr_sum:,.0f}"),
            QTableWidgetItem(f"{maintenance_sum:,.0f}")
        ]

        # 라인별 그룹 헤더 배경색 선택
        group_header_colors = [
            QColor('#ffffff'),  # 흰색
            QColor('#f5f5f5'),  # 연한 회색
        ]
        bg_color = group_header_colors[group_index % len(group_header_colors)]
        
        # 각 셀에 스타일 적용
        for col, item in enumerate(items):
            # 읽기 전용 설정
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            # 그룹 헤더 스타일
            item.setBackground(QBrush(bg_color))
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            
            # 텍스트 정렬
            if col >= 3:  # 숫자 열
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            
            self.setItem(row, col, item)
        
        # 행 높이 설정
        self.setRowHeight(row, 35)
        
    """일반 데이터 행 생성"""
    def create_data_row(self, row, line="", shift="", item_text="", prev_plan=0, 
                       curr_plan=0, maintenance=0, is_modified=False, group_index=0):
        # 행 추가
        self.insertRow(row)
        
        # 데이터 아이템 생성
        items = [
            QTableWidgetItem(line),
            QTableWidgetItem(shift),
            QTableWidgetItem(item_text),
            QTableWidgetItem(f"{prev_plan:,.0f}"),
            QTableWidgetItem(f"{curr_plan:,.0f}"),
            QTableWidgetItem(f"{maintenance:,.0f}")
        ]

        # 라인별 배경색 선택
        bg_color = self.group_colors[group_index % len(self.group_colors)]
        
        # 각 셀에 스타일 적용
        for col, item in enumerate(items):
            # 읽기 전용 설정
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            # 배경색 설정
            item.setBackground(QBrush(bg_color))

            # 텍스트 정렬
            if col >= 3:  # 숫자 열
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            
            # 변경된 항목 강조
            if is_modified and col == 4:  # curr_plan 열
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QBrush(QColor('#F8AC59')))
            
            self.setItem(row, col, item)
        
        # 행 높이 설정
        self.setRowHeight(row, 25)
        
    """총계 행 생성"""
    def create_total_row(self, total_prev, total_curr, total_maintenance):
        row = self.rowCount()
        self.insertRow(row)
        
        # 총계 아이템 생성
        items = [
            QTableWidgetItem("Total"),
            QTableWidgetItem(""),
            QTableWidgetItem(""),
            QTableWidgetItem(f"{total_prev:,.0f}"),
            QTableWidgetItem(f"{total_curr:,.0f}"),
            QTableWidgetItem(f"{total_maintenance:,.0f}")
        ]
        
        # 각 셀에 스타일 적용
        for col, item in enumerate(items):
            # 읽기 전용 설정
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            # 총계 행 스타일
            item.setBackground(QBrush(QColor('#1428A0')))
            item.setForeground(QBrush(QColor('white')))
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            
            # 텍스트 정렬
            if col >= 3:  # 숫자 열
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            
            self.setItem(row, col, item)
        
        # 행 높이 설정
        self.setRowHeight(row, 35)
    
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
        current_row = 0
        for group_key, group_data in sorted(groups.items()):
            # 라인별 그룹 인덱스 사용
            line = group_data['line']
            shift = group_data['shift']
            line_shift_key = f"{line}_{shift}"  
            line_group_index = line_shift_groups[line_shift_key]

            # 그룹 헤더 행 추가
            self.create_group_row(
                current_row,
                group_data['line'],
                group_data['shift'],
                group_data['prev_sum'],
                group_data['curr_sum'],
                group_data['maintenance_sum'],
                line_group_index
            )
            current_row += 1
            
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
                    current_row,
                    "",  # line은 그룹 헤더에만 표시
                    "",  # shift는 그룹 헤더에만 표시
                    item_value,
                    item_data['prev_plan'],
                    item_data['curr_plan'],
                    item_data['maintenance'],
                    is_modified,
                    line_group_index
                )
                current_row += 1
        
        # 총계 행 추가
        self.create_total_row(total_prev, total_curr, total_maintenance)


"""Item별 유지율 테이블 위젯"""
class ItemMaintenanceTable(MaintenanceTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "Item", "prev_plan", "curr_plan", "maintenance"])
        
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
        self.setup_header(["Line", "Shift", "RMC", "prev_plan", "curr_plan", "maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """RMC별 데이터 표시"""
        if df is None or df.empty:
            return
            
        df_data = df[df['Line'] != 'Total']  # Total 행만 필터링
        
        # 테이블에 데이터 표시
        self._populate_table(df_data, modified_item_keys, item_field='RMC')