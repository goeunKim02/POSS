from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog,
                             QLineEdit, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QCursor
import pandas as pd
from .item_grid_widget import ItemGridWidget
from .item_position_manager import ItemPositionManager
from app.views.components.result_components.enhanced_message_box import EnhancedMessageBox

class ModifiedLeftSection(QWidget):
    data_changed = pyqtSignal(pd.DataFrame)
    item_selected = pyqtSignal(object, object)  # 아이템 선택 이벤트 (아이템, 컨테이너)
    item_data_changed = pyqtSignal(object, dict)  # 아이템 데이터 변경 이벤트
    cell_moved = pyqtSignal(object, dict, dict)  # 이전 아이템, 이전 데이터, 새 데이터
    validation_error_occured = pyqtSignal(dict, str)  
    validation_error_resolved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.original_data = None
        self.grouped_data = None
        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.time_periods = ['Day', 'Night']
        self.pre_assigned_items = set()  # 사전할당된 아이템 저장
        self.shipment_failure_items = {}  # 출하 실패 아이템 저장
        self.init_ui()

        # 아이템 이동을 위한 정보 저장
        self.row_headers = []

        # 검색 관련 변수
        self.search_active = False
        self.last_search_text = ''
        self.all_items = []

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 컨트롤 레이아웃
        first_control_layout = QHBoxLayout()
        first_control_layout.setContentsMargins(10, 5, 10, 5)

        # 엑셀 파일 불러오기 버튼
        self.load_button = QPushButton("Import Excel file")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #004C99;
            }
            QPushButton:pressed {
                background-color: #003366;
            }
        """)
        self.load_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.load_button.clicked.connect(self.load_excel_file)
        first_control_layout.addWidget(self.load_button)

        # 원본 복원 버튼 
        self.reset_button = QPushButton("Reset to Original")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        self.reset_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_button.clicked.connect(self.reset_to_original)
        self.reset_button.setEnabled(False)
        first_control_layout.addWidget(self.reset_button)

        first_control_layout.addSpacing(20)

        search_label = QLabel('model search : ')
        search_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
                font-size: 14px;
                border: None;
            }
        """)
        first_control_layout.addWidget(search_label)

        # 검색 필드
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('searching...')
        self.search_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #1428A0;
                font-size: 14px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border: 1px solid #1428A0;
            }
        """)
        self.search_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search_field.setFixedHeight(36)
        self.search_field.returnPressed.connect(self.search_items)
        first_control_layout.addWidget(self.search_field)

        # 검색 버튼
        self.search_button = QPushButton('Search')
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #004C99;
            }
            QPushButton:pressed {
                background-color: #003366;
            }
        """)

        self.search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_button.clicked.connect(self.search_items)
        first_control_layout.addWidget(self.search_button)

        # 검색 초기화 버튼
        self.clear_search_button = QPushButton('Search Reset')
        self.clear_search_button.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        self.clear_search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setEnabled(False)
        first_control_layout.addWidget(self.clear_search_button)

        main_layout.addLayout(first_control_layout)

        # 검색 상태 표시 레이아웃
        self.search_status_layout = QHBoxLayout()
        self.search_status_layout.setContentsMargins(10, 0, 10, 5)

        # 검색 결과 수 표시
        self.search_result_label = QLabel('')
        self.search_result_label.setStyleSheet("""
            QLabel {
                color: #1428A0;
                font-weight: bold;
                font-size: 13px;
                border: None;
            }
        """)

        self.search_status_layout.addStretch(1)
        self.search_status_layout.addWidget(self.search_result_label)

        self.search_result_label.hide()
        main_layout.addLayout(self.search_status_layout)

        # 새로운 그리드 위젯 추가
        self.grid_widget = ItemGridWidget()
        self.grid_widget.itemSelected.connect(self.on_grid_item_selected)  # 아이템 선택 이벤트 연결
        self.grid_widget.itemDataChanged.connect(self.on_item_data_changed)  # 아이템 데이터 변경 이벤트 연결
        self.grid_widget.itemCreated.connect(self.register_item)

        main_layout.addWidget(self.grid_widget, 1)

    """
    새로 생성된 아이템 등록
    """
    def register_item(self, item) :
        if item not in self.all_items :
            self.all_items.append(item)

            if self.search_active and self.last_search_text :
                self.apply_search_to_item(item, self.last_search_text)

    """
    검색 기능 실행
    """
    def search_items(self) :
        search_text = self.search_field.text().strip().lower()

        if not search_text :
            self.clear_search()
            return
        
        self.search_active = True
        self.last_search_text = search_text
        self.clear_search_button.setEnabled(True)

        visible_count = 0
        invalid_items = []

        for item in self.all_items[:] :
            try:
                if self.apply_search_to_item(item, search_text):
                    visible_count += 1
            except RuntimeError:
                invalid_items.append(item)
            except Exception as e:
                print(f"검색 중 오류 발생: {e}")
        
        for item in invalid_items:
            if item in self.all_items:
                self.all_items.remove(item)

        self.grid_widget.update_container_visibility()

        if visible_count > 0 :
            self.search_result_label.setText(f'result : {visible_count}')
        else :
            self.search_result_label.setText('result : No matching items')
        
        self.search_result_label.show()

    """
    아이템에 검색 조건 적용
    """
    def apply_search_to_item(self, item, search_text) :
        try :
            if not item or not hasattr(item, 'item_data') or not item.item_data :
                return False
            
            try:
                _ = item.isVisible()
            except RuntimeError:
                if item in self.all_items:
                    self.all_items.remove(item)

                return False
            
            item_code = str(item.item_data.get('Item', '')).lower()
            is_match = search_text in item_code

            item.setVisible(is_match)

            container = item.parent()

            if container :
                if hasattr(container, 'update_visibility') :
                    container.update_visibility()

            return is_match
        except RuntimeError:
            return False
        except Exception as e:
            print(f"아이템 검색 중 오류: {e}")
            return False
    
    """
    검색 초기화
    """
    def clear_search(self) :
        if not self.search_active :
            return
        
        self.search_active = False
        self.last_search_text = ''
        self.search_field.clear()
        self.clear_search_button.setEnabled(False)
        self.search_result_label.hide()

        for item in self.all_items :
            item.setVisible(True)
        
        self.grid_widget.update_container_visibility()

    """그리드에서 아이템이 선택되면 호출되는 함수"""
    def on_grid_item_selected(self, selected_item, container):
        self.item_selected.emit(selected_item, container)

    """아이템 데이터가 변경되면 호출되는 함수"""
    def on_item_data_changed(self, item, new_data, changed_fields=None):

        if not item or not new_data or not hasattr(item, 'item_data'):
            print("아이템 또는 데이터가 없음")
            return
        
        # 이전 데이터 저장 (시각화 업데이트용)
        old_data = item.item_data.copy() if hasattr(item, 'item_data') else {}
        
        if changed_fields:
            old_data_for_validation = old_data.copy()

            for field, change_info in changed_fields.items():
                if field.startswith('_validation') or field.startswith('_drop_pos'):
                    continue

                if field not in ['_drop_pos'] and isinstance(change_info, dict) and 'from' in change_info:
                        old_data_for_validation[field] = change_info['from']
                
            old_data = old_data_for_validation  # 복원된 데이터를 사용

        if hasattr(self, 'validator'):
            is_move = False
            source_line = None
            source_time = None

            if 'Line' in changed_fields or 'Time' in changed_fields:
                is_move = True
                source_line = old_data.get('Line')
                source_time = old_data.get('Time')

        # 검증 실행
        try:
            valid, message = self.validator.validate_adjustment(
                new_data.get('Line'),
                new_data.get('Time'),
                new_data.get('Item', ''),
                new_data.get('Qty', 0),
                source_line if is_move else None,
                source_time if is_move else None
            )

            if not valid:
                validation_failed = True
                validation_error_message = message
                
                # 시그널 발생
                self.validation_error_occured.emit(new_data, message)
            else:
                # changed_fields에서 이전 값 복원
                old_data_for_removal = old_data.copy()
                if changed_fields:
                    for field, change_info in changed_fields.items():
                        if field not in ['_drop_pos'] and isinstance(change_info, dict) and 'from' in change_info:
                            old_data_for_removal[field] = change_info['from']

                self.validation_error_resolved.emit(old_data_for_removal)

        except Exception as e:
            print(f"검증 오류 발생: {e}")
        
        # Line 또는 Time 값 변경 체크
        position_change_needed = False

        if changed_fields:
            # Time 변경 확인
            if 'Time' in changed_fields:
                position_change_needed = True
                time_change = changed_fields['Time']
                old_time = time_change['from']
                new_time = time_change['to']

            # Line 변경 확인
            if 'Line' in changed_fields:
                position_change_needed = True
                line_change = changed_fields['Line']
                old_line = line_change['from']
                new_line = line_change['to']
            else:
                print("Line 변경 없음")

        # 위치 변경이 필요한 경우
        if position_change_needed:
            old_container = item.parent() if hasattr(item, 'parent') else None

            if not isinstance(old_container, QWidget):
                return

            # 변경된 Line과 Time에 따른 새 위치 계산
            line = new_data.get('Line')
            new_time = new_data.get('Time')

            if not line or not new_time:
                return

            # 새 위치 계산을 위한 정보 가져오기
            old_time = old_time if 'Time' in changed_fields else new_time
            old_line = old_line if 'Line' in changed_fields else line

            old_day_idx, old_shift = ItemPositionManager.get_day_and_shift(old_time)
            new_day_idx, new_shift = ItemPositionManager.get_day_and_shift(new_time)

            # 새 행/열 인덱스 계산
            old_row_key = ItemPositionManager.get_row_key(old_line, old_shift)
            new_row_key = ItemPositionManager.get_row_key(line, new_shift)

            old_row_idx = ItemPositionManager.find_row_index(old_row_key, self.row_headers)
            new_row_idx = ItemPositionManager.find_row_index(new_row_key, self.row_headers)

            old_col_idx = ItemPositionManager.get_col_from_day_idx(old_day_idx, self.days)
            new_col_idx = ItemPositionManager.get_col_from_day_idx(new_day_idx, self.days)

            # 유효한 인덱스인 경우 아이템 이동
            if old_row_idx >= 0 and old_col_idx >= 0 and new_row_idx >= 0 and new_col_idx >= 0:

                # 이전 위치에서 아이템 제거
                if old_container:
                    old_container.removeItem(item)

                # 새 위치에 아이템 추가
                item_text = ""
                if 'Item' in new_data:
                    item_text = str(new_data['Item'])

                    if 'Qty' in new_data and pd.notna(new_data['Qty']):
                        item_text += f" ({new_data['Qty']})"

                # 드롭 위치 정보 가져오기
                drop_index = 0

                if changed_fields and '_drop_pos' in changed_fields:
                    try:
                        drop_pos_info = changed_fields['_drop_pos']

                        x = int(drop_pos_info['x'])
                        y = int(drop_pos_info['y'])

                        # 새 컨테이너 가져오기
                        target_container = self.grid_widget.containers[new_row_idx][new_col_idx]

                        # 로컬 위치로 변환하여 드롭 인덱스 계산
                        drop_index = target_container.findDropIndex(QPoint(x, y))
                    except Exception as e:
                        drop_index = 0

                # 새 위치에 아이템 추가
                new_item = self.grid_widget.addItemAt(new_row_idx, new_col_idx, item_text, new_data,drop_index)

                if new_item:
                    # 복원 버튼 활성화
                    self.mark_as_modified()

                    # 아이템이 사전할당된 경우
                    if 'Item' in new_data and new_data['Item'] in self.pre_assigned_items:
                        new_item.set_pre_assigned_status(True)
                        
                    # 아이템이 출하 실패인 경우
                    if 'Item' in new_data and new_data['Item'] in self.shipment_failure_items:
                        failure_info = self.shipment_failure_items[new_data['Item']]
                        new_item.set_shipment_failure(True, failure_info.get('reason', 'Unknown reason'))

                    # 자재부족 상태 적용 (필요한 경우)
                    if hasattr(self, 'current_shortage_items') and 'Item' in new_data and new_data['Item'] in self.current_shortage_items:
                        shortage_info = self.current_shortage_items[new_data['Item']]
                        new_item.set_shortage_status(True, shortage_info)

                    # 셀 이동 이벤트 발생 (시각화 차트 업데이트)
                    self.cell_moved.emit(new_item, old_data, new_data)
                    return  
                else:
                    print("새 아이템 생성 실패")
                    return

        else:
            # 위치 변경이 필요 없는 경우 - 데이터만 업데이트
            if hasattr(item, 'update_item_data'):
                success, error_message = item.update_item_data(new_data)
                if not success:
                    print(f"아이템 데이터 업데이트 실패: {error_message}")
                    return

            # 데이터 변경 성공 시
            self.mark_as_modified()

            # 상위 위젯에 이벤트 전달
            self.item_data_changed.emit(item, new_data)
        

    """엑셀 파일 로드"""
    def load_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            try:
                self.clear_all_items()

                self.data = pd.read_excel(file_path)
                self.update_table_from_data()

                EnhancedMessageBox.show_validation_success(self, "File Loaded Successfully",
                                        f"File has been successfully loaded.\nRows: {self.data.shape[0]}, Columns: {self.data.shape[1]}")
            except Exception as e:
                EnhancedMessageBox.show_validation_error(self, "File Loding Error", f"An error occurred while loading the file.\n{str(e)}")

    """
    아이템 목록과 그리드 초기화하는 메서드
    """
    def clear_all_items(self) :
        self.all_items = []
        self.search_active = False
        self.last_search_text = ''
        self.search_field.clear()
        self.clear_search_button.setEnabled(False)
        self.search_result_label.hide()

        if hasattr(self, 'grid_widget'):
            self.grid_widget.clearAllItems()

    """엑셀 파일에서 데이터를 읽어와 테이블 업데이트"""
    def update_table_from_data(self):
        if self.data is None:
            return

        self.group_data()

        # 데이터 변경 신호 발생
        self.data_changed.emit(self.data)

    """Line과 Time으로 데이터 그룹화하고 개별 아이템으로 표시"""
    def group_data(self): 
        if self.data is None or 'Line' not in self.data.columns or 'Time' not in self.data.columns:
            EnhancedMessageBox.show_validation_error(self, "Grouping Failed",
                                "Data is missing or does not contain 'Line' or 'Time' columns.\nPlease load data with the required columns.")
            return

        try:
            # Line과 Time 값 추출
            lines = sorted(self.data['Line'].unique())
            times = sorted(self.data['Time'].unique())

            # 여기서는 원래 Line 값을 유지하고, 표시만 바뀌도록 처리
            # 내부적으로는 원래 라인명(예: "1", "A" 등)을 사용하되,
            # 화면에는 "ㅣ-01" 형식으로 표시

            # 교대 시간 구분
            shifts = {}
            for time in times:
                if int(time) % 2 == 1:
                    shifts[time] = "Day"
                else:
                    shifts[time] = "Night"

            # 라인별 교대 정보
            line_shifts = {}
            for line in lines:
                line_shifts[line] = ["Day", "Night"]

            # 행 헤더
            self.row_headers = []
            for line in lines:
                for shift in ["Day", "Night"]:
                    self.row_headers.append(f"{line}_({shift})")

            self.grid_widget.setupGrid(
                rows=len(self.row_headers),
                columns=len(self.days),
                row_headers=self.row_headers,
                column_headers=self.days,
                line_shifts=line_shifts  # 새로운 라인별 교대 정보 전달
            )

            # 각 요일과 라인/교대 별로 데이터 수집 및 그룹화
            for _, row_data in self.data.iterrows():
                if 'Line' not in row_data or 'Time' not in row_data:
                    continue

                line = row_data['Line']
                time = row_data['Time']
                shift = shifts[time]
                day_idx = (int(time) - 1) // 2

                if day_idx >= len(self.days):
                    continue

                day = self.days[day_idx]
                row_key = f"{line}_({shift})"

                # Item 정보가 있으면 추출하여 저장
                if 'Item' in row_data and pd.notna(row_data['Item']):
                    item_info = str(row_data['Item'])

                    # MFG 정보가 있으면 수량 정보로 추가
                    if 'Qty' in row_data and pd.notna(row_data['Qty']):
                        item_info += f" ({row_data['Qty']}개)"

                    try:
                        # 그리드에 아이템 추가
                        row_idx = self.row_headers.index(row_key)
                        col_idx = self.days.index(day)

                        # 전체 행 데이터를 아이템 데이터(dict 형태)로 전달
                        item_full_data = row_data.to_dict()
                        new_item = self.grid_widget.addItemAt(row_idx, col_idx, item_info, item_full_data)

                        if new_item:
                            item_code = item_full_data.get('Item', '')

                            # 사전할당 아이템인 경우
                            if item_code in self.pre_assigned_items:
                                new_item.set_pre_assigned_status(True)
                                
                            # 출하 실패 아이템인 경우
                            if item_code in self.shipment_failure_items:
                                item_code = item_full_data.get('Item')
                                failure_info = self.shipment_failure_items[item_code]
                                new_item.set_shipment_failure(True, failure_info.get('reason', 'Unknown reason'))

                            # 자재부족 아이템인 경우
                            if hasattr(self, 'current_shortage_items') and item_code in self.current_shortage_items:
                                shortage_info = self.current_shortage_items[item_code]
                                new_item.set_shortage_status(True, shortage_info)

                    except ValueError as e:
                        print(f"인덱스 찾기 오류: {e}")

            # 새로운 그룹화된 데이터 저장
            if 'Day' in self.data.columns:
                self.grouped_data = self.data.groupby(['Line', 'Day', 'Time']).first().reset_index()
            else:
                self.grouped_data = self.data.groupby(['Line', 'Time']).first().reset_index()

            # 데이터 변경 신호 발생
            self.data_changed.emit(self.grouped_data)

        except Exception as e:
            EnhancedMessageBox.show_validation_error(self, "Grouping Error", f"An error occurred during data grouping.\n{str(e)}")


    """외부에서 데이터 설정"""
    def set_data_from_external(self, new_data):
        if not new_data.empty:
            new_data['Time'] = pd.to_numeric(new_data['Time'], errors='coerce')
            new_data['Qty'] = pd.to_numeric(new_data['Qty'], errors='coerce')
        
        self.data = new_data
        self.original_data = self.data.copy()
        self.update_table_from_data()


    def set_validator(self, validator):
        self.validator = validator
        self.grid_widget.set_validator(validator)
        

    """사전할당 아이템 정보 설정"""
    def set_pre_assigned_items(self, pre_assigned_items):
        self.pre_assigned_items = pre_assigned_items

        # 이미 데이터가 있다면 적용
        if hasattr(self, 'data') and self.data is not None:
            self.apply_pre_assigned_status()


    """사전할당 아이템 상태 적용"""
    def apply_pre_assigned_status(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
        
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']
                        if item_code in self.pre_assigned_items:
                            item.set_pre_assigned_status(True)
    
    """출하 실패 아이템 정보 설정"""
    def set_shipment_failure_items(self, failure_items):
        # 이전 출하 실패 정보 초기화
        self.clear_shipment_failure_status()
        
        # 새 출하 실패 정보 저장
        self.shipment_failure_items = failure_items
        
        # 이미 데이터가 있다면 적용
        if hasattr(self, 'data') and self.data is not None:
            self.apply_shipment_failure_status()
    
    """출하 실패 상태 클리어"""
    def clear_shipment_failure_status(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
            
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if hasattr(item, 'set_shipment_failure'):
                        item.set_shipment_failure(False)
        
        # 출하 실패 정보 초기화
        self.shipment_failure_items = {}
    
    """출하 실패 상태 적용"""
    def apply_shipment_failure_status(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
            
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']
                        if item_code in self.shipment_failure_items:
                            failure_info = self.shipment_failure_items[item_code]
                            item.set_shipment_failure(True, failure_info.get('reason', 'Unknown reason'))

    """원본 데이터로 되돌리기"""
    def reset_to_original(self):
        if self.original_data is None:
            EnhancedMessageBox.show_validation_error(self, "Reset Failed", 
                                "No original data to reset to.")
            return
        
        # 사용자 확인 Dialog
        reply = EnhancedMessageBox.show_confirmation(
            self, "Reset to Original", "Are you sure you want to reset all changes and return to the original data?\nAll modifications will be lost."
        )

        if reply:
            # 원본 데이터로 복원
            self.data = self.original_data.copy()
            self.update_table_from_data()

            # Reset 버튼 비활성화
            self.reset_button.setEnabled(False)

            # 성공 메세지
            EnhancedMessageBox.show_validation_success(
                self, "Reset Complete", "Data has been successfully reset to the original values."
            )
    
    """데이터가 수정되었음을 표시하는 메서드"""
    def mark_as_modified(self):
        self.reset_button.setEnabled(True)


    """현재 자재부족 아이템 정보 저장"""
    def set_current_shortage_items(self, shortage_items):
        self.current_shortage_items = shortage_items
        self.apply_all_states()

    """모든 상태 정보를 현재 아이템들에 적용"""
    def apply_all_states(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
        
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']

                        # 사전할당 상태
                        if item_code in self.pre_assigned_items:
                            item.set_pre_assigned_status(True)

                        # 출하 실패 상태
                        if item_code in self.shipment_failure_items:
                            failure_info = self.shipment_failure_items[item_code]
                            item.set_shipment_failure(True, failure_info.get('reason', 'Unknown'))

                        # 자재 부족 상태
                        if hasattr(self, 'current_shortage_items') and item_code in self.current_shortage_items:
                            shortage_info = self.current_shortage_items[item_code]
                            item.set_shortage_status(True, shortage_info)