from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QFrame, QSplitter, QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QFont
from ..components.result_components.modified_left_section import ModifiedLeftSection
from ..components.visualization.mpl_canvas import MplCanvas
from ..components.visualization.visualizaiton_manager import VisualizationManager
from app.analysis.output.daily_capa_utilization import analyze_utilization

class ResultPage(QWidget):
    # 시그널 추가
    export_requested = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.utilization_data = None 
        self.init_ui()

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
        left_layout.addWidget(self.left_section)

        # 오른쪽 컨테이너 (현재는 비어있음)
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 2px solid #cccccc;")

        right_layout = QVBoxLayout(right_frame)
        # right_layout.setContentsMargins(0, 0, 0, 0)

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

    def export_results(self):
        """결과를 CSV 파일로 내보내기"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "결과 내보내기", "", "CSV 파일 (*.csv);;모든 파일 (*)"
            )

            if file_path:
                # 데이터가 있는지 확인
                if hasattr(self, 'left_section') and hasattr(self.left_section,
                                                             'data') and self.left_section.data is not None:
                    try:
                        # 데이터를 CSV로 저장
                        self.left_section.data.to_csv(file_path, index=False)
                        print(f"데이터가 {file_path}에 저장되었습니다.")
                    except Exception as e:
                        print(f"파일 저장 오류: {e}")
                else:
                    print("내보낼 데이터가 없습니다.")

                # 시그널 발생
                self.export_requested.emit(file_path)
        except Exception as e:
            print(f"Export 과정에서 오류 발생: {str(e)}")

    def switch_viz_page(self, index):
        """시각화 페이지 전환 및 버튼 스타일 업데이트"""
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

    def create_initial_visualization(self, canvas, viz_type):
        """각 지표별 초기 시각화 생성"""
        canvas.axes.clear()

        # 각 지표 예시
        if viz_type == "Capa":
            data = {'I': 71.46, 'K': 11.72, 'M': 16.83}
            VisualizationManager.create_chart(
                data,
                chart_type='bar',
                title='Plant Capacity Ratio',
                xlabel='Plant',
                ylabel='Ratio (%)',
                ax=canvas.axes
            )

        elif viz_type == "Utilization":
            if self.utilization_data is None:
                try:
                    result_file = "app/analysis/output/ssafy_result_0408.xlsx"
                    master_file = "app/analysis/output/ssafy_master_0408.xlsx"

                    self.utilization_data = analyze_utilization(result_file, master_file)

                    print("Finished Utilization Rate :", self.utilization_data)
                except Exception as e:
                    print(f"Utilization Rate Error : {str(e)}")
                    self.utilization_data = {}
        
            if self.utilization_data:
                days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                sorted_data = {day: self.utilization_data.get(day, 0) for day in days_order}

                VisualizationManager.create_chart(
                    sorted_data,
                    chart_type='bar',
                    title='Daily Utilization Rate',
                    xlabel='Day of week',
                    ylabel='Utilization Rate(%)',
                    ax=canvas.axes,
                    ylim=(0, 100),
                    threshold_values=[60, 80],
                    threshold_colors=['#4CAF50', '#FFC107', '#F44336'],
                    value_fontsize=14
                )

            else:
                canvas.axes.text(0.5, 0.5, 'No utilization data available', ha='center', va='center', fontsize=18)

        # 각 지표 추가

        canvas.draw()