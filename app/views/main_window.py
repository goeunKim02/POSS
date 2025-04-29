from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from app.core.input.capaAnalysis import PjtGroupAnalyzer
from app.models.input.capa import process_data
from app.views.components import Navbar, DataInputPage, PlanningPage,ResultPage
from app.views.models.data_model import DataModel
from app.models.common.fileStore import FilePaths
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon, QFont
import pandas as pd
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Samsung Production Planning Optimization System")
        self.resize(1920, 980)

        # Create a smaller icon
        app_icon = QIcon('../resources/icon/samsung_icon1.png')
        # Create a scaled version of the icon (adjust size as needed)
        scaled_pixmap = app_icon.pixmap(16, 16)  # Small 16x16 icon
        scaled_icon = QIcon(scaled_pixmap)
        self.setWindowIcon(scaled_icon)

        # 데이터 모델 초기화
        self.data_model = DataModel()

        # UI 초기화
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #F5F5F5; border:none;")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 네비게이션 바 추가
        self.navbar = Navbar()
        self.navbar.help_clicked.connect(self.show_help)
        self.navbar.settings_clicked.connect(self.show_settings)
        main_layout.addWidget(self.navbar)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setCursor(QCursor(Qt.PointingHandCursor))
        self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: none;  /* 상단 탭과 연결을 위해 상단 테두리 제거 */
                }
                QTabBar::tab:selected {
                    background-color: #F5F5F5;  /* 선택된 탭의 배경색 (파랑색) */
                    color: black;               /* 선택된 탭의 텍스트 색상 */
                    font-family: Arial, sans-serif;
                    font-weight: bold;
                 
                }
                QTabBar::tab:!selected {
                    background-color: #E4E3E3;  
                    font-family: Arial, sans-serif;
                    font-weight: bold;
                }
                QTabBar::tab {
                    padding: 8px 16px;          /* 탭 내부 여백 */
                    min-width: 250px;           /* 최소 탭 너비 */
                    margin-left: 7px;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    font-family: Arial, sans-serif;
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                }
                QTabBar::tab::first { margin-left: 10px;}
            """)



        # 페이지 컴포넌트 생성 - main_window 전달
        self.data_input_page = DataInputPage()
        self.data_input_page.file_selected.connect(self.on_file_selected)

        self.planning_page = PlanningPage(self)  # self 전달
        # 시그널이 정의되지 않았으므로 연결 제거 또는 시그널 추가 필요

        self.result_page = ResultPage(self)  # self 전달
        self.analysis_page = AnalysisPage(self)
        # 시그널이 정의되지 않았으므로 연결 제거 또는 시그널 추가 필요

        # 페이지를 탭에 추가
        self.tab_widget.addTab(self.data_input_page, "Data Input")
        self.tab_widget.addTab(self.planning_page, "Pre-Assigned Result")
        self.tab_widget.addTab(self.result_page, "Results")
        self.tab_widget.addTab(self.analysis_page, "Results Adjustment")

        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central_widget)

    def navigate_to_page(self, index):
        """특정 인덱스의 탭으로 이동"""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)

    def show_help(self):
        # 도움말 창 표시 로직
        print("도움말 표시")

    def show_settings(self):
        # 설정 창 표시 로직
        print("설정 표시")

    def on_file_selected(self, file_path):
        # 파일 경로를 데이터 모델에 저장
        self.data_model.set_file_path(file_path)

        # filePath 경로 중앙 관리를 위한 저장
        file_name = os.path.basename(file_path)

        if "demand" in file_name :
            FilePaths.set("demand_excel_file", file_path)
        elif "dynamic" in file_name:
            FilePaths.set("dynamic_excel_file", file_path)
        elif "master" in file_name:
            FilePaths.set("master_excel_file", file_path)
        else:
            FilePaths.set("etc_excel_file", file_path)

        processed_data = process_data()
        
        if processed_data :
            from app.core.input.capaValidator import validate_distribution_ratios
            validation_results = validate_distribution_ratios(processed_data)
            print(validation_results)
            # self.display_validation_results(validation_results)

            try:
                analyzer = PjtGroupAnalyzer(processed_data)
                results = analyzer.analyze()
                self.data_model.analysis_results = results

            except Exception as e:
                print(f"프로젝트 그룹 분석 중 오류 발생: {e}")
                import traceback
                print(traceback.format_exc())
        else :
            print("데이터 처리에 실패했습니다")

    def run_optimization(self, parameters=None):
        # 생산계획 최적화 실행 로직
        print(f"생산계획 최적화 실행: {parameters}")
        # self.data_model.process_data(parameters)

    def export_results(self, file_path=None):
        # 결과 내보내기 로직
        print(f"결과를 다음 경로에 저장: {file_path}")
        # self.data_model.export_results(file_path)