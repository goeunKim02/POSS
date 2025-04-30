from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QHeaderView, QTabWidget, QStackedWidget)
from PyQt5.QtGui import QCursor, QFont

import os

from app.views.components.data_upload_components.date_range_selector import DateRangeSelector
from app.views.components.data_upload_components.file_upload_component import FileUploadComponent
from app.views.components.data_upload_components.sheet_selector_component import SheetSelectorComponent
from app.views.components.data_upload_components.file_tab_component import FileTabComponent
from app.views.components.data_upload_components.parameter_component import ParameterComponent
from app.views.components.data_upload_components.file_explorer_sidebar import FileExplorerSidebar
from app.views.components.data_upload_components.enhanced_table_filter_component import EnhancedTableFilterComponent
from app.views.components.data_upload_components.data_table_component import DataTableComponent


# from app.core.optimization import Optimization

class DataInputPage(QWidget):
    # 시그널 정의
    file_selected = pyqtSignal(str)
    date_range_selected = pyqtSignal(QDate, QDate)
    run_button_clicked = pyqtSignal()  # Run 버튼 클릭 시그널 추가

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loaded_files = {}  # 로드된 파일과 해당 데이터프레임을 저장
        self.current_file = None
        self.current_sheet = None
        self.open_tabs = {}  # {(file_path, sheet_name): tab_index} 형태로 열린 탭 추적
        self.updating_from_tab = False  # 탭에서 선택이 변경되었을 때 사이드바 업데이트 중인지 여부
        self.updating_from_sidebar = False  # 사이드바에서 선택이 변경되었을 때 탭 업데이트 중인지 여부
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 전체 여백 제거
        layout.setSpacing(0)  # 위젯 간 간격 설정

        # 전체 컨테이너 생성
        main_container = QFrame()
        main_container.setStyleSheet("border:none; border-radius: 5px;")
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)  # 내부 위젯 간격

        # 제목과 입력 섹션을 포함할 컨테이너 생성
        top_container = QFrame()
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(10, 10, 10, 10)
        top_container_layout.setSpacing(10)  # 위젯 간 간격 설정
        top_container.setStyleSheet("background-color: #F5F5F5; border-radius: 5px;")
        top_container.setFixedHeight(150)  # 높이 고정

        # 제목과 버튼을 포함할 상단 행 컨테이너
        title_row = QFrame()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 16, 0)  # 여백 설정

        # 제목 레이블 생성
        title_label = QLabel("Upload Data")
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)

        title_row_layout.addWidget(title_label, 1)  # 왼쪽에 제목 배치 (stretch 1)

        # Run 버튼 생성 (수정된 부분)
        run_btn = QPushButton("Run")
        run_btn.setCursor(QCursor(Qt.PointingHandCursor))
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                border: none;
                border-radius: 10px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)
        run_btn.setFixedWidth(150)
        run_btn.setFixedHeight(50)

        # 폰트 설정 (문자열이 아닌 QFont 객체 사용)
        run_font = QFont("Arial", 9)
        run_font.setBold(True)
        run_btn.setFont(run_font)

        # 버튼 클릭 시그널을 mainwindow로 전달
        run_btn.clicked.connect(self.on_run_clicked)

        title_row_layout.addWidget(run_btn)

        # 입력 섹션 생성
        input_section = QFrame()
        input_section.setFrameShape(QFrame.StyledPanel)
        input_section.setStyleSheet("background-color: white; border-radius: 10px; border: 3px solid #cccccc;")
        input_section.setFixedHeight(70)

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

        # 하단 영역을 위한 컨테이너 생성
        bottom_container = QFrame()
        bottom_container.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        bottom_container_layout = QVBoxLayout(bottom_container)
        bottom_container_layout.setContentsMargins(10, 10, 10, 10)

        # IDE 스타일 레이아웃을 위한 메인 스플리터
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("background-color: transparent;")
        main_splitter.setContentsMargins(0, 0, 0, 0)

        # 왼쪽 사이드바 (파일 탐색기)
        self.file_explorer = FileExplorerSidebar()
        self.file_explorer.file_or_sheet_selected.connect(self.on_file_or_sheet_selected)

        # 오른쪽 콘텐츠 영역 (선택된 파일/시트 내용)
        right_area = QFrame()
        right_area.setStyleSheet("background-color: white; border: 1px solid #cccccc; border-radius: 10px;")
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # 콘텐츠 제목 표시 영역
        self.content_title = QLabel("No file selected")
        self.content_title.setFont(QFont("Arial", 10, QFont.Bold))
        self.content_title.setStyleSheet("padding: 5px; background-color: #F5F5F5; border-radius: 5px;")
        self.content_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 시트 탭 영역 - IDE 스타일로 변경
        self.sheet_tabs = QTabWidget()
        self.sheet_tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #1428A0;
                color: white;
            }
        """)
        self.sheet_tabs.setTabPosition(QTabWidget.North)
        self.sheet_tabs.setDocumentMode(True)  # 더 깔끔한 탭 모드
        self.sheet_tabs.setTabsClosable(True)  # 닫기 버튼 추가 (IDE 스타일)
        self.sheet_tabs.setMovable(True)  # 탭 이동 가능
        self.sheet_tabs.currentChanged.connect(self.on_sheet_tab_changed)
        self.sheet_tabs.tabCloseRequested.connect(self.on_tab_close_requested)  # 탭 닫기 이벤트 연결

        # 초기 상태 - 빈 탭 표시
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_msg = QLabel("Select a file or sheet from the sidebar to open a new tab")
        empty_msg.setAlignment(Qt.AlignCenter)
        empty_msg.setStyleSheet("color: #888; font-size: 14px;")
        empty_layout.addWidget(empty_msg)

        # 콘텐츠 영역에 시트 탭 추가
        self.sheet_tabs.addTab(empty_widget, "Start Page")

        # 파라미터 영역
        parameter_container = QFrame()
        parameter_layout = QVBoxLayout(parameter_container)
        parameter_layout.setContentsMargins(0, 0, 0, 0)

        self.parameter_component = ParameterComponent()
        parameter_layout.addWidget(self.parameter_component)

        # 오른쪽 영역 레이아웃에 위젯 추가
        right_layout.addWidget(self.content_title)
        right_layout.addWidget(self.sheet_tabs, 3)  # 시트 탭이 콘텐츠 영역을 대체
        right_layout.addWidget(parameter_container, 1)  # 파라미터 영역

        # 메인 스플리터에 왼쪽 사이드바와 오른쪽 영역 추가
        main_splitter.addWidget(self.file_explorer)
        main_splitter.addWidget(right_area)
        main_splitter.setSizes([200, 800])  # 초기 크기 설정

        # 하단 컨테이너에 스플리터 추가
        bottom_container_layout.addWidget(main_splitter)

        # 메인 컨테이너에 상단 컨테이너와 하단 컨테이너 추가
        main_container_layout.addWidget(top_container)
        main_container_layout.addWidget(bottom_container, 1)

        # 전체 레이아웃에 메인 컨테이너 추가
        layout.addWidget(main_container)

    def on_date_range_changed(self, start_date, end_date):
        """날짜 범위가 변경되면 시그널 발생"""
        print(f"날짜 범위 변경: {start_date.toString('yyyy-MM-dd')} ~ {end_date.toString('yyyy-MM-dd')}")
        self.date_range_selected.emit(start_date, end_date)

    def on_file_selected(self, file_path):
        """파일이 선택되면 시그널 발생 및 사이드바에 추가"""
        print(f"파일 선택됨: {file_path}")
        self.file_selected.emit(file_path)

        # 파일 확장자 확인
        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            # 엑셀 파일인 경우 시트 목록 가져오기
            sheet_names = None
            if file_ext in ['.xls', '.xlsx']:
                import pandas as pd
                excel = pd.ExcelFile(file_path)
                sheet_names = excel.sheet_names

                # 첫 번째 시트 로드
                if sheet_names:
                    df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_names[0])
                    self.loaded_files[file_path] = {'df': df, 'sheets': sheet_names, 'current_sheet': sheet_names[0]}

            # CSV 파일인 경우
            elif file_ext == '.csv':
                df = DataTableComponent.load_data_from_file(file_path)
                self.loaded_files[file_path] = {'df': df, 'sheets': None, 'current_sheet': None}

            # 파일 탐색기에 파일 추가
            self.file_explorer.add_file(file_path, sheet_names)

            # 첫 번째 파일인 경우 자동 선택
            if len(self.loaded_files) == 1:
                self.file_explorer.select_first_item()

            self.update_status_message(True, f"파일 '{os.path.basename(file_path)}'이(가) 로드되었습니다")

        except Exception as e:
            self.update_status_message(False, f"파일 로드 오류: {str(e)}")

    def on_run_clicked(self):
        """Run 버튼 클릭 시 호출되는 함수"""
        print("Run 버튼 클릭됨")
        # MainWindow로 시그널 전달
        self.run_button_clicked.emit()

    def on_file_removed(self, file_path):
        """파일이 삭제되면 사이드바에서도 제거하고 관련된 모든 탭 닫기"""
        # 사이드바에서 파일 제거
        self.file_explorer.remove_file(file_path)

        # 해당 파일과 관련된 모든 탭 찾아서 닫기
        tabs_to_remove = []
        for (path, sheet), idx in self.open_tabs.items():
            if path == file_path:
                tabs_to_remove.append((path, sheet))

        # 탭 삭제 (인덱스는 닫을 때마다 변하므로 역순으로)
        for key in tabs_to_remove:
            self.close_tab(key[0], key[1])

        # 로드된 파일 목록에서 제거
        if file_path in self.loaded_files:
            del self.loaded_files[file_path]

        # 현재 표시 중인 파일이 제거된 경우, 화면 초기화
        if self.current_file == file_path:
            self.current_file = None
            self.current_sheet = None
            self.content_title.setText("No file selected")

        self.update_status_message(True, f"파일 '{os.path.basename(file_path)}'이(가) 제거되었습니다")

    def on_file_or_sheet_selected(self, file_path, sheet_name):
        """파일 탐색기에서 파일이나 시트가 선택되면 호출"""
        print(f"사이드바에서 선택됨: {file_path}, 시트: {sheet_name}")

        # 탭으로부터의 업데이트 중이면 무시 (무한 루프 방지)
        if self.updating_from_tab:
            return

        self.updating_from_sidebar = True

        # 파일이 로드되지 않은 경우
        if file_path not in self.loaded_files:
            self.update_status_message(False, "선택한 파일이 로드되지 않았습니다")
            self.updating_from_sidebar = False
            return

        self.current_file = file_path
        file_info = self.loaded_files[file_path]

        # 시트 이름 결정
        if sheet_name and file_info['sheets'] and sheet_name in file_info['sheets']:
            self.current_sheet = sheet_name
            self.content_title.setText(f"File: {os.path.basename(file_path)} - Sheet: {sheet_name}")
        else:
            # 시트를 명시적으로 선택하지 않은 경우 (파일만 선택)
            if file_info.get('sheets'):
                # 엑셀 파일이고 시트가 있는 경우 기본값 설정
                self.current_sheet = file_info.get('current_sheet') or file_info['sheets'][0]
            else:
                # CSV 파일인 경우
                self.current_sheet = None

            self.content_title.setText(f"File: {os.path.basename(file_path)}")

        # 해당 탭이 이미 열려 있는지 확인
        tab_key = (file_path, self.current_sheet)
        if tab_key in self.open_tabs:
            # 이미 열려 있는 탭으로 전환
            self.sheet_tabs.setCurrentIndex(self.open_tabs[tab_key])
        else:
            # 새 탭 생성
            self._create_new_tab(file_path, self.current_sheet)

        self.updating_from_sidebar = False

    def _create_new_tab(self, file_path, sheet_name):
        """새 탭 생성"""
        try:
            file_info = self.loaded_files[file_path]

            # 데이터프레임 로드
            if sheet_name and file_info['sheets'] and sheet_name in file_info['sheets']:
                # 시트가 명시적으로 선택된 경우
                df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_name)
                file_info['df'] = df  # 현재 로드된 데이터프레임 업데이트
                file_info['current_sheet'] = sheet_name
                tab_title = f"{os.path.basename(file_path)} - {sheet_name}"
            else:
                # CSV 파일이거나 시트가 없는 경우
                df = file_info['df']
                tab_title = os.path.basename(file_path)

            # 새 탭용 위젯 생성
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)

            # 필터 컴포넌트 생성
            filter_component = EnhancedTableFilterComponent()

            # 데이터 테이블 생성
            data_container = DataTableComponent.create_table_from_dataframe(df, filter_component)
            tab_layout.addWidget(data_container)

            # 새 탭 추가
            tab_index = self.sheet_tabs.addTab(tab_widget, tab_title)

            # 탭 상태 저장 및 선택
            self.open_tabs[(file_path, sheet_name)] = tab_index
            self.sheet_tabs.setCurrentIndex(tab_index)

            return tab_index

        except Exception as e:
            self.update_status_message(False, f"탭 생성 오류: {str(e)}")
            return -1

    def on_sheet_tab_changed(self, index):
        """탭이 변경되면 관련 파일과 시트 정보 업데이트"""
        # 사이드바에서 업데이트 중이면 무시 (무한 루프 방지)
        if self.updating_from_sidebar:
            return

        if index < 0 or index >= self.sheet_tabs.count():
            return

        # 시작 페이지인 경우 (인덱스 0)
        if index == 0 and self.sheet_tabs.tabText(0) == "Start Page":
            self.current_file = None
            self.current_sheet = None
            self.content_title.setText("No file selected")
            return

        # 현재 선택된 탭에 해당하는 파일과 시트 찾기
        found = False
        for (file_path, sheet_name), idx in self.open_tabs.items():
            if idx == index:
                found = True
                self.current_file = file_path
                self.current_sheet = sheet_name

                # 제목 업데이트
                if sheet_name:
                    self.content_title.setText(f"File: {os.path.basename(file_path)} - Sheet: {sheet_name}")
                else:
                    self.content_title.setText(f"File: {os.path.basename(file_path)}")

                # 파일 정보 업데이트
                if file_path in self.loaded_files:
                    file_info = self.loaded_files[file_path]
                    if sheet_name:
                        file_info['current_sheet'] = sheet_name

                # 사이드바에서도 동일 항목 선택 처리
                self.updating_from_tab = True
                self.file_explorer.select_file_or_sheet(file_path, sheet_name)
                self.updating_from_tab = False

                break

        if not found:
            self.current_file = None
            self.current_sheet = None

    def on_tab_close_requested(self, index):
        """탭 닫기 요청 처리"""
        # 시작 페이지는 닫을 수 없음
        if index == 0 and self.sheet_tabs.tabText(0) == "Start Page":
            return

        # 닫을 탭에 해당하는 키 찾기
        tab_key_to_close = None
        for tab_key, idx in self.open_tabs.items():
            if idx == index:
                tab_key_to_close = tab_key
                break

        if tab_key_to_close:
            self.close_tab(tab_key_to_close[0], tab_key_to_close[1])

    def close_tab(self, file_path, sheet_name):
        """특정 파일과 시트에 해당하는 탭 닫기"""
        tab_key = (file_path, sheet_name)
        if tab_key in self.open_tabs:
            tab_index = self.open_tabs[tab_key]

            # 탭 제거
            self.sheet_tabs.removeTab(tab_index)
            del self.open_tabs[tab_key]

            # 인덱스 업데이트 (삭제한 탭 이후의 모든 탭 인덱스를 1씩 감소)
            updated_open_tabs = {}
            for key, idx in self.open_tabs.items():
                if idx > tab_index:
                    updated_open_tabs[key] = idx - 1
                else:
                    updated_open_tabs[key] = idx
            self.open_tabs = updated_open_tabs

    def update_status_message(self, success, message):
        """상태 메시지 업데이트"""
        if success:
            print(f"성공: {message}")
        else:
            print(f"오류: {message}")

    def get_file_paths(self):
        """선택된 파일 경로 리스트 반환"""
        return self.file_uploader.get_file_paths()