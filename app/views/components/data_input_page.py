from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QHeaderView, QTabWidget)
from PyQt5.QtGui import QCursor, QFont

import os

from app.views.components.data_upload_components.date_range_selector import DateRangeSelector
from app.views.components.data_upload_components.file_upload_component import FileUploadComponent
from app.views.components.data_upload_components.sheet_selector_component import SheetSelectorComponent
from app.views.components.data_upload_components.file_tab_component import FileTabComponent


class DataInputPage(QWidget):
    file_selected = pyqtSignal(str)
    date_range_selected = pyqtSignal(QDate, QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
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
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)

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
        self.file_uploader.file_removed.connect(self.on_file_removed)  # 파일 삭제 시그널 연결

        # 입력 레이아웃에 위젯 추가
        input_layout.addWidget(self.date_selector, 1)  # 왼쪽에 날짜 선택기
        input_layout.addWidget(self.file_uploader, 3)  # 오른쪽에 파일 업로더

        # 컨테이너에 제목 행과 입력 섹션 추가
        top_container_layout.addWidget(title_row)
        top_container_layout.addWidget(input_section)

        # 하단 영역을 위한 스플리터 생성 (왼쪽과 오른쪽으로 나눔)
        splitter = QSplitter(Qt.Horizontal)

        # 왼쪽 영역 - 파일 탭 컴포넌트와 시트 선택기로 구성
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: white; border: 1px solid #cccccc;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # 파일 탭 컴포넌트 추가
        self.file_tab_component = FileTabComponent()
        self.file_tab_component.tab_changed.connect(self.on_tab_changed)
        left_layout.addWidget(self.file_tab_component)

        # 시트 선택 컴포넌트 추가
        self.sheet_selector = SheetSelectorComponent()
        self.sheet_selector.sheet_changed.connect(self.on_sheet_changed)
        left_layout.addWidget(self.sheet_selector)

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
        """파일이 선택되면 시그널 발생 및 탭에 추가"""
        self.file_selected.emit(file_path)

        # 파일 탭 컴포넌트에 파일 추가
        success, message = self.file_tab_component.add_file_tab(file_path)

        # 메시지 표시
        self.update_status_message(success, message)

        # 엑셀 파일이면 시트 선택기 업데이트
        current_file = self.file_tab_component.get_current_file_path()
        if current_file and self.file_tab_component.is_excel_file(current_file):
            sheets = self.file_tab_component.get_excel_sheets(current_file)
            self.sheet_selector.set_sheets(sheets)
        else:
            self.sheet_selector.setVisible(False)

    def on_file_removed(self, file_path):
        """파일이 삭제되면 해당 탭도 제거"""
        # 파일 탭 컴포넌트에서 해당 탭 제거
        success, message = self.file_tab_component.remove_file_tab(file_path)

        # 메시지 표시
        self.update_status_message(success, message)

        # 현재 선택된 파일 확인 및 시트 선택기 업데이트
        current_file = self.file_tab_component.get_current_file_path()
        if current_file and self.file_tab_component.is_excel_file(current_file):
            sheets = self.file_tab_component.get_excel_sheets(current_file)
            self.sheet_selector.set_sheets(sheets)
        else:
            self.sheet_selector.setVisible(False)

        # 탭이 하나도 없으면 기본 메시지 표시
        if not self.file_tab_component.has_tabs():
            self.error_label.setText("파일을 업로드하세요")
            self.error_label.setStyleSheet("color: blue; font-size: 14px;")

    def on_tab_changed(self, file_path):
        """탭이 변경되면 호출되는 함수"""
        # 엑셀 파일이면 시트 선택기 표시
        if self.file_tab_component.is_excel_file(file_path):
            sheets = self.file_tab_component.get_excel_sheets(file_path)
            self.sheet_selector.set_sheets(sheets)
        else:
            self.sheet_selector.setVisible(False)

    def on_sheet_changed(self, sheet_name):
        """시트가 변경되면 호출되는 함수"""
        # 현재 파일에 해당 시트 로드
        current_file = self.file_tab_component.get_current_file_path()
        if not current_file:
            return

        # 시트 로드
        success, message = self.file_tab_component.load_sheet(current_file, sheet_name)

        # 메시지 표시
        self.update_status_message(success, message)

    def update_status_message(self, success, message):
        """상태 메시지 업데이트"""
        if success:
            self.error_label.setText(message)
            self.error_label.setStyleSheet("color: green; font-size: 14px;")
        else:
            self.error_label.setText(message)
            self.error_label.setStyleSheet("color: red; font-size: 14px;")

    def get_file_paths(self):
        """선택된 파일 경로 리스트 반환"""
        return self.file_uploader.get_file_paths()