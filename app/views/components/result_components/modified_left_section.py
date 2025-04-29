from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
import pandas as pd
from .item_grid_widget import ItemGridWidget
from .item_position_manager import ItemPositionManager


class ModifiedLeftSection(QWidget):
    data_changed = pyqtSignal(pd.DataFrame)
    item_selected = pyqtSignal(object, object)  # 아이템 선택 이벤트 추가 (아이템, 컨테이너)
    item_data_changed = pyqtSignal(object, dict)  # 아이템 데이터 변경 이벤트 추가

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

        # 테이블 초기화 버튼
        self.clear_button = QPushButton("테이블 초기화")
        self.clear_button.setStyleSheet("""
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
        self.clear_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_button.clicked.connect(self.clear_table)
        control_layout.addWidget(self.clear_button)

        # 나머지 공간 채우기
        control_layout.addStretch(1)

        main_layout.addLayout(control_layout)

        # 새로운 그리드 위젯 추가
        self.grid_widget = ItemGridWidget()
        self.grid_widget.itemSelected.connect(self.on_grid_item_selected)  # 아이템 선택 이벤트 연결
        self.grid_widget.itemDataChanged.connect(self.on_item_data_changed)  # 아이템 데이터 변경 이벤트 연결
        main_layout.addWidget(self.grid_widget)

    def on_grid_item_selected(self, selected_item, container):
        """그리드에서 아이템이 선택되면 호출되는 함수"""
        # 선택 이벤트만 전달하고 정보 표시 관련 코드는 제거
        self.item_selected.emit(selected_item, container)

    def on_item_data_changed(self, item, new_data, changed_fields=None):
        """아이템 데이터가 변경되면 호출되는 함수"""
        if not item or not new_data or not hasattr(item, 'item_data'):
            print("아이템 또는 데이터가 없음")
            return

        print(f"데이터 변경: {item.item_data}")
        print(f"새 데이터: {new_data}")

        if changed_fields:
            print(f"변경된 필드: {changed_fields}")

        # Line 또는 Time 값 변경 체크 - 위치 변경 필요한지 확인
        position_change_needed = False
        if changed_fields:
            # Time 변경 확인
            if 'Time' in changed_fields:
                position_change_needed = True
                time_change = changed_fields['Time']
                old_time = time_change['from']
                new_time = time_change['to']
                print(f"Time 값 변경 감지: {old_time} -> {new_time}")

            # Line 변경 확인
            if 'Line' in changed_fields:
                position_change_needed = True
                line_change = changed_fields['Line']
                old_line = line_change['from']
                new_line = line_change['to']
                print(f"Line 값 변경 감지: {old_line} -> {new_line}")

        # 위치 변경이 필요한 경우
        if position_change_needed:
            # 기존 container에서 아이템 제거 준비
            old_container = item.parent() if hasattr(item, 'parent') else None

            if not isinstance(old_container, QWidget):
                print("유효한 컨테이너가 아님")
                return

            # 변경된 Line과 Time에 따른 새 위치 계산
            line = new_data.get('Line')
            new_time = new_data.get('Time')

            if not line or not new_time:
                print("Line 또는 Time 정보 없음")
                return

            # 새 위치 계산을 위한 정보 가져오기
            old_time = old_time if 'Time' in changed_fields else new_time
            old_line = old_line if 'Line' in changed_fields else line

            # 새 위치 계산
            from .item_position_manager import ItemPositionManager

            old_day_idx, old_shift = ItemPositionManager.get_day_and_shift(old_time)
            new_day_idx, new_shift = ItemPositionManager.get_day_and_shift(new_time)

            print(f"이전 위치: 요일 인덱스 {old_day_idx}, 교대 {old_shift}")
            print(f"새 위치: 요일 인덱스 {new_day_idx}, 교대 {new_shift}")

            # 새 행/열 인덱스 계산
            old_row_key = ItemPositionManager.get_row_key(old_line, old_shift)
            new_row_key = ItemPositionManager.get_row_key(line, new_shift)

            print(f"이전 행 키: {old_row_key}, 새 행 키: {new_row_key}")
            print(f"현재 row_headers: {self.row_headers}")

            old_row_idx = ItemPositionManager.find_row_index(old_row_key, self.row_headers)
            new_row_idx = ItemPositionManager.find_row_index(new_row_key, self.row_headers)

            old_col_idx = ItemPositionManager.get_col_from_day_idx(old_day_idx, self.days)
            new_col_idx = ItemPositionManager.get_col_from_day_idx(new_day_idx, self.days)

            print(f"이전 위치: 행 {old_row_idx}, 열 {old_col_idx}")
            print(f"새 위치: 행 {new_row_idx}, 열 {new_col_idx}")

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

                print(f"새 위치에 아이템 추가 시도: 행 {new_row_idx}, 열 {new_col_idx}, 텍스트 {item_text}")

                # 새 위치에 아이템 추가
                new_item = self.grid_widget.addItemAt(new_row_idx, new_col_idx, item_text, new_data)

                if new_item:
                    print("새 아이템 생성 성공")
                    # 상위 위젯에 이벤트만 전달하고 메시지는 표시하지 않음
                    self.item_data_changed.emit(new_item, new_data)
                    return  # 이후 코드는 실행하지 않음
                else:
                    print("새 아이템 생성 실패")
            else:
                print(
                    f"유효하지 않은 인덱스: old_row_idx={old_row_idx}, old_col_idx={old_col_idx}, new_row_idx={new_row_idx}, new_col_idx={new_col_idx}")

        # 상위 위젯에 이벤트 전달
        self.item_data_changed.emit(item, new_data)

        # 변경 알림 메시지 표시
        QMessageBox.information(self, "데이터 변경됨",
                                f"아이템 정보가 성공적으로 변경되었습니다.\n{item.text()}",
                                QMessageBox.Ok)

    def load_excel_file(self):
        """엑셀 파일 선택 및 로드"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            try:
                # 엑셀 파일 로드
                self.data = pd.read_excel(file_path)
                self.update_table_from_data()

                # 데이터 로드 성공 메시지
                QMessageBox.information(self, "파일 로드 성공",
                                        f"파일을 성공적으로 로드했습니다.\n행: {self.data.shape[0]}, 열: {self.data.shape[1]}")

            except Exception as e:
                # 에러 메시지 표시
                QMessageBox.critical(self, "파일 로드 오류", f"파일을 로드하는 중 오류가 발생했습니다.\n{str(e)}")

    def update_table_from_data(self):
        """데이터프레임으로 테이블 위젯 업데이트"""
        if self.data is None:
            return

        # 파일 불러오자마자 바로 그룹화된 테이블 표시
        self.group_data()

        # 데이터 변경 신호 발생
        self.data_changed.emit(self.data)

    def group_data(self):
        """Line과 Time으로 데이터 그룹화하고 개별 아이템으로 표시"""
        if self.data is None or 'Line' not in self.data.columns or 'Time' not in self.data.columns:
            QMessageBox.warning(self, "그룹화 불가",
                                "데이터가 없거나 'Line' 또는 'Time' 컬럼이 없습니다.\n필요한 컬럼이 포함된 데이터를 로드해주세요.")
            return

        try:
            # Line과 Time 값 추출
            lines = sorted(self.data['Line'].unique())
            times = sorted(self.data['Time'].unique())

            # 교대 시간 구분
            shifts = {}
            for time in times:
                if int(time) % 2 == 1:  # 홀수
                    shifts[time] = "주간"
                else:  # 짝수
                    shifts[time] = "야간"

            # 행 헤더 생성
            self.row_headers = []
            for line in lines:
                for shift in ["주간", "야간"]:
                    self.row_headers.append(f"{line}_({shift})")

            # 그리드 설정
            self.grid_widget.setupGrid(
                rows=len(self.row_headers),
                columns=len(self.days),
                row_headers=self.row_headers,
                column_headers=self.days
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
            QMessageBox.critical(self, "그룹화 오류", f"데이터 그룹화 중 오류가 발생했습니다.\n{str(e)}")
            # 디버깅을 위한 예외 정보 출력
            import traceback
            traceback.print_exc()

    def clear_table(self):
        """테이블 초기화"""
        reply = QMessageBox.question(
            self, '테이블 초기화',
            "정말로 테이블을 초기화하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.grid_widget.clearAllItems()
            self.data = None
            self.grouped_data = None
            self.row_headers = []

            # 빈 데이터프레임 신호 발생
            self.data_changed.emit(pd.DataFrame())

    def set_data_from_external(self, new_data):
        """외부에서 데이터를 받아 설정하는 메서드"""
        self.data = new_data
        self.update_table_from_data()