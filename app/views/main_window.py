from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QCursor, QIcon, QFont
import pandas as pd
import os
from app.core.optimization import Optimization
from app.core.input.capaAnalysis import PjtGroupAnalyzer
from app.models.input.capa import process_data
from app.views.components import Navbar, DataInputPage, PlanningPage, ResultPage
from app.views.models.data_model import DataModel
from app.models.common.fileStore import FilePaths

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Samsung Production Planning Optimization System")
        self.resize(1920, 980)

        # Create a smaller icon
        # app_icon = QIcon('../resources/icon/samsung_icon1.png')
        # # Create a scaled version of the icon (adjust size as needed)
        # scaled_pixmap = app_icon.pixmap(16, 16)  # Small 16x16 icon
        # scaled_icon = QIcon(scaled_pixmap)
        # self.setWindowIcon(scaled_icon)

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
        # 새로운 시그널 연결 추가
        self.data_input_page.date_range_selected.connect(self.on_date_range_selected)
        self.data_input_page.run_button_clicked.connect(self.on_run_button_clicked)

        self.planning_page = PlanningPage(self)  # self 전달
        self.planning_page.optimization_requested.connect(self.handle_optimization_result)
        # 시그널이 정의되지 않았으므로 연결 제거 또는 시그널 추가 필요

        self.result_page = ResultPage(self)  # self 전달
        # 시그널이 정의되지 않았으므로 연결 제거 또는 시그널 추가 필요

        # 페이지를 탭에 추가
        self.tab_widget.addTab(self.data_input_page, "Data Input")
        self.tab_widget.addTab(self.planning_page, "Pre-Assigned Result")
        self.tab_widget.addTab(self.result_page, "Results")

        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(central_widget)

    def navigate_to_page(self, index):
        """특정 인덱스의 탭으로 이동"""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)

    """ 도움말 표시 실행 함수"""
    def show_help(self):
        from app.views.components.help_dialogs.help_dialog import HelpDialog
        hel_dialog = HelpDialog(self)
        hel_dialog.exec_()
        print("도움말 표시")

    def show_settings(self):
        # 설정 창 표시 로직
        print("설정 표시")

    def on_file_selected(self, file_path):
        # 파일 경로를 데이터 모델에 저장
        self.data_model.set_file_path(file_path)

        # filePath 경로 중앙 관리를 위한 저장
        file_name = os.path.basename(file_path)

        if "demand" in file_name:
            FilePaths.set("demand_excel_file", file_path)
        elif "dynamic" in file_name:
            FilePaths.set("dynamic_excel_file", file_path)
        elif "master" in file_name:
            FilePaths.set("master_excel_file", file_path)
        else:
            FilePaths.set("etc_excel_file", file_path)

        processed_data = process_data()
        
        if processed_data :
            # 제조동별 capa 검증
            from app.core.input.capaValidator import validate_distribution_ratios
            validation_results = validate_distribution_ratios(processed_data)
            print(validation_results)
            # self.display_validation_results(validation_results)

            # PJT Group 분석
            try:
                analyzer = PjtGroupAnalyzer(processed_data)
                results = analyzer.analyze()
                self.data_model.analysis_results = results

            except Exception as e:
                print(f"프로젝트 그룹 분석 중 오류 발생: {e}")
                import traceback
                print(traceback.format_exc())

            # 0 미만 자재 분석
            try :
                from app.core.input.materialAnalyzer import MaterialAnalyzer
                shortage_results = MaterialAnalyzer.analyze_material_shortage()

                if shortage_results :
                    self.data_model.material_shortage_results = shortage_results
            except Exception as e :
                print(f'자재 부족 분석 중 오류 발생 : {e}')

            # 자재만족률 분석
            try :
                from app.core.input.materialRateValidator import analyze_material_satisfaction_all
                # threshold의 값에 따라 기준 비율 바뀜
                satisfaction_results = analyze_material_satisfaction_all(threshold=80)

                if satisfaction_results and 'error' not in satisfaction_results :
                    self.data_model.material_satisfaction_results = satisfaction_results
            except Exception as e :
                print(f'자재만족률 분석 중 오류 발생 : {e}')
                import traceback
                print(traceback.format_exc())
        else :
            print("데이터 처리에 실패했습니다")

    def on_date_range_selected(self, start_date, end_date):
        """날짜 범위가 선택되면 처리"""
        print(f"선택된 날짜 범위: {start_date.toString('yyyy-MM-dd')} ~ {end_date.toString('yyyy-MM-dd')}")

        # 데이터 모델에 날짜 범위 저장
        self.data_model.set_date_range(start_date, end_date)

        # FilePaths에 날짜 정보 저장 (필요한 경우)
        # start_date_str = start_date.toString('yyyy-MM-dd')
        # end_date_str = end_date.toString('yyyy-MM-dd')
        # FilePaths.set("start_date", start_date_str)
        # FilePaths.set("end_date", end_date_str)

    def on_run_button_clicked(self):
        """Run 버튼이 클릭되면 처리 - DataStore에서 데이터프레임 가져와 사용"""
        print("메인 윈도우에서 Run 버튼 처리")

        # 필요한 모든 데이터가 준비되었는지 확인
        demand_file = FilePaths.get("demand_excel_file")
        dynamic_file = FilePaths.get("dynamic_excel_file")
        master_file = FilePaths.get("master_excel_file")

        if not all([demand_file, dynamic_file, master_file]):
            print("필요한 모든 파일이 업로드되지 않았습니다.")
            return

        # DataStore에서 데이터프레임 가져오기
        from app.models.common.fileStore import DataStore
        all_dataframes = DataStore.get("organized_dataframes", {})

        print(f"최적화에 사용할 데이터프레임: {len(all_dataframes)}개 파일")
        for file_path, df_data in all_dataframes.items():
            if isinstance(df_data, dict):  # 엑셀 파일인 경우 (시트별 데이터프레임)
                print(f"  - 파일: {os.path.basename(file_path)}, 시트 수: {len(df_data)}")
            else:  # CSV 파일 등 단일 데이터프레임
                print(f"  - 파일: {os.path.basename(file_path)}, 단일 데이터프레임")

        # 최적화 실행
        optimization = Optimization(all_dataframes)

        # 데이터프레임 전달 (새로운 방법)
        try:
            # Optimization 클래스에 set_data 메소드가 있는지 확인
            if hasattr(optimization, 'set_data') and callable(getattr(optimization, 'set_data')):
                optimization.set_data(all_dataframes)
                print("최적화 엔진에 데이터프레임 전달 완료")
            else:
                print("최적화 엔진에 set_data 메소드가 없습니다. 기존 방식으로 진행합니다.")
        except Exception as e:
            print(f"데이터프레임 전달 중 오류 발생: {str(e)}")

        # 기존 방식으로 최적화 실행
        result_dict = optimization.pre_assign()
        df = result_dict['result']

        # PlanningPage에 결과 전달
        self.planning_page.display_preassign_result(df)

        # 결과 페이지로 이동+
        self.navigate_to_page(1)

    def export_results(self, file_path=None):
        # 결과 내보내기 로직
        print(f"결과를 다음 경로에 저장: {file_path}")
        # self.data_model.export_results(file_path)

    """최적화 결과 처리"""
    def handle_optimization_result(self, results):
        # Args:
        #     results (dict): 최적화 결과를 포함하는 딕셔너리

        # 결과 페이지 초기화 확인
        if not hasattr(self, 'result_page'):
            self.result_page = ResultPage(self)
            self.central_widget.addWidget(self.result_page)
    
        # 결과 페이지의 데이터 업데이트
        if 'assignment_result' in results and results['assignment_result'] is not None:
            self.result_page.left_section.update_data(results['assignment_result'])
