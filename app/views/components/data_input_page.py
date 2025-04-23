from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QSplitter, QHeaderView, QTabWidget)
from PyQt5.QtGui import QCursor

import pandas as pd
import os

from app.views.components.date_range_selector import DateRangeSelector
from app.views.components.file_upload_component import FileUploadComponent


class DataInputPage(QWidget):
    file_selected = pyqtSignal(str)
    date_range_selected = pyqtSignal(QDate, QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_tabs = {}  # 파일 경로를 키로, 해당 탭 인덱스를 값으로 저장
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 전체 여백 제거
        layout.setSpacing(0)  # 위젯 간 간격 제거

        # 제목과 입력 섹션을 포함할 컨테이너 생성
        top_container = QFrame()
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(10, 10, 10, 10)  # 여백 추가
        top_container_layout.setSpacing(10)  # 위젯 간 간격 설정
        top_container.setStyleSheet("border: solid 1px grey; background-color: #F9F9F9")
        top_container.setFixedHeight(120)  # 높이 고정

        # 제목과 버튼을 포함할 상단 행 컨테이너
        title_row = QFrame()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(10, 0, 10, 0)  # 여백 제거

        # 제목 레이블 생성
        title_label = QLabel("Upload Data")
        title_label.setStyleSheet("font-weight: bold; font-size: 30px; color: #333333;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 왼쪽 가운데 정렬

        # Execute 버튼 생성
        excute_button = QPushButton("Execute")
        excute_button.setFixedWidth(200)
        excute_button.setFixedHeight(40)
        excute_button.setCursor(QCursor(Qt.PointingHandCursor))
        excute_button.setStyleSheet("""
        QPushButton {
        background-color: #1428A0; color: white; font-weight: bold; padding: 5px 15px; border-radius: 5px; 
        }
        QPushButton:hover {
                background-color: #004C99; /* 원래 색상보다 약간 어두운 색 */
            }
            QPushButton:pressed {
                background-color: #003366; /* 클릭 시에는 더 어두운 색 */
            }
        """)


        # 타이틀 행에 제목과 버튼 추가
        title_row_layout.addWidget(title_label, 1)  # 왼쪽에 제목 배치 (stretch 1)
        title_row_layout.addWidget(excute_button, 0, Qt.AlignRight)  # 오른쪽에 버튼 배치

        # 입력 섹션 생성
        input_section = QFrame()
        input_section.setFrameShape(QFrame.StyledPanel)
        input_section.setStyleSheet("background-color: white;")
        input_section.setFixedHeight(50)

        # 입력 섹션의 레이아웃 설정
        input_layout = QHBoxLayout(input_section)
        input_layout.setContentsMargins(10, 5, 10, 5)

        # 왼쪽 섹션: 날짜 선택 컴포넌트 사용
        self.date_selector = DateRangeSelector()
        self.date_selector.date_range_changed.connect(self.on_date_range_changed)

        # 오른쪽 섹션: 파일 업로드 컴포넌트 사용
        self.file_uploader = FileUploadComponent()
        self.file_uploader.file_selected.connect(self.on_file_selected)

        # 입력 레이아웃에 위젯 추가
        input_layout.addWidget(self.date_selector, 1)  # 왼쪽에 날짜 선택기
        input_layout.addWidget(self.file_uploader, 3)  # 오른쪽에 파일 업로더

        # 컨테이너에 제목 행과 입력 섹션 추가
        top_container_layout.addWidget(title_row)
        top_container_layout.addWidget(input_section)

        # 하단 영역을 위한 스플리터 생성 (왼쪽과 오른쪽으로 나눔)
        splitter = QSplitter(Qt.Horizontal)

        # 왼쪽 영역 - 탭 위젯으로 여러 파일 데이터 표시
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: white; border: 1px solid #cccccc;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #cccccc; 
                background: white; 
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px 10px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #1428A0;
                color: white;
            }
            QTabBar::tab:selected {
                border-bottom-color: white;
            }
        """)

        # 기본 탭 추가
        default_tab = QWidget()
        default_layout = QVBoxLayout(default_tab)
        default_label = QLabel("파일을 업로드하면 여기에 데이터가 표시됩니다.")
        default_label.setAlignment(Qt.AlignCenter)
        default_layout.addWidget(default_label)

        # 왼쪽 패널에 탭 위젯 추가
        left_layout.addWidget(self.tab_widget)

        # 오른쪽 영역 - 오류 메시지 표시
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: white; border: 1px solid #cccccc;")
        right_layout = QVBoxLayout(right_panel)

        # 오류 메시지 레이블
        self.error_label = QLabel("파일을 업로드하세요")
        self.error_label.setStyleSheet("color: blue; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignCenter)

        # 오른쪽 패널에 위젯 추가
        right_layout.addWidget(self.error_label)
        right_layout.addStretch()

        # 스플리터에 패널 추가
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])  # 초기 크기 설정 (7:3 비율)

        # 전체 레이아웃에 컨테이너와 스플리터 추가
        layout.addWidget(top_container)
        layout.addWidget(splitter, 1)  # 스플리터가 나머지 공간을 채우도록 stretch factor 1 설정

    def on_date_range_changed(self, start_date, end_date):
        """날짜 범위가 변경되면 시그널 발생"""
        self.date_range_selected.emit(start_date, end_date)

    def on_file_selected(self, file_path):
        """파일이 선택되면 시그널 발생"""
        self.file_selected.emit(file_path)

        # 파일이 선택되면 새 탭에 데이터 표시
        self.add_file_tab(file_path)

    def get_file_paths(self):
        """선택된 파일 경로 리스트 반환"""
        return self.file_uploader.get_file_paths()

    def add_file_tab(self, file_path):
        """새 탭을 생성하고 파일 데이터를 표시"""
        try:
            if not file_path or not os.path.exists(file_path):
                self.error_label.setText("파일을 찾을 수 없습니다")
                self.error_label.setStyleSheet("color: red; font-size: 14px;")
                return

            # 이미 탭이 있는지 확인
            if file_path in self.file_tabs:
                # 이미 있는 탭으로 이동
                self.tab_widget.setCurrentIndex(self.file_tabs[file_path])
                self.error_label.setText("이미 로드된 파일입니다")
                self.error_label.setStyleSheet("color: blue; font-size: 14px;")
                return

            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)

            # 파일 확장자에 따라 다른 방식으로 데이터 로드
            if file_ext == '.csv':
                # CSV 파일 로드
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_ext in ['.xls', '.xlsx']:
                # 엑셀 파일 로드
                df = pd.read_excel(file_path)
            else:
                self.error_label.setText("지원하지 않는 파일 형식입니다")
                self.error_label.setStyleSheet("color: red; font-size: 14px;")
                return

            # 새 탭 생성
            new_tab = QWidget()
            new_tab_layout = QVBoxLayout(new_tab)
            new_tab_layout.setContentsMargins(0, 0, 0, 0)

            # 데이터 테이블 생성
            data_table = QTableWidget()
            data_table.setStyleSheet("QTableWidget { border: none; }")
            data_table.setAlternatingRowColors(True)
            data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            data_table.horizontalHeader().setStretchLastSection(True)

            # 테이블 설정
            data_table.setRowCount(len(df))
            data_table.setColumnCount(len(df.columns))
            data_table.setHorizontalHeaderLabels(df.columns)

            # 데이터 채우기
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iloc[row, col]))
                    data_table.setItem(row, col, item)

            # 테이블 열 너비 자동 조정
            data_table.resizeColumnsToContents()

            # 탭에 테이블 추가
            new_tab_layout.addWidget(data_table)

            # 탭 추가
            tab_index = self.tab_widget.addTab(new_tab, file_name)
            self.tab_widget.setCurrentIndex(tab_index)  # 새 탭으로 전환

            # 탭 정보 저장
            self.file_tabs[file_path] = tab_index

            # 성공 메시지 표시
            self.error_label.setText(f"'{file_name}' 파일이 성공적으로 로드되었습니다")
            self.error_label.setStyleSheet("color: green; font-size: 14px;")

        except Exception as e:
            # 오류 발생 시 메시지 표시
            self.error_label.setText(f"데이터 로딩 오류: {str(e)}")
            self.error_label.setStyleSheet("color: red; font-size: 14px;")