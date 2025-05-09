from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QStackedWidget, QTabBar)
from PyQt5.QtGui import QCursor, QFont
import os

from app.core.input.pre_assign import run_allocation
from app.core.input.maintenance import run_maintenance_analysis
from app.models.common.fileStore import FilePaths, DataStore

from app.views.components.data_upload_components.date_range_selector import DateRangeSelector
from app.views.components.data_upload_components.file_upload_component import FileUploadComponent
from app.views.components.data_upload_components.parameter_component import ParameterComponent
from app.views.components.data_upload_components.file_explorer_sidebar import FileExplorerSidebar

# 분리된 관리자 클래스 가져오기
from app.views.components.data_upload_components.data_input_components import FileTabManager
from app.views.components.data_upload_components.data_input_components import DataModifier
from app.views.components.data_upload_components.data_input_components import SidebarManager
from app.views.components.data_upload_components.save_confirmation_dialog import SaveConfirmationDialog

class DataInputPage(QWidget):
    # 시그널 정의
    file_selected = pyqtSignal(str)
    date_range_selected = pyqtSignal(QDate, QDate)
    run_button_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loaded_files = {}  # 로드된 파일과 해당 데이터프레임을 저장
        self.current_file = None
        self.current_sheet = None

        # UI 초기화
        self.init_ui()

        # 관리자 클래스 초기화 (UI 초기화 후에 해야 함)
        self.sidebar_manager = SidebarManager(self)
        self.tab_manager = FileTabManager(self)
        self.data_modifier = DataModifier(self)


        # 시그널 연결
        self._connect_signals()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 전체 컨테이너 생성
        main_container = QFrame()
        main_container.setStyleSheet("border:none; border-radius: 5px;")
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)

        # 제목과 입력 섹션을 포함할 컨테이너 생성
        top_container = QFrame()
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(10, 10, 10, 10)
        top_container_layout.setSpacing(10)
        top_container.setStyleSheet("background-color: #F5F5F5; border-radius: 5px;")
        top_container.setFixedHeight(150)

        # 제목과 버튼을 포함할 상단 행 컨테이너
        title_row = QFrame()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 16, 0)

        # 제목 레이블 생성
        title_label = QLabel("Upload Data")
        title_font = QFont()
        title_font.setFamily("Arial")
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_font.setWeight(99)
        title_label.setFont(title_font)

        title_row_layout.addWidget(title_label, 1)

        save_btn = QPushButton("Save")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setStyleSheet("""
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
                    """
        )
        save_btn.setFixedWidth(150)
        save_btn.setFixedHeight(50)


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
        save_btn.setFont(run_font)

        # 버튼 클릭 시그널 연결
        run_btn.clicked.connect(self.on_run_clicked)
        save_btn.clicked.connect(self.on_save_clicked)

        title_row_layout.addWidget(save_btn)
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
        input_layout.addWidget(self.date_selector, 1)
        input_layout.addWidget(self.file_uploader, 3)

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
        main_splitter.setHandleWidth(10)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #F5F5F5; }")
        main_splitter.setContentsMargins(0, 0, 0, 0)

        # 왼쪽 사이드바 (파일 탐색기)
        self.file_explorer = FileExplorerSidebar()

        # 오른쪽 콘텐츠 영역 (선택된 파일/시트 내용)
        right_area = QFrame()
        right_area.setFrameShape(QFrame.NoFrame)
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

        # 콘텐츠 영역
        self.stacked_widget = QStackedWidget()

        # 레이아웃에 추가
        tab_layout.addWidget(self.tab_bar)
        tab_layout.addWidget(self.stacked_widget)

        # 파라미터 영역
        parameter_container = QFrame()
        parameter_container.setStyleSheet("background-color: white; border-radius: 10px; border: 3px solid #cccccc;")
        parameter_layout = QHBoxLayout(parameter_container)  # QVBoxLayout에서 QHBoxLayout으로 변경
        parameter_layout.setContentsMargins(5, 5, 5, 5)

        # 수평 스플리터 추가
        parameter_splitter = QSplitter(Qt.Horizontal)
        parameter_splitter.setHandleWidth(3)
        parameter_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                width: 1px;
            }
        """)

        # 왼쪽 영역 (새로 추가)
        left_parameter_area = QFrame()
        left_parameter_area.setStyleSheet("background-color: white; border: none;")
        left_parameter_layout = QVBoxLayout(left_parameter_area)
        left_parameter_layout.setContentsMargins(5, 5, 5, 5)

        # 왼쪽 영역에 임시 레이블 추가 (나중에 실제 컴포넌트로 대체)
        left_label = QLabel("왼쪽 파라미터 영역")
        left_label.setAlignment(Qt.AlignCenter)
        left_parameter_layout.addWidget(left_label)

        # 오른쪽 영역 (기존 ParameterComponent 포함)
        right_parameter_area = QFrame()
        right_parameter_area.setStyleSheet("background-color: white; border: none;")
        right_parameter_layout = QVBoxLayout(right_parameter_area)
        right_parameter_layout.setContentsMargins(5, 5, 5, 5)

        # 기존 ParameterComponent 추가
        self.parameter_component = ParameterComponent()
        right_parameter_layout.addWidget(self.parameter_component)

        # 스플리터에 왼쪽/오른쪽 영역 추가
        parameter_splitter.addWidget(left_parameter_area)
        parameter_splitter.addWidget(right_parameter_area)

        # 7:3 비율로 설정
        parameter_splitter.setSizes([700, 300])

        # 메인 레이아웃에 스플리터 추가
        parameter_layout.addWidget(parameter_splitter)

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
        main_splitter.setSizes([150, 850])  # 초기 크기 설정

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

        self.file_selected.connect(self.parameter_component.on_file_selected)

        # 파일 탐색기 시그널
        self.file_explorer.file_or_sheet_selected.connect(
            self.sidebar_manager.on_file_or_sheet_selected)

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

        self.register_file_path(file_path)
        self.run_combined_analysis()

    def on_file_removed(self, file_path):
        """파일이 삭제되면 사이드바에서도 제거하고 관련된 모든 탭 닫기"""
        # 사이드바 관리자를 통해 파일 제거
        result = self.sidebar_manager.remove_file_from_sidebar(file_path)

        # 탭 관리자를 통해 관련 탭 닫기
        self.tab_manager.close_file_tabs(file_path)

        # 상태 메시지 업데이트
        file_name = os.path.basename(file_path)
        self.update_status_message(True, f"파일 '{file_name}'이(가) 제거되었습니다")

        try:
            solution, failures = run_allocation()
            self.parameter_component.show_failures.emit(solution, failures)
        except Exception as e:
            print(f"[preAssign 자동분석] 오류 발생: {e}")

    def on_run_clicked(self):
        """Run 버튼 클릭 시 호출되는 함수 - 모든 데이터프레임 DataStore에 저장"""
        print("Run 버튼 클릭됨 - 현재 탭의 데이터 저장 및 모든 데이터프레임 전달")

        # 현재 열려있는 탭의 데이터 저장
        self.tab_manager.save_current_tab_data()

        modified_data = self.data_modifier.get_all_modified_data()

        if modified_data:
            # 변경 사항이 있으면 다이얼로그 표시
            choice = SaveConfirmationDialog.show_dialog(self)

            if choice == "save_and_run":
                # 저장 후 실행
                self.on_save_clicked()
                # DataStore에서 모든 데이터프레임 준비
                self.prepare_dataframes_for_optimization()
                # 기존 시그널 발생
                self.run_button_clicked.emit()
            elif choice == "run_without_save":
                # 저장하지 않고 실행
                # DataStore에서 모든 데이터프레임 준비
                self.prepare_dataframes_for_optimization()
                # 기존 시그널 발생
                self.run_button_clicked.emit()
            else:  # "cancel"
                # 작업 취소
                return
        else:
            # 변경 사항이 없으면 바로 실행
            # DataStore에서 모든 데이터프레임 준비
            self.prepare_dataframes_for_optimization()
            # 기존 시그널 발생
            self.run_button_clicked.emit()

    def prepare_dataframes_for_optimization(self):
        """최적화를 위한 데이터프레임 준비 및 저장"""
        # DataStore에서 모든 데이터프레임 가져오기
        all_dataframes = DataStore.get("dataframes", {})

        # 각 파일 유형별로 데이터프레임 구성
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

    def update_status_message(self, success, message):
        """상태 메시지 업데이트"""
        if success:
            print(f"성공: {message}")
        else:
            print(f"오류: {message}")

    def get_file_paths(self):
        """선택된 파일 경로 리스트 반환"""
        return self.file_uploader.get_file_paths()

    def register_file_path(self, file_path):
        """파일 경로를 FilePaths에 등록"""
        fn = os.path.basename(file_path).lower()
        if "demand" in fn:
            FilePaths.set("demand_excel_file", file_path)
        elif "dynamic" in fn:
            FilePaths.set("dynamic_excel_file", file_path)
        elif "master" in fn:
            FilePaths.set("master_excel_file", file_path)
        elif "pre_assign" in fn:
            FilePaths.set("pre_assign_excel_file", file_path)
        else:
            FilePaths.set("etc_excel_file", file_path)

    def run_combined_analysis(self):
        """파일 분석 실행"""
        try:
            solution, failures = run_allocation()
            print(failures)

            failed_items, failed_rmcs = run_maintenance_analysis()
            print(failed_items, failed_rmcs)

            failures["plan_adherence_rate"] = {
                "item_failures": failed_items,
                "rmc_failures": failed_rmcs
            }

            self.parameter_component.show_failures.emit(failures)
        except Exception as e:
            print(f"[preAssign 분석] 오류 발생: {e}")

    def on_save_clicked(self):
        """Save 버튼 클릭 시 호출되는 함수 - 현재 데이터를 원본 파일에 저장"""
        import pandas as pd

        print("Save 버튼 클릭됨 - 원본 파일에 변경사항 저장")

        # 현재 탭 데이터 저장 (내부 저장소에만)
        self.tab_manager.save_current_tab_data()

        # 모든 수정된 데이터 가져오기
        modified_data = self.data_modifier.get_all_modified_data()

        if not modified_data:
            print("저장할 변경사항이 없습니다.")
            return

        success_count = 0
        error_count = 0

        # 각 파일에 대해 처리
        for file_path, sheets in modified_data.items():
            file_ext = os.path.splitext(file_path)[1].lower()

            try:
                if file_ext == '.csv':
                    # CSV 파일 처리
                    if 'data' in sheets:
                        df = sheets['data']
                        df.to_csv(file_path, index=False, encoding='utf-8')
                        success_count += 1
                elif file_ext in ['.xls', '.xlsx']:
                    # 엑셀 파일 처리
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        for sheet_name, df in sheets.items():
                            if sheet_name != 'data':  # data는 CSV용 특수 키
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                    success_count += 1
            except Exception as e:
                print(f"파일 '{file_path}' 저장 중 오류 발생: {str(e)}")
                error_count += 1

        # 저장 후 수정 상태 초기화
        if success_count > 0:
            self.data_modifier.modified_data_dict.clear()

            # UI 업데이트 - 모든 탭과 사이드바 항목의 '*' 제거
            for (file_path, sheet_name), idx in self.tab_manager.open_tabs.items():
                self.data_modifier.remove_modified_status_in_sidebar(file_path, sheet_name)
                self.tab_manager.update_tab_title(file_path, sheet_name, False)

        # 결과 메시지
        if error_count == 0:
            self.update_status_message(True, f"{success_count}개 파일 저장 완료")
        else:
            self.update_status_message(False, f"{success_count}개 파일 저장 완료, {error_count}개 파일 저장 실패")