from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QStackedWidget, QTabBar)
from PyQt5.QtGui import QCursor, QFont

import os

from app.views.components.data_upload_components.date_range_selector import DateRangeSelector
from app.views.components.data_upload_components.file_upload_component import FileUploadComponent
from app.views.components.data_upload_components.parameter_component import ParameterComponent
from app.views.components.data_upload_components.file_explorer_sidebar import FileExplorerSidebar

# 분리된 관리자 클래스 가져오기
from app.views.components.data_upload_components.data_input_components import FileTabManager
from app.views.components.data_upload_components.data_input_components import DataModifier
from app.views.components.data_upload_components.data_input_components import SidebarManager


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

        # UI 초기화
        self.init_ui()

        # 관리자 클래스 초기화 (UI 초기화 후에 해야 함)
        self.tab_manager = FileTabManager(self)
        self.data_modifier = DataModifier(self)
        self.sidebar_manager = SidebarManager(self)

        # 시그널 연결
        self._connect_signals()

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

        # Run 버튼 생성
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

        # 폰트 설정
        run_font = QFont("Arial", 9)
        run_font.setBold(True)
        run_btn.setFont(run_font)

        # 버튼 클릭 시그널 연결
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

        # 오른쪽 섹션: 파일 업로드 컴포넌트 사용
        self.file_uploader = FileUploadComponent()

        # 입력 레이아웃에 위젯 추가
        input_layout.addWidget(self.date_selector, 1)  # 왼쪽에 날짜 선택기
        input_layout.addWidget(self.file_uploader, 3)  # 오른쪽에 파일 업로더

        # 컨테이너에 제목 행과 입력 섹션 추가
        top_container_layout.addWidget(title_row)
        top_container_layout.addWidget(input_section)

        # 하단 영역을 위한 컨테이너 생성
        bottom_container = QFrame()
        bottom_container.setStyleSheet("background-color: #F5F5F5; border-radius: 10px; border:none;")
        bottom_container_layout = QVBoxLayout(bottom_container)
        bottom_container_layout.setContentsMargins(10, 10, 10, 10)

        # IDE 스타일 레이아웃을 위한 메인 스플리터 (수평 분할)
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(10)  # 스플리터 핸들 너비 설정
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #F5F5F5; }")
        main_splitter.setContentsMargins(0, 0, 0, 0)

        # 왼쪽 사이드바 (파일 탐색기)
        self.file_explorer = FileExplorerSidebar()

        # 오른쪽 콘텐츠 영역 (선택된 파일/시트 내용)
        right_area = QFrame()
        right_area.setFrameShape(QFrame.NoFrame)  # 프레임 모양 제거
        right_area.setStyleSheet("background-color: #F5F5F5; border-radius: 10px; border: none;")
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # 오른쪽 영역에 수직 스플리터 추가 (탭 영역과 파라미터 영역 분리)
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setHandleWidth(10)
        vertical_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #F5F5F5;
                height: 10px;
            }
        """)

        # 탭 영역 컨테이너
        tab_container = QWidget()
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        # 탭 바
        self.tab_bar = QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setDrawBase(False)  # 기본 라인 제거
        self.tab_bar.setStyleSheet("""
            QTabBar {
                background-color: transparent;
                border: none;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 6px 10px;
                margin-right: 2px;
                margin-bottom: 0px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #1428A0;
                color: white;
            }
        """)

        # 콘텐츠 영역
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("border: 2px solid #cccccc; background-color: white;")

        # 초기 "Start Page" 추가 (나중에 tab_manager에서 처리)
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_msg = QLabel("Select a file or sheet from the sidebar to open a new tab")
        empty_msg.setAlignment(Qt.AlignCenter)
        empty_msg.setStyleSheet("color: #888; font-size: 14px; font-family: Arial; font-weight: bold;")
        empty_layout.addWidget(empty_msg)

        self.stacked_widget.addWidget(empty_widget)
        self.tab_bar.addTab("Start Page")

        # 레이아웃에 추가
        tab_layout.addWidget(self.tab_bar)
        tab_layout.addWidget(self.stacked_widget)

        # 파라미터 영역
        parameter_container = QFrame()
        parameter_container.setStyleSheet("background-color: white; border-radius: 10px; border: 3px solid #cccccc;")
        parameter_layout = QVBoxLayout(parameter_container)
        parameter_layout.setContentsMargins(10, 10, 10, 10)

        self.parameter_component = ParameterComponent()
        parameter_layout.addWidget(self.parameter_component)

        # 수직 스플리터에 탭 컨테이너와 파라미터 컨테이너 추가
        vertical_splitter.addWidget(tab_container)
        vertical_splitter.addWidget(parameter_container)

        # 스플리터 사이즈 설정 (70%:30% 비율로 초기화)
        vertical_splitter.setSizes([700, 300])

        # 오른쪽 영역 레이아웃에 수직 스플리터 추가
        right_layout.addWidget(vertical_splitter)

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

    def _connect_signals(self):
        """시그널 연결"""
        # 날짜 범위 선택 시그널
        self.date_selector.date_range_changed.connect(self.on_date_range_changed)

        # 파일 관련 시그널
        self.file_uploader.file_selected.connect(self.on_file_selected)
        self.file_uploader.file_removed.connect(self.on_file_removed)

        # 파일 탐색기 시그널
        self.file_explorer.file_or_sheet_selected.connect(
            self.sidebar_manager.on_file_or_sheet_selected)

        # 탭 관련 시그널
        self.tab_bar.currentChanged.connect(self.tab_manager.on_tab_changed)
        self.tab_bar.tabCloseRequested.connect(self.tab_manager.on_tab_close_requested)
        self.tab_bar.tabMoved.connect(self.tab_manager.on_tab_moved)
        self.tab_bar.setTabsClosable(True)

    def on_date_range_changed(self, start_date, end_date):
        """날짜 범위가 변경되면 시그널 발생"""
        print(f"날짜 범위 변경: {start_date.toString('yyyy-MM-dd')} ~ {end_date.toString('yyyy-MM-dd')}")
        self.date_range_selected.emit(start_date, end_date)

    def on_file_selected(self, file_path):
        """파일이 선택되면 시그널 발생 및 사이드바에 추가"""
        print(f"파일 선택됨: {file_path}")
        self.file_selected.emit(file_path)

        # 사이드바 관리자를 통해 파일 추가
        success, message = self.sidebar_manager.add_file_to_sidebar(file_path)
        self.update_status_message(success, message)

    def on_file_removed(self, file_path):
        """파일이 삭제되면 사이드바에서도 제거하고 관련된 모든 탭 닫기"""
        # 사이드바 관리자를 통해 파일 제거
        result = self.sidebar_manager.remove_file_from_sidebar(file_path)

        # 탭 관리자를 통해 관련 탭 닫기
        self.tab_manager.close_file_tabs(file_path)

        # 상태 메시지 업데이트
        file_name = os.path.basename(file_path)
        self.update_status_message(True, f"파일 '{file_name}'이(가) 제거되었습니다")

    def on_run_clicked(self):
        """Run 버튼 클릭 시 호출되는 함수 - 모든 데이터프레임 DataStore에 저장"""
        print("Run 버튼 클릭됨 - 현재 탭의 데이터 저장 및 모든 데이터프레임 전달")

        # 현재 열려있는 탭의 데이터 저장
        current_tab_index = self.tab_bar.currentIndex()
        if current_tab_index >= 0 and current_tab_index < self.stacked_widget.count():
            current_tab_widget = self.stacked_widget.widget(current_tab_index)
            if current_tab_widget:
                # 현재 탭에 해당하는 파일과 시트 찾기
                current_file_path = None
                current_sheet_name = None
                for (file_path, sheet_name), idx in self.tab_manager.open_tabs.items():
                    if idx == current_tab_index:
                        current_file_path = file_path
                        current_sheet_name = sheet_name
                        break

                if current_file_path:
                    # 현재 탭 데이터 저장
                    self.data_modifier.save_tab_data(current_tab_widget, current_file_path, current_sheet_name)

        # DataStore에서 모든 데이터프레임 가져오기
        from app.models.common.fileStore import DataStore, FilePaths
        all_dataframes = DataStore.get("dataframes", {})

        # 수정된 사항 확인을 위한 상세 로그 추가
        print("\n===== 데이터프레임 저장 전 상세 정보 =====")
        print(f"전체 데이터프레임 개수: {len(all_dataframes)}")
        for key, df in all_dataframes.items():
            # 데이터프레임의 기본 정보 출력
            if df is not None:
                print(f"데이터프레임 키: {key}")
                print(f"  - 크기: {df.shape}")
                print(f"  - 컬럼: {df.columns.tolist()}")
                print(f"  - 데이터 샘플: {df.head(2).to_dict('records')}")

                # 수정 여부 확인 (데이터 수정자에서 추적 중인 경우)
                is_modified = False
                # 마지막 콜론의 위치 찾기
                if ":" in key:
                    # 키 형식에서 파일 경로와 시트 이름 분리 (마지막 콜론 기준)
                    last_colon_index = key.rfind(":")
                    if last_colon_index > 0:  # 콜론이 있는지 확인
                        file_path = key[:last_colon_index]
                        sheet_name = key[last_colon_index + 1:]

                        if (file_path in self.data_modifier.modified_data_dict and
                                sheet_name in self.data_modifier.modified_data_dict[file_path]):
                            is_modified = True
                else:
                    if (key in self.data_modifier.modified_data_dict and
                            'data' in self.data_modifier.modified_data_dict[key]):
                        is_modified = True

                print(f"  - 수정됨: {is_modified}")
            else:
                print(f"데이터프레임 키: {key} - 데이터 없음")
        print("========================================\n")

        # 기존 방식의 simplified_dataframes 생성 (파일 경로 기준)
        simplified_dataframes = {}
        for key, df in all_dataframes.items():
            # 키 형식이 "file_path:sheet_name"인 경우 또는 그냥 file_path인 경우
            if ":" in key:
                # 마지막 콜론의 위치 찾기
                last_colon_index = key.rfind(":")
                if last_colon_index > 0:  # 콜론이 있는지 확인
                    file_path = key[:last_colon_index]
                    sheet_name = key[last_colon_index + 1:]

                    if file_path not in simplified_dataframes:
                        simplified_dataframes[file_path] = {}
                    simplified_dataframes[file_path][sheet_name] = df
            else:
                # 시트가 없는 파일 (CSV 등)
                simplified_dataframes[key] = df

        # 단순화된 데이터프레임 딕셔너리 DataStore에 저장
        DataStore.set("simplified_dataframes", simplified_dataframes)
        print(f"파일경로 기준 데이터프레임 저장됨: {len(simplified_dataframes)}개 파일, {len(all_dataframes)}개 데이터프레임")

        # 새로운 데이터 구조 - 파일 유형별로 구성
        organized_dataframes = {
            "demand": {},
            "dynamic": {},
            "master": {},
            "etc": {}
        }

        # 파일 유형 결정 함수
        def get_file_type(file_path):
            file_name = os.path.basename(file_path).lower()
            if "demand" in file_name:
                return "demand"
            elif "dynamic" in file_name:
                return "dynamic"
            elif "master" in file_name:
                return "master"
            else:
                return "etc"

        # 모든 데이터프레임을 새 구조로 재구성
        for key, df in all_dataframes.items():
            if ":" in key:  # 엑셀 파일의 시트
                file_path, sheet_name = key.rsplit(":", 1)
                file_type = get_file_type(file_path)
                organized_dataframes[file_type][sheet_name] = df
            else:  # CSV 파일 등
                file_type = get_file_type(key)
                # CSV 파일은 파일명에서 확장자를 제거하여 키로 사용
                file_name = os.path.basename(key).split('.')[0]
                organized_dataframes[file_type][file_name] = df

        # 유형별 데이터프레임 딕셔너리 DataStore에 저장
        DataStore.set("organized_dataframes", organized_dataframes)
        print(f"유형별 데이터프레임 저장됨:")
        for file_type, sheets in organized_dataframes.items():
            print(f"  - {file_type}: {len(sheets)}개 시트/파일")

            # 각 유형의 시트 정보 상세 출력
            if sheets:
                print(f"\n{file_type} 데이터 상세 정보:")
                for sheet_name, df in sheets.items():
                    print(f"    * 시트: {sheet_name}")
                    print(f"      - 크기: {df.shape}")
                    print(f"      - 컬럼: {df.columns.tolist()[:5]}..." if len(
                        df.columns) > 5 else f"      - 컬럼: {df.columns.tolist()}")
                    if not df.empty:
                        print(f"      - 첫 번째 행 샘플: {df.iloc[0].to_dict()}")

        # 기존 시그널 발생
        self.run_button_clicked.emit()

    def update_status_message(self, success, message):
        """상태 메시지 업데이트"""
        if success:
            print(f"성공: {message}")
        else:
            print(f"오류: {message}")

    def get_file_paths(self):
        """선택된 파일 경로 리스트 반환"""
        return self.file_uploader.get_file_paths()