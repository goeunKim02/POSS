from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
import pandas as pd
from .item_grid_widget import ItemGridWidget


class ModifiedLeftSection(QWidget):
    data_changed = pyqtSignal(pd.DataFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.grouped_data = None
        self.days = ['월', '화', '수', '목', '금', '토', '일']
        self.time_periods = ['주간', '야간']
        self.init_ui()

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
        main_layout.addWidget(self.grid_widget)

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
            rows = []
            for line in lines:
                for shift in ["주간", "야간"]:
                    rows.append(f"{line}_({shift})")

            # 그리드 설정
            self.grid_widget.setupGrid(
                rows=len(rows),
                columns=len(self.days),
                row_headers=rows,
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
                    if 'MFG' in row_data and pd.notna(row_data['MFG']):
                        item_info += f" ({row_data['MFG']}개)"

                    try:
                        # 그리드에 아이템 추가
                        row_idx = rows.index(row_key)
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

            # 빈 데이터프레임 신호 발생
            self.data_changed.emit(pd.DataFrame())

    def set_data_from_external(self, new_data):
        """외부에서 데이터를 받아 설정하는 메서드"""
        self.data = new_data
        self.update_table_from_data()