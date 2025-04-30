from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QTabWidget)
from PyQt5.QtGui import QCursor, QFont

import os
import pandas as pd

from app.views.components.data_upload_components.date_range_selector import DateRangeSelector
from app.views.components.data_upload_components.file_upload_component import FileUploadComponent
from app.views.components.data_upload_components.parameter_component import ParameterComponent
from app.views.components.data_upload_components.file_explorer_sidebar import FileExplorerSidebar
from app.views.components.data_upload_components.enhanced_table_filter_component import EnhancedTableFilterComponent
from app.views.components.data_upload_components.data_table_component import DataTableComponent


class DataInputPage(QWidget):
    file_selected = pyqtSignal(str)
    date_range_selected = pyqtSignal(QDate, QDate)
    run_button_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loaded_files = {}  # 로드된 파일과 해당 데이터프레임을 저장
        self.current_file = None
        self.current_sheet = None
        self.open_tabs = {}  # {(file_path, sheet_name): tab_index} 형태로 열린 탭 추적
        self.is_updating_ui = False  # 이벤트 루프 방지용 플래그 추가
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 메인 컨테이너
        main_container = self._create_main_container()
        layout.addWidget(main_container)

    def _create_main_container(self):
        """메인 컨테이너 생성"""
        main_container = QFrame()
        main_container.setStyleSheet("border:none; border-radius: 5px;")

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 섹션 (제목, 버튼, 입력 필드)
        top_container = self._create_top_container()

        # 하단 섹션 (파일 탐색기, 데이터 표시)
        bottom_container = self._create_bottom_container()

        main_layout.addWidget(top_container)
        main_layout.addWidget(bottom_container, 1)

        return main_container

    def _create_top_container(self):
        """상단 컨테이너 생성 (제목, 버튼, 입력 필드)"""
        top_container = QFrame()
        top_container.setStyleSheet("background-color: #F5F5F5; border-radius: 5px;")
        top_container.setFixedHeight(150)

        layout = QVBoxLayout(top_container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 제목 행
        title_row = self._create_title_row()

        # 입력 섹션
        input_section = self._create_input_section()

        layout.addWidget(title_row)
        layout.addWidget(input_section)

        return top_container

    def _create_title_row(self):
        """제목과 Run 버튼 행 생성"""
        title_row = QFrame()
        layout = QHBoxLayout(title_row)
        layout.setContentsMargins(0, 0, 16, 0)

        # 제목
        title_label = QLabel("Upload Data")
        title_font = QFont("Arial", 15)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)

        # Run 버튼
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

        run_font = QFont("Arial", 9)
        run_font.setBold(True)
        run_btn.setFont(run_font)

        run_btn.clicked.connect(self.on_run_clicked)

        layout.addWidget(title_label, 1)
        layout.addWidget(run_btn)

        return title_row

    def _create_input_section(self):
        """날짜 선택기와 파일 업로더 섹션 생성"""
        input_section = QFrame()
        input_section.setFrameShape(QFrame.StyledPanel)
        input_section.setStyleSheet("background-color: white; border-radius: 10px; border: 3px solid #cccccc;")
        input_section.setFixedHeight(70)

        layout = QHBoxLayout(input_section)
        layout.setContentsMargins(10, 5, 10, 5)

        # 날짜 선택기
        self.date_selector = DateRangeSelector()
        self.date_selector.date_range_changed.connect(self.on_date_range_changed)

        # 파일 업로더
        self.file_uploader = FileUploadComponent()
        self.file_uploader.file_selected.connect(self.on_file_selected)
        self.file_uploader.file_removed.connect(self.on_file_removed)

        layout.addWidget(self.date_selector, 1)
        layout.addWidget(self.file_uploader, 3)

        return input_section

    def _create_bottom_container(self):
        """하단 컨테이너 생성 (파일 탐색기, 데이터 표시)"""
        bottom_container = QFrame()
        bottom_container.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")

        layout = QVBoxLayout(bottom_container)
        layout.setContentsMargins(10, 10, 10, 10)

        # 메인 스플리터
        splitter = self._create_main_splitter()
        layout.addWidget(splitter)

        return bottom_container

    def _create_main_splitter(self):
        """메인 스플리터 생성 (파일 탐색기와 콘텐츠 영역)"""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("background-color: transparent;")
        splitter.setContentsMargins(0, 0, 0, 0)

        # 파일 탐색기
        self.file_explorer = FileExplorerSidebar()
        self.file_explorer.file_or_sheet_selected.connect(self.on_file_or_sheet_selected)

        # 콘텐츠 영역
        right_area = self._create_content_area()

        splitter.addWidget(self.file_explorer)
        splitter.addWidget(right_area)
        splitter.setSizes([150, 850])

        return splitter

    def _create_content_area(self):
        """콘텐츠 영역 생성 (시트 탭, 파라미터)"""
        content_area = QFrame()
        content_area.setStyleSheet("background-color: white; border: 1px solid #cccccc; border-radius: 10px;")

        layout = QVBoxLayout(content_area)
        layout.setContentsMargins(5, 5, 5, 5)

        # 콘텐츠 제목
        self.content_title = QLabel("No file selected")
        self.content_title.setFont(QFont("Arial", 10, QFont.Bold))
        self.content_title.setStyleSheet("padding: 5px; background-color: #F5F5F5; border-radius: 5px;")
        self.content_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 시트 탭
        self.sheet_tabs = self._create_sheet_tabs()

        # 파라미터 영역
        parameter_container = QFrame()
        parameter_layout = QVBoxLayout(parameter_container)
        parameter_layout.setContentsMargins(0, 0, 0, 0)

        self.parameter_component = ParameterComponent()
        parameter_layout.addWidget(self.parameter_component)

        layout.addWidget(self.content_title)
        layout.addWidget(self.sheet_tabs, 3)
        layout.addWidget(parameter_container, 1)

        return content_area

    def _create_sheet_tabs(self):
        """시트 탭 위젯 생성"""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
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
        tabs.setTabPosition(QTabWidget.North)
        tabs.setDocumentMode(True)
        tabs.setTabsClosable(True)
        tabs.setMovable(True)
        tabs.currentChanged.connect(self.on_sheet_tab_changed)
        tabs.tabCloseRequested.connect(self.on_tab_close_requested)

        # 초기 빈 탭
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_msg = QLabel("Select a file or sheet from the sidebar to open a new tab")
        empty_msg.setAlignment(Qt.AlignCenter)
        empty_msg.setStyleSheet("color: #888; font-size: 14px;")
        empty_layout.addWidget(empty_msg)

        tabs.addTab(empty_widget, "Start Page")

        return tabs

    def on_date_range_changed(self, start_date, end_date):
        """날짜 범위가 변경되면 시그널 발생"""
        print(f"날짜 범위 변경: {start_date.toString('yyyy-MM-dd')} ~ {end_date.toString('yyyy-MM-dd')}")
        self.date_range_selected.emit(start_date, end_date)

    def on_file_selected(self, file_path):
        """파일이 선택되면 시그널 발생 및 사이드바에 추가"""
        print(f"파일 선택됨: {file_path}")
        self.file_selected.emit(file_path)

        # 파일 처리
        self._process_selected_file(file_path)

    def _process_selected_file(self, file_path):
        """선택된 파일 처리"""
        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            # 엑셀 파일 처리
            if file_ext in ['.xls', '.xlsx']:
                self._process_excel_file(file_path)
            # CSV 파일 처리
            elif file_ext == '.csv':
                self._process_csv_file(file_path)
            else:
                self.update_status_message(False, f"지원되지 않는 파일 형식: {file_ext}")
                return

            # 파일 탐색기에 파일 추가
            sheet_names = self.loaded_files[file_path].get('sheets')
            self.file_explorer.add_file(file_path, sheet_names)

            # 첫 번째 파일인 경우 자동 선택
            if len(self.loaded_files) == 1:
                self.file_explorer.select_first_item()

            self.update_status_message(True, f"파일 '{os.path.basename(file_path)}'이(가) 로드되었습니다")

        except Exception as e:
            self.update_status_message(False, f"파일 로드 오류: {str(e)}")

    def _process_excel_file(self, file_path):
        """엑셀 파일 처리"""
        excel = pd.ExcelFile(file_path)
        sheet_names = excel.sheet_names

        if sheet_names:
            df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_names[0])
            self.loaded_files[file_path] = {
                'df': df,
                'sheets': sheet_names,
                'current_sheet': sheet_names[0]
            }

    def _process_csv_file(self, file_path):
        """CSV 파일 처리"""
        df = DataTableComponent.load_data_from_file(file_path)
        self.loaded_files[file_path] = {
            'df': df,
            'sheets': None,
            'current_sheet': None
        }

    def on_run_clicked(self):
        """Run 버튼 클릭 시 호출되는 함수"""
        print("Run 버튼 클릭됨")
        self.run_button_clicked.emit()

    def on_file_removed(self, file_path):
        """파일이 삭제되면 사이드바에서도 제거하고 관련된 모든 탭 닫기"""
        # 사이드바에서 파일 제거
        self.file_explorer.remove_file(file_path)

        # 해당 파일과 관련된 모든 탭 닫기
        self._close_tabs_for_file(file_path)

        # 로드된 파일 목록에서 제거
        if file_path in self.loaded_files:
            del self.loaded_files[file_path]

        # 현재 표시 중인 파일이 제거된 경우, 화면 초기화
        if self.current_file == file_path:
            self.current_file = None
            self.current_sheet = None
            self.content_title.setText("No file selected")

        self.update_status_message(True, f"파일 '{os.path.basename(file_path)}'이(가) 제거되었습니다")

    def _close_tabs_for_file(self, file_path):
        """특정 파일에 관련된 모든 탭 닫기"""
        tabs_to_remove = []
        for (path, sheet), idx in self.open_tabs.items():
            if path == file_path:
                tabs_to_remove.append((path, sheet))

        # 탭 삭제
        for key in tabs_to_remove:
            self.close_tab(key[0], key[1])

    def on_file_or_sheet_selected(self, file_path, sheet_name):
        """파일 탐색기에서 파일이나 시트가 선택되면 호출"""
        # 무한 루프 방지
        if self.is_updating_ui:
            return

        self.is_updating_ui = True
        try:
            print(f"선택됨: {file_path}, 시트: {sheet_name}")

            # 파일이 로드되지 않은 경우
            if file_path not in self.loaded_files:
                self.update_status_message(False, "선택한 파일이 로드되지 않았습니다")
                return

            self.current_file = file_path
            file_info = self.loaded_files[file_path]

            # 시트 이름 결정
            self.current_sheet = self._determine_sheet_name(file_info, sheet_name)

            # 콘텐츠 제목 업데이트
            self._update_content_title()

            # 탭 열기
            self._open_or_switch_tab()

        finally:
            self.is_updating_ui = False

    def _determine_sheet_name(self, file_info, selected_sheet):
        """적절한 시트 이름 결정"""
        # 시트가 명시적으로 선택된 경우
        if selected_sheet and file_info['sheets'] and selected_sheet in file_info['sheets']:
            return selected_sheet

        # 시트가 선택되지 않은 경우
        if file_info.get('sheets'):
            # 이전에 선택했던 시트나 첫 번째 시트 사용
            return file_info.get('current_sheet') or file_info['sheets'][0]

        # CSV 파일의 경우
        return None

    def _update_content_title(self):
        """콘텐츠 제목 업데이트"""
        if not self.current_file:
            self.content_title.setText("No file selected")
        elif self.current_sheet:
            self.content_title.setText(f"File: {os.path.basename(self.current_file)} - Sheet: {self.current_sheet}")
        else:
            self.content_title.setText(f"File: {os.path.basename(self.current_file)}")

    def _open_or_switch_tab(self):
        """탭 열기 또는 전환"""
        tab_key = (self.current_file, self.current_sheet)

        # 이미 열려 있는 탭인 경우
        if tab_key in self.open_tabs:
            self.sheet_tabs.setCurrentIndex(self.open_tabs[tab_key])
        else:
            # 새 탭 생성
            self._create_new_tab(self.current_file, self.current_sheet)

    def _create_new_tab(self, file_path, sheet_name):
        """새 탭 생성"""
        try:
            file_info = self.loaded_files[file_path]

            # 데이터프레임 로드
            df, tab_title = self._load_data_for_tab(file_path, sheet_name, file_info)

            # 새 탭 위젯 생성
            tab_widget = self._create_tab_widget(df)

            # 탭 추가 및 선택
            tab_index = self.sheet_tabs.addTab(tab_widget, tab_title)
            self.open_tabs[(file_path, sheet_name)] = tab_index
            self.sheet_tabs.setCurrentIndex(tab_index)

            return tab_index

        except Exception as e:
            self.update_status_message(False, f"탭 생성 오류: {str(e)}")
            return -1

    def _load_data_for_tab(self, file_path, sheet_name, file_info):
        """탭에 표시할 데이터 로드"""
        if sheet_name and file_info['sheets'] and sheet_name in file_info['sheets']:
            # 시트가 명시적으로 선택된 경우
            df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_name)
            file_info['df'] = df
            file_info['current_sheet'] = sheet_name
            tab_title = f"{os.path.basename(file_path)} - {sheet_name}"
        else:
            # CSV 파일이거나 시트가 없는 경우
            df = file_info['df']
            tab_title = os.path.basename(file_path)

        return df, tab_title

    def _create_tab_widget(self, df):
        """탭 위젯 생성"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # 필터 컴포넌트
        filter_component = EnhancedTableFilterComponent()

        # 데이터 테이블 컴포넌트
        data_container = DataTableComponent.create_table_from_dataframe(df, filter_component)
        tab_layout.addWidget(data_container)

        return tab_widget

    def on_sheet_tab_changed(self, index):
        """탭이 변경되면 관련 파일과 시트 정보 업데이트하고 사이드바도 동기화"""
        # 무한 루프 방지
        if self.is_updating_ui:
            return

        self.is_updating_ui = True
        try:
            if index < 0 or index >= self.sheet_tabs.count():
                return

            # 시작 페이지인 경우
            if index == 0 and self.sheet_tabs.tabText(0) == "Start Page":
                self.current_file = None
                self.current_sheet = None
                self.content_title.setText("No file selected")
                return

            # 현재 선택된 탭에 해당하는 파일과 시트 찾기
            found = self._find_file_and_sheet_for_tab(index)

            # 탭 정보를 찾지 못한 경우
            if not found and index > 0:
                print(f"Warning: 탭 인덱스 {index}에 해당하는 파일/시트 정보를 찾지 못함")
        finally:
            self.is_updating_ui = False

    def _find_file_and_sheet_for_tab(self, index):
        """탭 인덱스에 해당하는 파일과 시트 정보 찾기"""
        for (file_path, sheet_name), idx in self.open_tabs.items():
            if idx == index:
                self.current_file = file_path
                self.current_sheet = sheet_name

                # 콘텐츠 제목 업데이트
                self._update_content_title()

                # 파일 정보 업데이트
                if file_path in self.loaded_files:
                    file_info = self.loaded_files[file_path]
                    if sheet_name:
                        file_info['current_sheet'] = sheet_name

                # 사이드바 업데이트
                self.file_explorer.select_file_or_sheet(file_path, sheet_name)
                return True

        return False

    def on_tab_close_requested(self, index):
        """탭 닫기 요청 처리"""
        # 열린 탭이 하나밖에 없으면 닫지 않음
        if self.sheet_tabs.count() <= 1:
            return

        # Start Page 탭인 경우
        if index == 0 and self.sheet_tabs.tabText(0) == "Start Page":
            self._close_start_page_tab()
            return

        # 일반 탭인 경우
        tab_key = self._find_tab_key_by_index(index)
        if tab_key:
            self.close_tab(tab_key[0], tab_key[1])

    def _close_start_page_tab(self):
        """Start Page 탭 닫기"""
        self.sheet_tabs.removeTab(0)

        # 남은 모든 탭의 인덱스를 1씩 감소
        updated_open_tabs = {}
        for key, idx in self.open_tabs.items():
            updated_open_tabs[key] = idx - 1
        self.open_tabs = updated_open_tabs

    def _find_tab_key_by_index(self, index):
        """인덱스로 탭 키 찾기"""
        for tab_key, idx in self.open_tabs.items():
            if idx == index:
                return tab_key
        return None

    def close_tab(self, file_path, sheet_name):
        """특정 파일과 시트에 해당하는 탭 닫기"""
        tab_key = (file_path, sheet_name)
        if tab_key in self.open_tabs:
            tab_index = self.open_tabs[tab_key]

            # 탭 제거
            self.sheet_tabs.removeTab(tab_index)
            del self.open_tabs[tab_key]

            # 인덱스 업데이트
            self._update_tab_indices(tab_index)

    def _update_tab_indices(self, removed_index):
        """탭이 삭제된 후 인덱스 업데이트"""
        updated_open_tabs = {}
        for key, idx in self.open_tabs.items():
            if idx > removed_index:
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