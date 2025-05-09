from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
import pandas as pd

"""유지율 표시를 위한 트리 위젯 기본 클래스"""
class MaintenanceTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_appearance()
        
    """트리 위젯의 기본 스타일 설정"""
    def setup_appearance(self):
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #dddddd;
                border: none;
                background-color: white;
                alternate-background-color: #f9f9f9;
                font-size: 24px;  
                outline: none;
                gridline-color: #dddddd;
            }
            QTreeWidget::item {
                height: 48px;  
                border-bottom: 1px solid #f0f0f0;
                padding-left: 8px;
                padding-right: 12px;
                border-right: 1px solid #e0e0e0;
            }
            QTreeWidget::item:selected {
                background-color: #f0f5ff;
                color: #1428A0;
                border: none;
                border-right: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: white;
                padding: 12px; 
                border: none;
                border-bottom: 2px solid #1428A0;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                color: #333333;
                font-size: 24px;  
            }
            QTreeView::branch {
                background-color: transparent;
                border: none;
            }
        """)
        self.setAlternatingRowColors(True)
        
    """헤더 설정"""
    def setup_header(self, header_labels):
        self.setHeaderLabels(header_labels)
        self.setColumnCount(len(header_labels))
        
        # 헤더 설정
        header = self.header()
        for i in range(len(header_labels)):
            if i < 3:  # 텍스트 컬럼은 내용에 맞게
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:  # 숫자 컬럼은 고정 크기
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                header.resizeSection(i, 150)
        
        # 헤더 정렬 설정
        for i in range(len(header_labels)):
            self.headerItem().setTextAlignment(i, Qt.AlignCenter)
        
        header.setStretchLastSection(False)
        
    """그룹 아이템 생성"""
    def create_group_item(self, line, shift, prev_sum, curr_sum, maintenance_sum):
        # line과 shift 로깅
        print(f"그룹 아이템 생성: line={line}, shift={shift}, prev_sum={prev_sum}, curr_sum={curr_sum}")

        group_item = QTreeWidgetItem([
            line,
            shift,
            "",  # Item/RMC는 비워둠
            f"{prev_sum:,.0f}",
            f"{curr_sum:,.0f}",
            f"{maintenance_sum:,.0f}"
        ])

        # 각 열의 텍스트 로깅
        for i in range(6):
            print(f"  열 {i}: '{group_item.text(i)}'")
        
        # 스타일 설정
        for i in range(6):
            group_item.setBackground(i, QBrush(QColor('#f0f5ff')))
            font = group_item.font(i)
            font.setBold(True)
            group_item.setFont(i, font)
        
        # 데이터 정렬
        group_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        group_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        group_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)

        # 그룹 아이템 크기 확인
        print(f"  그룹 아이템 상태: 보이기={group_item.isHidden()}, 높이={group_item.sizeHint(0).height()}")
        
        return group_item
        
    """자식 아이템 생성"""
    def create_child_item(self, item_text, prev_plan, curr_plan, maintenance, is_modified=False):
        child_item = QTreeWidgetItem([
            "",  # Line은 비워둠
            "",  # Shift는 비워둠
            item_text,
            f"{prev_plan:,.0f}",
            f"{curr_plan:,.0f}",
            f"{maintenance:,.0f}"
        ])
        
        # 데이터 정렬
        child_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        child_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        child_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        # 변경 여부에 따라 스타일 적용
        if is_modified:
            font = child_item.font(4)
            font.setBold(True)
            child_item.setFont(4, font)
            child_item.setForeground(4, QBrush(QColor('#F8AC59')))
            
        return child_item
        
    """총계 아이템 생성"""
    def create_total_item(self, total_prev, total_curr, total_maintenance):
        total_item = QTreeWidgetItem([
            "Total",
            "",
            "",
            f"{total_prev:,.0f}",
            f"{total_curr:,.0f}",
            f"{total_maintenance:,.0f}"
        ])
        
        # 스타일 설정
        for i in range(6):
            total_item.setBackground(i, QBrush(QColor('#1428A0')))
            total_item.setForeground(i, QBrush(QColor('white')))
            font = total_item.font(i)
            font.setBold(True)
            total_item.setFont(i, font)
            
        # 데이터 정렬
        total_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        total_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)
        
        return total_item
    

    """
    트리 위젯에 데이터를 채우는 메서드
    """
    def _populate_tree(self, df_data, modified_item_keys, item_field='Item'):
        # 데이터프레임이 비어있으면 종료
        if df_data is None or df_data.empty:
            return
        

        # 디버깅: 원본 데이터 확인
        print(f"트리 위젯 데이터 채우기 - 원본 행 수: {len(df_data)}")
        print(f"고유한 Line 값: {df_data['Line'].unique()}")
        print(f"고유한 Shift 값: {df_data['Shift'].unique()}")
        
        # 트리 위젯 초기화
        self.clear()
        
        # Line, Shift별로 그룹화
        line_shift_groups = {}
        
        for _, row in df_data.iterrows():
            line = row['Line']
            shift = row['Shift']
            
            # 총계 행은 별도로 처리
            if line == 'Total':
                continue
                
            # 그룹 키
            group_key = f"{line}_{shift}"
            
            # 그룹이 없으면 새로 생성
            if group_key not in line_shift_groups:
                line_shift_groups[group_key] = []
                
            # 그룹에 행 추가
            line_shift_groups[group_key].append(row)
        
        # Line-Shift 그룹별로 처리
        for group_key, rows in line_shift_groups.items():
            print(f"그룹 처리 중: {group_key}, 행 수: {len(rows)}")
            # 첫 번째 행에서 기본 정보 가져오기
            first_row = rows[0]
            line = first_row['Line']
            shift = str(first_row['Shift'])
            
            # 그룹의 총합 계산
            prev_sum = sum(row['prev_plan'] for row in rows)
            curr_sum = sum(row['curr_plan'] for row in rows)
            maintenance_sum = sum(row['maintenance'] for row in rows)
            
            # 그룹 아이템 생성
            group_item = self.create_group_item(line, shift, prev_sum, curr_sum, maintenance_sum)
            self.addTopLevelItem(group_item)
            
            # 개별 아이템 추가
            for row in rows:
                # 그룹 소계 행은 건너뛰기
                if 'is_group_total' in row and row['is_group_total']:
                    continue
                    
                # 아이템 정보
                item_text = row[item_field]
                prev_plan = row['prev_plan']
                curr_plan = row['curr_plan']
                maintenance = row['maintenance']
                
                # 수정된 아이템인지 확인
                is_modified = False
                if modified_item_keys:
                    # 아이템 키 비교
                    item_key = f"{line}_{shift}_{item_text}"
                    is_modified = item_key in modified_item_keys

                    # 디버깅: 수정 여부 확인
                    if is_modified:
                        print(f"수정된 아이템 발견: {item_key}")
                
                # 자식 아이템 생성
                child_item = self.create_child_item(item_text, prev_plan, curr_plan, maintenance, is_modified)
                group_item.addChild(child_item)
            
            # 그룹 노드 열기
            group_item.setExpanded(True)
        
        # 총계 행 추가 (마지막 행으로 가정)
        if not df_data.empty:
            last_row = None
            for _, row in df_data.iterrows():
                if row['Line'] == 'Total':
                    last_row = row
                    break
                    
            if last_row is not None:
                total_prev = last_row['prev_plan']
                total_curr = last_row['curr_plan']
                total_maintenance = last_row['maintenance']
                
                # 총계 아이템 생성
                total_item = self.create_total_item(total_prev, total_curr, total_maintenance)
                self.addTopLevelItem(total_item)


    # MaintenanceTreeWidget 클래스에 메서드 추가
    def update_visibility(self):
        """모든 아이템이 보이도록 업데이트"""
        # 모든 상위 레벨 아이템 처리
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                self.ensure_item_visible(item)
                # 자식 아이템도 처리
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child:
                        self.ensure_item_visible(child)
        
        # 모든 열 너비 최적화
        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)



"""Item별 유지율 트리 위젯"""
class ItemMaintenanceTree(MaintenanceTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "Item", "prev_plan", "curr_plan", "maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """아이템별 데이터 표시"""
        self.clear()
        
        if df is None or df.empty:
            return
            
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]
        
        # Line-Shift별 그룹화 및 데이터 표시 로직
        self._populate_tree(df_data, modified_item_keys, item_field='Item')


    """RMC별 유지율 트리 위젯"""
class RMCMaintenanceTree(MaintenanceTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_header(["Line", "Shift", "RMC", "prev_plan", "curr_plan", "maintenance"])
        
    def populate_data(self, df, modified_item_keys):
        """RMC별 데이터 표시"""
        self.clear()
        
        if df is None or df.empty:
            return
            
        # 데이터 필터링 - 총계 행 제외
        df_data = df[:-2]
        
        # Line-Shift별 그룹화 및 데이터 표시 로직
        self._populate_tree(df_data, modified_item_keys, item_field='RMC')



