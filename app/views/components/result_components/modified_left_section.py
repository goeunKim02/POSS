from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
import pandas as pd
from .item_grid_widget import ItemGridWidget
from app.views.components.result_components.enhanced_message_box import EnhancedMessageBox

class ModifiedLeftSection(QWidget):
    data_changed = pyqtSignal(pd.DataFrame)
    item_selected = pyqtSignal(object, object)  # 아이템 선택 이벤트 추가 (아이템, 컨테이너)
    item_data_changed = pyqtSignal(object, dict)  # 아이템 데이터 변경 이벤트 추가
    cell_moved = pyqtSignal(object, dict, dict)  # 이전 아이템, 이전 데이터, 새 데이터

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.grouped_data = None
        self.days = ['월', '화', '수', '목', '금', '토', '일']
        self.time_periods = ['주간', '야간']
        self.init_ui()

        # 아이템 이동을 위한 정보 저장
        self.row_headers = []

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 컨트롤 레이아웃
        control_layout = QHBoxLayout()

        # 엑셀 파일 불러오기 버튼
        self.load_button = QPushButton("엑셀 파일 불러오기")
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
        control_layout.addWidget(self.load_button)

        # # 테이블 초기화 버튼
        # self.clear_button = QPushButton("테이블 초기화")
        # self.clear_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: #808080;
        #         color: white;
        #         font-weight: bold;
        #         padding: 8px 15px;
        #         border-radius: 4px;
        #     }
        #     QPushButton:hover {
        #         background-color: #606060;
        #     }
        #     QPushButton:pressed {
        #         background-color: #404040;
        #     }
        # """)
        # self.clear_button.setCursor(QCursor(Qt.PointingHandCursor))
        # self.clear_button.clicked.connect(self.clear_table)
        # control_layout.addWidget(self.clear_button)

        # 나머지 공간 채우기
        control_layout.addStretch(1)

        main_layout.addLayout(control_layout)

        # 새로운 그리드 위젯 추가
        self.grid_widget = ItemGridWidget()
        self.grid_widget.itemSelected.connect(self.on_grid_item_selected)  # 아이템 선택 이벤트 연결
        self.grid_widget.itemDataChanged.connect(self.on_item_data_changed)  # 아이템 데이터 변경 이벤트 연결
        main_layout.addWidget(self.grid_widget)

    """그리드에서 아이템이 선택되면 호출되는 함수"""
    def on_grid_item_selected(self, selected_item, container):
        # 선택 이벤트만 전달하고 정보 표시 관련 코드는 제거
        self.item_selected.emit(selected_item, container)

    """아이템 데이터가 변경되면 호출되는 함수"""
    def on_item_data_changed(self, item, new_data, changed_fields=None):
        print("===== on_item_data_changed 함수 호출 시작 =====")
        print(f"아이템 타입: {type(item)}")
        print(f"변경된 필드: {changed_fields}")
        print(f"새 데이터: {new_data}")

        if not item or not new_data or not hasattr(item, 'item_data'):
            print("아이템 또는 데이터가 없음")
            return

        # 이전 데이터 저장 (시각화 업데이트용)
        old_data = item.item_data.copy() if hasattr(item, 'item_data') else {}
        print(f"이전 데이터: {old_data}")

        # 검증 통과 시
        # Line 또는 Time 값 변경 체크 - 위치 변경 필요한지 확인
        position_change_needed = False
        if changed_fields:
            # Time 변경 확인
            if 'Time' in changed_fields:
                position_change_needed = True
                time_change = changed_fields['Time']
                old_time = time_change['from']
                new_time = time_change['to']
                # print(f"Time 값 변경 감지: {old_time} -> {new_time}")

            # Line 변경 확인
            if 'Line' in changed_fields:
                position_change_needed = True
                line_change = changed_fields['Line']
                old_line = line_change['from']
                new_line = line_change['to']
                # print(f"Line 값 변경 감지: {old_line} -> {new_line}")

        # 위치 변경이 필요한 경우
        if position_change_needed:
            # 기존 container에서 아이템 제거 준비
            old_container = item.parent() if hasattr(item, 'parent') else None

            if not isinstance(old_container, QWidget):
                # print("유효한 컨테이너가 아님")
                return

            # 변경된 Line과 Time에 따른 새 위치 계산
            line = new_data.get('Line')
            new_time = new_data.get('Time')

            if not line or not new_time:
                # print("Line 또는 Time 정보 없음")
                return

            # 새 위치 계산을 위한 정보 가져오기
            old_time = old_time if 'Time' in changed_fields else new_time
            old_line = old_line if 'Line' in changed_fields else line

            # 새 위치 계산
            from .item_position_manager import ItemPositionManager

            old_day_idx, old_shift = ItemPositionManager.get_day_and_shift(old_time)
            new_day_idx, new_shift = ItemPositionManager.get_day_and_shift(new_time)

            # print(f"이전 위치: 요일 인덱스 {old_day_idx}, 교대 {old_shift}")
            # print(f"새 위치: 요일 인덱스 {new_day_idx}, 교대 {new_shift}")

            # 새 행/열 인덱스 계산
            old_row_key = ItemPositionManager.get_row_key(old_line, old_shift)
            new_row_key = ItemPositionManager.get_row_key(line, new_shift)

            # print(f"이전 행 키: {old_row_key}, 새 행 키: {new_row_key}")
            # print(f"현재 row_headers: {self.row_headers}")

            old_row_idx = ItemPositionManager.find_row_index(old_row_key, self.row_headers)
            new_row_idx = ItemPositionManager.find_row_index(new_row_key, self.row_headers)

            old_col_idx = ItemPositionManager.get_col_from_day_idx(old_day_idx, self.days)
            new_col_idx = ItemPositionManager.get_col_from_day_idx(new_day_idx, self.days)

            # print(f"이전 위치: 행 {old_row_idx}, 열 {old_col_idx}")
            # print(f"새 위치: 행 {new_row_idx}, 열 {new_col_idx}")

            # 유효한 인덱스인 경우 아이템 이동
            if old_row_idx >= 0 and old_col_idx >= 0 and new_row_idx >= 0 and new_col_idx >= 0:
                print("아이템 이동 시도")

                # 이전 위치에서 아이템 제거
                if old_container:
                    print(f"컨테이너에서 아이템 제거 시도: {old_container}")
                    old_container.removeItem(item)

                # 새 위치에 아이템 추가
                item_text = ""
                if 'Item' in new_data:
                    item_text = str(new_data['Item'])
                    if 'Qty' in new_data and pd.notna(new_data['Qty']):
                        item_text += f" ({new_data['Qty']}개)"

                # print(f"새 위치에 아이템 추가 시도: 행 {new_row_idx}, 열 {new_col_idx}, 텍스트 {item_text}")

                # 수정: 데이터를 추가하기 전에 검증
                if hasattr(self, 'validator'):
                    valid, message = self.validator.validate_adjustment(
                        new_data.get('Line'),
                        new_data.get('Time'),
                        new_data.get('Item', ''),
                        new_data.get('Qty', 0),
                        old_data.get('Line'),
                        old_data.get('Time')
                    )
                    
                    if not valid:
                        EnhancedMessageBox.show_validation_error(self, "Adjustment Not Possible", message)
                        return

                # 새 위치에 아이템 추가
                new_item = self.grid_widget.addItemAt(new_row_idx, new_col_idx, item_text, new_data)

                if new_item:
                    # print("새 아이템 생성 성공")

                    # 셀 이동 이벤트 발생 (시각화 차트 업데이트)
                    self.cell_moved.emit(new_item, old_data, new_data)

                    # 상위 위젯에 이벤트만 전달하고 메시지는 표시하지 않음
                    self.item_data_changed.emit(new_item, new_data)
                    return  # 이후 코드는 실행하지 않음
                else:
                    print("새 아이템 생성 실패")
                    return
            else:
                print(
                    f"유효하지 않은 인덱스: old_row_idx={old_row_idx}, old_col_idx={old_col_idx}, new_row_idx={new_row_idx}, new_col_idx={new_col_idx}")
                return
            
        # 위치 변경이 필요 없는 경우 - 데이터만 업데이트
        if hasattr(item, 'update_item_data'):
            # 수정: update_item_data 메서드의 반환값 처리
            success, error_message = item.update_item_data(new_data)
            if not success:
                EnhancedMessageBox.show_validation_error(self, "Adjustment Not Possible", error_message)
                return

        # 데이터 변경 성공 시
        # 상위 위젯에 이벤트 전달
        self.item_data_changed.emit(item, new_data)

        # 셀 이동 이벤트 발생 (시각화 차트 업데이트) 추가
        if not position_change_needed:
            # 위치 변경이 없는 데이터 수정의 경우에도 시각화 업데이트
            self.cell_moved.emit(item, old_data, new_data)

        # 변경 알림 메시지 표시
        EnhancedMessageBox.show_validation_success(self, "Data Updated",
                                f"The production schedule has been successfully updated. \n{item.text()}")

    """엑셀 파일 로드"""
    def load_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            try:
                # 엑셀 파일 로드
                self.data = pd.read_excel(file_path)
                self.update_table_from_data()

                # 데이터 로드 성공 메시지
                EnhancedMessageBox.show_validation_success(self, "File Loaded Successfully",
                                        f"File has been successfully loaded.\nRows: {self.data.shape[0]}, Columns: {self.data.shape[1]}")

            except Exception as e:
                # 에러 메시지 표시
                EnhancedMessageBox.show_validation_error(self, "File Loding Error", f"An error occurred while loading the file.\n{str(e)}")

    """엑셀 파일에서 데이터를 읽어와 테이블 업데이트"""
    def update_table_from_data(self):
        if self.data is None:
            return

        # 파일 불러오자마자 바로 그룹화된 테이블 표시
        self.group_data()

        # 데이터 변경 신호 발생
        self.data_changed.emit(self.data)

    """Line과 Time으로 데이터 그룹화하고 개별 아이템으로 표시 (라인별 셀 병합 형태로)"""
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
            # 화면에는 "ㅣ-01" 형식으로 표시됨

            # 교대 시간 구분
            shifts = {}
            for time in times:
                if int(time) % 2 == 1:  # 홀수
                    shifts[time] = "주간"
                else:  # 짝수
                    shifts[time] = "야간"

            # 라인별 교대 정보 구성
            line_shifts = {}
            for line in lines:
                line_shifts[line] = ["주간", "야간"]  # 모든 라인에 주간/야간 교대 추가

            # 행 헤더 생성 (내부 데이터 관리용)
            self.row_headers = []
            for line in lines:
                for shift in ["주간", "야간"]:
                    self.row_headers.append(f"{line}_({shift})")

            # 수정된 그리드 설정 (라인별 셀 병합 형태)
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

                    # MFG 정보가 있으면 수량 정보로 추가 (표시 텍스트에만)
                    if 'Qty' in row_data and pd.notna(row_data['Qty']):
                        item_info += f" ({row_data['Qty']}개)"

                    try:
                        # 그리드에 아이템 추가
                        row_idx = self.row_headers.index(row_key)
                        col_idx = self.days.index(day)

                        # 전체 행 데이터를 아이템 데이터로 전달
                        # pandas Series를 딕셔너리로 변환하여 전달
                        item_full_data = row_data.to_dict()
                        self.grid_widget.addItemAt(row_idx, col_idx, item_info, item_full_data)
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
            # 에러 메시지 표시
            EnhancedMessageBox.show_validation_error(self, "Grouping Error", f"An error occurred during data grouping.\n{str(e)}")
            # 디버깅을 위한 예외 정보 출력
            import traceback
            traceback.print_exc()

    # """테이블 초기화"""
    # def clear_table(self):
    #     reply = QMessageBox.question(
    #         self, '테이블 초기화',
    #         "정말로 테이블을 초기화하시겠습니까?",
    #         QMessageBox.Yes | QMessageBox.No,
    #         QMessageBox.No
    #     )

    #     if reply == QMessageBox.Yes:
    #         self.grid_widget.clearAllItems()
    #         self.data = None
    #         self.grouped_data = None
    #         self.row_headers = []

    #         # 빈 데이터프레임 신호 발생
    #         self.data_changed.emit(pd.DataFrame())


    """외부에서 데이터 설정"""
    def set_data_from_external(self, new_data):
        # 데이터 타입 통일
        if not new_data.empty:
            # 정수 변환
            new_data['Time'] = pd.to_numeric(new_data['Time'], errors='coerce')
            new_data['Qty'] = pd.to_numeric(new_data['Qty'], errors='coerce')
            
        print("데이터 타입 통일 후:")
        if 'Time' in new_data.columns:
            print(f"Time 열 타입: {new_data['Time'].dtype}")
        if 'Qty' in new_data.columns:
            print(f"Qty 열 타입: {new_data['Qty'].dtype}")
        
        self.data = new_data
        self.update_table_from_data()


    def set_validator(self, validator):
        self.validator = validator
        self.grid_widget.set_validator(validator)