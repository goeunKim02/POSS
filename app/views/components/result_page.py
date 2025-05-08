import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QFrame, QSplitter, QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QFont
import pandas as pd
from ..components.result_components.modified_left_section import ModifiedLeftSection
from ..components.visualization.mpl_canvas import MplCanvas
from ..components.visualization.visualization_updater import VisualizationUpdater
from app.analysis.output.daily_capa_utilization import CapaUtilization
from app.analysis.output.capa_ratio import CapaRatioAnalyzer
from ..components.result_components.maintenance_rate.plan_maintenance_widget import PlanMaintenanceWidget
from app.utils.export_manager import ExportManager

class ResultPage(QWidget):
    export_requested = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.capa_ratio_data = None
        self.data_changed_count = 0
        self.utilization_data = None # 가동률 데이터 저장 변수
        self.result_data = None # 결과 데이터 저장 변수
        self.init_ui()

        self.connect_signals()

    def init_ui(self):
        # 레이아웃 설정
        result_layout = QVBoxLayout(self)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(0)

        # 타이틀 프레임
        title_frame = QFrame()
        title_frame.setFrameShape(QFrame.StyledPanel)
        title_frame.setStyleSheet("QFrame { min-height:61px; max-height:62px; border:none }")

        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(25, 10, 15, 5)
        title_layout.setSpacing(0)

        # 타이틀 레이블
        title_label = QLabel("Result")

        # QFont를 사용하여 더 두껍게 설정
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(99)
        title_label.setFont(font)

        title_layout.addWidget(title_label, 0, Qt.AlignVCenter)
        title_layout.addStretch(1)

        # 버튼 레이아웃
        export_layout = QHBoxLayout()
        export_layout.setContentsMargins(0, 0, 0, 0)  # 여백 수정
        export_layout.setSpacing(10)

        # Export 버튼
        export_btn = QPushButton()
        export_btn.setText("Export")
        export_btn.setFixedSize(130, 40)
        export_btn.setCursor(QCursor(Qt.PointingHandCursor))
        export_btn.clicked.connect(self.export_results)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                font-weight: bold; 
                padding: 5px 15px; 
                border-radius: 5px; 
            }
            QPushButton:hover {
                background-color: #004C99;
            }
            QPushButton:pressed {
                background-color: #003366;
            }
        """)

        # Report 버튼
        report_btn = QPushButton()
        report_btn.setText("Report")
        report_btn.setFixedSize(130, 40)
        report_btn.setCursor(QCursor(Qt.PointingHandCursor))
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                font-weight: bold; 
                padding: 5px 15px; 
                border-radius: 5px; 
            }
            QPushButton:hover {
                background-color: #004C99;
            }
            QPushButton:pressed {
                background-color: #003366;
            }
        """)

        export_layout.addWidget(export_btn)
        export_layout.addWidget(report_btn)

        # 버튼 레이아웃을 타이틀 레이아웃에 추가
        title_layout.addLayout(export_layout)

        # 타이틀 프레임을 메인 레이아웃에 추가
        result_layout.addWidget(title_frame)

        # QSplitter 생성
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)  # 스플리터 핸들 너비 설정
        splitter.setStyleSheet("QSplitter::handle { background-color: #F5F5F5; }")
        splitter.setContentsMargins(10,10,10,10)

        # 왼쪽 컨테이너
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 3px solid #cccccc;")

        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # 드래그 가능한 테이블 위젯 추가
        self.left_section = ModifiedLeftSection()
        # 데이터 변경 시그널 연결
        self.left_section.data_changed.connect(self.on_data_changed)
        # 셀 이동 시그널 연결
        self.left_section.cell_moved.connect(self.on_cell_moved)
        left_layout.addWidget(self.left_section)

        # 오른쪽 컨테이너 
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 2px solid #cccccc;")

        right_layout = QVBoxLayout(right_frame)

        # 지표 버튼
        button_group_layout = QHBoxLayout()
        button_group_layout.setSpacing(5)
        button_group_layout.setContentsMargins(10, 10, 10, 5)

        self.viz_buttons = []
        viz_types = ["Capa", "Utilization", "PortCapa", "Plan"]
        active_button_style = """
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                font-weight: bold; 
                padding: 8px 15px; 
                border-radius: 4px;
            }
        """
        inactive_button_style = """
            QPushButton {
                background-color: #8E9CC9; 
                color: white; 
                font-weight: bold; 
                padding: 8px 15px; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1428A0;
            }
        """

        # 시각화 콘텐츠를 표시할 스택 위젯
        self.viz_stack = QStackedWidget()

        # 시각화 캔버스 저장
        self.viz_canvases = []

        # 버튼과 콘텐츠 페이지 생성
        for i, btn_text in enumerate(viz_types):
            btn = QPushButton(btn_text)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(active_button_style if i == 0 else inactive_button_style)
            btn.clicked.connect(lambda checked, idx=i: self.switch_viz_page(idx))
            button_group_layout.addWidget(btn)
            self.viz_buttons.append(btn)

            # 해당 버튼에 대응하는 콘텐츠 페이지 생성
            page = QWidget()
            page_layout = QVBoxLayout(page)
            
            # tab 유형 별 처리 
            if btn_text == 'Plan':
                # 계획 유지율 위젯 생성
                self.plan_maintenance_widget = PlanMaintenanceWidget()
                page_layout.addWidget(self.plan_maintenance_widget)

            else: # 다른 탭은 시각화 그대로 유지
                # 페이지에 적절한 시각화 추가
                canvas = MplCanvas(width=6, height=4, dpi=100)
                page_layout.addWidget(canvas)
                
                # 초기 시각화 생성
                self.create_initial_visualization(canvas, btn_text)
            
            # 스택 위젯에 페이지 추가
            self.viz_stack.addWidget(page)

        # 레이아웃에 버튼 그룹과 스택 위젯 추가
        right_layout.addLayout(button_group_layout)
        right_layout.addWidget(self.viz_stack)

        # 스플리터에 프레임 추가
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)

        # 초기 크기 비율 설정 (7:3)
        splitter.setSizes([720, 280])

        # 스플리터를 메인 레이아웃에 추가
        result_layout.addWidget(splitter, 1)  # stretch factor 1로 설정하여 남은 공간 모두 차지

    
    # 시각화 캔버스 초기화 
    def init_visualization_canvases(self):
        self.viz_canvases = []

        # Plan 제외한 탭들의 캔버스 찾기
        for i in range(3):
            page = self.viz_stack.widget(i)
            if page:
                # 페이지 내의 모든 자식 위젯 중 MplCanvas 찾기
                canvas = None
                for child in page.findChildren(MplCanvas):
                    canvas = child
                    break
                
                # 캔버스가 있으면 리스트에 추가
                if canvas:
                    self.viz_canvases.append(canvas)
                else:
                    print(f"Tab {i}에서 캔버스를 찾을 수 없습니다.")


    """이벤트 시그널 연결"""
    def connect_signals(self):
        # 왼쪽 섹션의 데이터 변경 이벤트 연결
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'data_changed'):
            self.left_section.data_changed.connect(self.on_data_changed)
        
        # 아이템 변경 이벤트 연결 (필요한 경우)
        if hasattr(self, 'left_section') and hasattr(self.left_section, 'item_data_changed'):
            self.left_section.item_data_changed.connect(self.on_item_data_changed)


    """아이템 데이터가 변경되었을 때 호출되는 함수"""
    def on_item_data_changed(self, item, new_data):
        # 수량 변경이 있는 경우 계획 유지율 위젯 업데이트
        if 'Qty' in new_data and pd.notna(new_data['Qty']):
            line = new_data.get('Line')
            time = new_data.get('Time')
            item = new_data.get('Item')
            new_qty = new_data.get('Qty')
            demand = new_data.get('Demand', None)  # 선택적 필드

            # 값 변환 및 검증
            try:
                time = int(time) if time is not None else None
                new_qty = int(float(new_qty)) if new_qty is not None else None
            except (ValueError, TypeError):
                print(f"시간 또는 수량 변환 오류: time={time}, qty={new_qty}")
                return

            if line is not None and time is not None and item is not None and new_qty is not None:
                    # 계획 유지율 위젯 업데이트
                    if hasattr(self, 'plan_maintenance_widget'):
                        # 수량 직접 업데이트
                        print(f"수량 업데이트: {line}, {time}, {item}, {new_qty}")
                        self.plan_maintenance_widget.update_quantity(line, time, item, new_qty, demand)
                        
                        # Plan 탭으로 전환 (선택 사항)
                        plan_index = [i for i, btn in enumerate(self.viz_buttons) if btn.text() == "Plan"]
                        if plan_index:
                            self.switch_viz_page(plan_index[0])
        

    """시각화 페이지 전환 및 버튼 스타일 업데이트"""
    def switch_viz_page(self, index):
        self.viz_stack.setCurrentIndex(index)

         # Update button style 
        active_style = """
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                font-weight: bold; 
                padding: 8px 15px; 
                border-radius: 4px;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: #8E9CC9; 
                color: white; 
                font-weight: bold; 
                padding: 8px 15px; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1428A0;
            }
        """

        for i, btn in enumerate(self.viz_buttons):
            btn.setStyleSheet(active_style if i == index else inactive_style)

    """각 지표별 초기 시각화 생성"""
    def create_initial_visualization(self, canvas, viz_type):
        # 각 지표 예시
        if viz_type == "Capa":
            VisualizationUpdater.update_capa_chart(canvas, self.capa_ratio_data)
        

        elif viz_type == "Utilization":
            if self.utilization_data is None:
                try:
                    self.utilization_data = CapaUtilization.analyze_utilization(self.result_data)
                    print("Finished Utilization Rate :", self.utilization_data)
                except Exception as e:
                    print(f"Utilization Rate Error : {str(e)}")
                    self.utilization_data = {}
            
            VisualizationUpdater.update_utilization_chart(canvas, self.utilization_data)

        elif viz_type == "PortCapa":
            pass

    """
    데이터가 변경되었을 때 호출되는 메서드
    데이터프레임을 분석하여 시각화 업데이트
    """
    def on_data_changed(self, data):
        print("on_data_changed 호출됨 - 데이터 변경 감지")
        self.result_data = data
        
        try:
            # 데이터가 비어있지 않은 경우에만 분석 수행
            if data is not None and not data.empty:
                # 데이터 변경 이벤트 카운터 증가
                self.data_changed_count += 1

                # Plan 탭의 계획 유지율 위젯 업데이트
                print("계획 유지율 위젯 업데이트 시작")

                if hasattr(self, 'plan_maintenance_widget'):
                    # 날짜 범위 가져오기 (메인 윈도우의 DataInputPage에서)
                    start_date, end_date = self.main_window.data_input_page.date_selector.get_date_range()
                    
                    # 한 번에 데이터 설정 (자동으로 이전 계획 감지 및 로드)
                    self.plan_maintenance_widget.set_data(data, start_date, end_date)
                    print("계획 유지율 위젯 데이터 업데이트 완료")

                # Capa 비율 분석
                # 두 번째 이벤트부터 정상 출력 (첫 번째 이벤트는 출력 안함)
                if self.data_changed_count > 1:
                    # 제조동별 생산량 비율 분석
                    self.capa_ratio_data = CapaRatioAnalyzer.analyze_capa_ratio(data_df=data, is_initial=False)
                else:
                    # 첫 번째 이벤트는 결과를 저장하지만 출력하지 않음
                    self.capa_ratio_data = CapaRatioAnalyzer.analyze_capa_ratio(data_df=data, is_initial=True)
                
                # 요일별 가동률 
                self.utilization_data = CapaUtilization.analyze_utilization(data)

                # 시각화 업데이트
                self.update_all_visualizations()
                    
            else:
                print("빈 데이터프레임")
                self.capa_ratio_data = {}
                self.utilization_data = {}

        except Exception as e:
            print(f"데이터 분석 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    """
    셀이 이동되었을 때 호출되는 메서드
    변경된 항목에 따라 시각화 업데이트
    """
    def on_cell_moved(self, item, old_data, new_data):
        # print(f"셀 이동 감지: {old_data.get('Item', '알 수 없음')} -> {new_data.get('Item', '알 수 없음')}")
        
        try:
            # 결과 데이터가 있을 때만 처리
            if self.result_data is not None and not self.result_data.empty:
                # 셀 이동에 따른 제조동별 생산량 비율 업데이트
                updated_ratio = CapaRatioAnalyzer.update_capa_ratio_for_cell_move(
                    self.result_data, old_data, new_data, is_initial=False  # 셀 이동 시 결과 표시
                )

                # 업데이트된 비율이 있는 경우
                if updated_ratio:
                    # 원본 데이터가 없는 경우 원본 데이터 저장
                    if not hasattr(self, 'original_capa_ratio') or self.original_capa_ratio is None:
                        self.original_capa_ratio = self.capa_ratio_data.copy() if isinstance(self.capa_ratio_data, dict) else {}
                    
                    # 비교 형식으로 데이터 구성
                    self.capa_ratio_data = {
                        'original': self.original_capa_ratio,
                        'adjusted': updated_ratio
                    }

                    # utilization 비교 데이터 처리
                    # 요일별 가동률 업데이트 : 불필요한 계산 막기 위해 capa가 업데이트 되면 시행
                    utilization_updated = CapaUtilization.update_utilization_for_cell_move(
                        self.result_data, old_data, new_data
                    )
                    
                    print(f"가동률 업데이트: {utilization_updated}")

                    if utilization_updated:
                        # 원본 데이터 저장(처음 수정 시)
                        if not hasattr(self, 'original_utilization') or self.original_utilization is None:
                            self.original_utilization = self.utilization_data.copy() if isinstance(self.utilization_data, dict) else {}

                        # 비교 형식으로 데이터 구성
                        self.utilization_data = {
                            'original' : self.original_utilization,
                            'adjusted': utilization_updated
                        }

                        print(f"비교 데이터 구성: {self.utilization_data}")

                    # 시각화 업데이트
                    self.update_all_visualizations()

                    # print(f"업데이트된 분석 결과: {self.capa_ratio_data}")

                    # Plan 탭의 계획 유지율 위젯 업데이트
                    if hasattr(self, 'plan_maintenance_widget'):
                        # 필요한 데이터 추출
                        line = new_data.get('Line')
                        time = new_data.get('Time')
                        item = new_data.get('Item')
                        qty = new_data.get('Qty')
                        demand = new_data.get('Demand', None)
                        
                        # 값이 있으면 수량 업데이트
                        if line and time is not None and item and qty is not None:
                            self.plan_maintenance_widget.update_quantity(line, time, item, qty, demand)
        
        except Exception as e:
            print(f"셀 이동 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    """모든 시각화 차트 업데이트"""
    def update_all_visualizations(self):
        print(f"시각화 업데이트 시작 - 캔버스 개수: {len(self.viz_canvases)}")

        # 캔버스 초기화
        if not self.viz_canvases:
            print("캔버스가 초기화되지 않음. 초기화 실행...")
            self.init_visualization_canvases()
        
        # 데이터 로그
        print(f"Capa 비율 데이터: {self.capa_ratio_data}")
        print(f"가동률 데이터: {self.utilization_data}")

        for i, canvas in enumerate(self.viz_canvases):
            viz_type = ["Capa", "Utilization", "PortCapa", "Plan"][i]
            print(f"  - 캔버스 {i}: {viz_type}, 유효함: {canvas is not None}")
            self.update_visualization(canvas, viz_type)

        print("시각화 업데이트 완료")
    
    """개별 시각화 차트 업데이트"""
    def update_visualization(self, canvas, viz_type):
        if viz_type == "Capa":
            VisualizationUpdater.update_capa_chart(canvas, self.capa_ratio_data)
        elif viz_type == "Utilization":
            VisualizationUpdater.update_utilization_chart(canvas, self.utilization_data)
        elif viz_type == "PortCapa":
            pass


    """최종 최적화 결과를 파일로 내보내는 메서드"""
    def export_results(self):
        try:
            # 데이터가 있는지 확인
            if hasattr(self, 'left_section') and hasattr(self.left_section,
                                                            'data') and self.left_section.data is not None:
                
                # 날짜 범위 가져오기
                start_date, end_date = self.main_window.data_input_page.date_selector.get_date_range()
                
                # 통합 내보내기 로직
                saved_path = ExportManager.export_data(
                    parent=self,
                    data_df=self.left_section.data,
                    start_date=start_date,
                    end_date=end_date,
                    is_planning=False
                )

                # 성공적으로 파일 저장 시 시그널 발생
                if saved_path:
                    self.export_requested.emit(saved_path)

            else:
                print("No data to export.")
                QMessageBox.warning(
                    self,
                    "Export Error",
                    "No data to export."
                )

        except Exception as e:
            print(f"Export 과정에서 오류 발생: {str(e)}")
            QMessageBox.critical(
            self, 
            "Export Error", 
            f"An error occurred during export:\n{str(e)}"
        )
