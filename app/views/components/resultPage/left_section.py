# from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
#                              QFileDialog, QLabel, QMessageBox, QTableWidgetItem)
# from PyQt5.QtCore import Qt, pyqtSignal
# from PyQt5.QtGui import QCursor
# import pandas as pd
#
# # 드래그 가능한 테이블 위젯 임포트
# from ..resultPage.dragable_table_widget import DraggableTableWidget
#
#
# class LeftSection(QWidget):
#     # 데이터가 변경되었을 때 신호 발생
#     data_changed = pyqtSignal(pd.DataFrame)
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.data = None  # 불러온 데이터를 저장할 변수
#         self.grouped_data = None  # 그룹화된 데이터를 저장할 변수
#         self.days = ['월', '화', '수', '목', '금', '토', '일']  # 요일 리스트
#         self.time_periods = ['주간', '야간']  # 교대 리스트
#         self.init_ui()
#
#     def init_ui(self):
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#
#         # 상단 컨트롤 영역
#         control_layout = QHBoxLayout()
#
#         # 엑셀 파일 불러오기 버튼
#         self.load_button = QPushButton("엑셀 파일 불러오기")
#         self.load_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #1428A0;
#                 color: white;
#                 font-weight: bold;
#                 padding: 8px 15px;
#                 border-radius: 4px;
#             }
#             QPushButton:hover {
#                 background-color: #004C99;
#             }
#             QPushButton:pressed {
#                 background-color: #003366;
#             }
#         """)
#         self.load_button.setCursor(QCursor(Qt.PointingHandCursor))
#         self.load_button.clicked.connect(self.load_excel_file)
#         control_layout.addWidget(self.load_button)
#
#         # 테이블 초기화 버튼
#         self.clear_button = QPushButton("테이블 초기화")
#         self.clear_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #808080;
#                 color: white;
#                 font-weight: bold;
#                 padding: 8px 15px;
#                 border-radius: 4px;
#             }
#             QPushButton:hover {
#                 background-color: #606060;
#             }
#             QPushButton:pressed {
#                 background-color: #404040;
#             }
#         """)
#         self.clear_button.setCursor(QCursor(Qt.PointingHandCursor))
#         self.clear_button.clicked.connect(self.clear_table)
#         control_layout.addWidget(self.clear_button)
#
#         # 그룹화 버튼 추가
#         self.group_button = QPushButton("Line/Time 그룹화")
#         self.group_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #28A745;
#                 color: white;
#                 font-weight: bold;
#                 padding: 8px 15px;
#                 border-radius: 4px;
#             }
#             QPushButton:hover {
#                 background-color: #218838;
#             }
#             QPushButton:pressed {
#                 background-color: #1E7E34;
#             }
#         """)
#         self.group_button.setCursor(QCursor(Qt.PointingHandCursor))
#         self.group_button.clicked.connect(self.group_data)
#         control_layout.addWidget(self.group_button)
#
#         # 나머지 공간 채우기
#         control_layout.addStretch(1)
#
#         main_layout.addLayout(control_layout)
#
#         # 테이블 영역
#         self.table_widget = DraggableTableWidget()
#         self.table_widget.setMinimumHeight(500)  # 최소 높이 설정
#         self.table_widget.itemChanged.connect(self.on_table_item_changed)
#         main_layout.addWidget(self.table_widget)
#
#     def load_excel_file(self):
#         """엑셀 파일 선택 및 로드"""
#         file_path, _ = QFileDialog.getOpenFileName(
#             self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
#         )
#
#         if file_path:
#             try:
#                 # 엑셀 파일 로드
#                 self.data = pd.read_excel(file_path)
#                 self.update_table_from_data()
#
#                 # 데이터 로드 성공 메시지
#                 QMessageBox.information(self, "파일 로드 성공",
#                                         f"파일을 성공적으로 로드했습니다.\n행: {self.data.shape[0]}, 열: {self.data.shape[1]}")
#
#             except Exception as e:
#                 # 에러 메시지 표시
#                 QMessageBox.critical(self, "파일 로드 오류", f"파일을 로드하는 중 오류가 발생했습니다.\n{str(e)}")
#
#     def update_table_from_data(self):
#         """데이터프레임으로 테이블 위젯 업데이트"""
#         if self.data is None:
#             return
#
#         # 파일 불러오자마자 바로 그룹화된 테이블 표시
#         self.group_data()
#
#         # 데이터 변경 신호 발생
#         self.data_changed.emit(self.data)
#
#     def group_data(self):
#         """Line과 Time으로 데이터 그룹화하고 Line_교대 형식으로 표시, Item과 MFG 정보 포함"""
#         if self.data is None or 'Line' not in self.data.columns or 'Time' not in self.data.columns:
#             QMessageBox.warning(self, "그룹화 불가",
#                                 "데이터가 없거나 'Line' 또는 'Time' 컬럼이 없습니다.\n필요한 컬럼이 포함된 데이터를 로드해주세요.")
#             return
#
#         try:
#             # Line과 Time 값 추출
#             lines = sorted(self.data['Line'].unique())
#             times = sorted(self.data['Time'].unique())
#
#             # 교대 시간 구분 (홀수: 1교대, 짝수: 2교대)
#             shifts = {}
#             for time in times:
#                 if int(time) % 2 == 1:  # 홀수
#                     shifts[time] = "주간"
#                 else:  # 짝수
#                     shifts[time] = "야간"
#
#             # 결과 테이블 초기화 - 요일 수만큼 열 할당
#             self.table_widget.clear()
#
#             # 새로운 행 구조: 각 Line_교대 쌍이 하나의 행이 됨
#             rows = []
#             for line in lines:
#                 for shift in ["주간", "야간"]:
#                     rows.append(f"{line} ({shift})")
#
#             self.table_widget.setRowCount(len(rows))
#             self.table_widget.setColumnCount(len(self.days))  # 각 요일당 1칸
#
#             # 열 헤더를 요일로 설정
#             self.table_widget.setHorizontalHeaderLabels(self.days)
#
#             # 행 헤더를 Line_교대로 설정
#             self.table_widget.setVerticalHeaderLabels(rows)
#
#             # 각 요일과 라인/교대 별로 데이터 수집 및 그룹화
#             day_line_shift_items = {}
#
#             for _, row_data in self.data.iterrows():
#                 if 'Line' not in row_data or 'Time' not in row_data:
#                     continue
#
#                 line = row_data['Line']
#                 time = row_data['Time']
#                 shift = shifts[time]
#                 day_idx = (int(time) - 1) // 2
#
#                 if day_idx >= len(self.days):
#                     continue
#
#                 day = self.days[day_idx]
#                 row_key = f"{line} ({shift})"
#
#                 # 해당 요일과 라인/교대에 대한 아이템 정보 저장
#                 if (day, row_key) not in day_line_shift_items:
#                     day_line_shift_items[(day, row_key)] = []
#
#                 # Item과 MFG 정보가 있으면 추출하여 저장
#                 item_info = ""
#
#                 if 'Item' in row_data and pd.notna(row_data['Item']):
#                     item_info = str(row_data['Item'])
#
#                     # MFG 정보가 있으면 수량 정보로 추가
#                     if 'MFG' in row_data and pd.notna(row_data['MFG']):
#                         item_info += f" ({row_data['MFG']}개)"
#
#                     day_line_shift_items[(day, row_key)].append(item_info)
#
#             # 수집된, 그룹화된 데이터를 테이블에 표시
#             for (day, row_key), items in day_line_shift_items.items():
#                 try:
#                     day_idx = self.days.index(day)
#                     row_idx = rows.index(row_key)
#
#                     # 아이템 목록을 줄바꿈으로 구분하여 표시
#                     content = "\n".join(items)
#
#                     # QTableWidgetItem 생성 및 설정
#                     item = QTableWidgetItem(content)
#                     item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)  # 텍스트 위치 설정
#                     self.table_widget.setItem(row_idx, day_idx, item)
#                 except ValueError as e:
#                     print(f"인덱스 찾기 오류: {e}")
#
#             # 새로운 그룹화된 데이터 저장
#             if 'Day' in self.data.columns:
#                 self.grouped_data = self.data.groupby(['Line', 'Day', 'Time']).first().reset_index()
#             else:
#                 # Day 컬럼이 없으면 Line과 Time으로만 그룹화
#                 self.grouped_data = self.data.groupby(['Line', 'Time']).first().reset_index()
#
#             # 셀 크기 자동 조절 설정
#             self.table_widget.resizeRowsToContents()
#             self.table_widget.resizeColumnsToContents()
#
#             # 셀 내용이 많을 경우 행 높이를 더 크게 설정 (최소 높이 설정)
#             for row in range(self.table_widget.rowCount()):
#                 current_height = self.table_widget.rowHeight(row)
#                 if current_height < 100:  # 최소 행 높이 설정 (필요에 따라 조정)
#                     self.table_widget.setRowHeight(row, 100)
#
#             # 열 너비 최소값 설정
#             for col in range(self.table_widget.columnCount()):
#                 current_width = self.table_widget.columnWidth(col)
#                 if current_width < 200:  # 최소 열 너비 설정 (필요에 따라 조정)
#                     self.table_widget.setColumnWidth(col, 200)
#
#             # 행 헤더 너비 설정
#             self.table_widget.verticalHeader().setMinimumWidth(150)
#             self.table_widget.verticalHeader().setDefaultSectionSize(100)  # 기본 행 높이 설정
#
#             # 워드랩 허용 (긴 텍스트 자동 줄바꿈)
#             self.table_widget.setWordWrap(True)
#
#             # 데이터 변경 신호 발생 (그룹화된 데이터 전달)
#             self.data_changed.emit(self.grouped_data)
#
#             # 성공 메시지 (자동 그룹화 시 메시지 표시하지 않음)
#             if self.sender() == self.group_button:
#                 QMessageBox.information(self, "그룹화 성공", "데이터를 Line과 Time으로 그룹화하여 표시했습니다.")
#
#         except Exception as e:
#             # 에러 메시지 표시
#             QMessageBox.critical(self, "그룹화 오류", f"데이터 그룹화 중 오류가 발생했습니다.\n{str(e)}")
#             # 디버깅을 위한 예외 정보 출력
#             import traceback
#             traceback.print_exc()
#
#     def on_table_item_changed(self, item):
#         """테이블 아이템이 변경되었을 때 호출"""
#         if self.data is None or item is None:
#             return
#
#         row, col = item.row(), item.column()
#
#         # 데이터프레임 업데이트
#         try:
#             value = item.text()
#             if value:
#                 # 숫자인 경우 형변환
#                 try:
#                     if '.' in value:
#                         value = float(value)
#                     else:
#                         value = int(value)
#                 except ValueError:
#                     # 숫자가 아니면 문자열 그대로 사용
#                     pass
#             else:
#                 value = None
#
#             self.data.iloc[row, col] = value
#
#             # 데이터 변경 신호 발생
#             self.data_changed.emit(self.data)
#
#         except Exception as e:
#             print(f"데이터 업데이트 오류: {e}")
#
#     def clear_table(self):
#         """테이블 초기화"""
#         reply = QMessageBox.question(
#             self, '테이블 초기화',
#             "정말로 테이블을 초기화하시겠습니까?",
#             QMessageBox.Yes | QMessageBox.No,
#             QMessageBox.No
#         )
#
#         if reply == QMessageBox.Yes:
#             self.table_widget.clear()
#             self.table_widget.setRowCount(0)
#             self.table_widget.setColumnCount(0)
#             self.data = None
#             self.grouped_data = None
#
#             # 빈 데이터프레임 신호 발생
#             self.data_changed.emit(pd.DataFrame())
#
#     def set_data_from_external(self, new_data):
#         """외부에서 데이터를 받아 설정하는 메서드"""
#         self.data = new_data
#         self.update_table_from_data()