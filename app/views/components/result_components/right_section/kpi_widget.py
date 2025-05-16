from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from app.analysis.output.kpi_score import KpiScore

class KpiWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.kpi_calculator = None
        self.scores_layout = None
        
        self.init_ui()

    def init_ui(self):
        """KPI 위젯 UI 초기화"""
        # 메인 프레임
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        # 레이아웃 구성
        main_layout = QVBoxLayout()
        frame_layout = QVBoxLayout()
        
        # 제목
        self.title_label = QLabel("KPI Score")
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16pt;
                color: #1428A0;
                text-align: center;
                margin-bottom: 15px;
                padding: 5px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.title_label)
        
        # 점수 표시 영역
        self.scores_widget = QWidget()
        self.scores_layout = QGridLayout()
        self.scores_widget.setLayout(self.scores_layout)
        frame_layout.addWidget(self.scores_widget)
        
        # 초기 빈 레이블들 생성
        self.create_empty_labels()
        
        frame.setLayout(frame_layout)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)
        
    def create_empty_labels(self):
        """초기 빈 레이블들 생성"""
        # Mat, SOP, Util 레이블 (첫 번째 행)
        self.mat_label = QLabel("Mat: --")
        self.sop_label = QLabel("SOP: --")
        self.util_label = QLabel("Util: --")
        
        # Total 레이블 (두 번째 행)
        self.total_label = QLabel("Total: --")
        
        # 스타일 적용
        for label in [self.mat_label, self.sop_label, self.util_label]:
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 12pt;
                    color: #666;
                    padding: 5px;
                    text-align: center;
                }
            """)
            label.setAlignment(Qt.AlignCenter)
        
        # Total 레이블은 더 크게
        self.total_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14pt;
                color: #666;
                padding: 10px;
                text-align: center;
                border-top: 1px solid #eee;
                margin-top: 10px;
            }
        """)
        self.total_label.setAlignment(Qt.AlignCenter)
        
        # 레이아웃에 추가
        self.scores_layout.addWidget(self.mat_label, 0, 0)
        self.scores_layout.addWidget(self.sop_label, 0, 1)
        self.scores_layout.addWidget(self.util_label, 0, 2)
        self.scores_layout.addWidget(self.total_label, 1, 0, 1, 3)

    
    """
    데이터 설정 및 KPI Calculator 초기화
    """
    def set_data(self, result_df, material_analyzer=None, demand_df=None):
        self.kpi_calculator = KpiScore(self.main_window)
        self.kpi_calculator.set_data(result_df, material_analyzer, demand_df)
        self.kpi_calculator.set_kpi_widget(self.scores_widget)

        # 초기 점수 계산
        self.refresh_scores()

    """
    점수 새로고침
    """
    def refresh_scores(self):
        if not self.kpi_calculator:
            return None

        scores = self.kpi_calculator.calculate_all_scores()
        self.update_labels(scores)
        return scores
    
    """
    라벨 업데이트
    """
    def update_labels(self, scores):
        if not scores:
            return
        
        # 점수에 따른 색상 결정
        def get_color(score):
            if score >= 90:
                return "#28a745"  # 초록색
            elif score >= 70:
                return "#ffc107"  # 노란색
            else:
                return "#dc3545"  # 빨간색
        
        # 각 라벨 업데이트
        mat_color = get_color(scores['Mat'])
        sop_color = get_color(scores['SOP'])
        util_color = get_color(scores['Util'])
        total_color = get_color(scores['Total'])
        
        self.mat_label.setText(f"Mat: {scores['Mat']:.1f}%")
        self.mat_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 12pt;
                color: {mat_color};
                padding: 5px;
                text-align: center;
            }}
        """)
        
        self.sop_label.setText(f"SOP: {scores['SOP']:.1f}%")
        self.sop_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 12pt;
                color: {sop_color};
                padding: 5px;
                text-align: center;
            }}
        """)
        
        self.util_label.setText(f"Util: {scores['Util']:.1f}%")
        self.util_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 12pt;
                color: {util_color};
                padding: 5px;
                text-align: center;
            }}
        """)
        
        self.total_label.setText(f"Total: {scores['Total']:.1f}%")
        self.total_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 14pt;
                color: {total_color};
                padding: 10px;
                text-align: center;
                border-top: 1px solid #eee;
                margin-top: 10px;
            }}
        """)

    """
    데이터 변경 시 호출
    """
    def on_data_changed(self):
        self.refresh_scores()
        
    """
    점수 초기화
    """
    def clear_scores(self):
        self.mat_label.setText("Mat: --")
        self.sop_label.setText("SOP: --")
        self.util_label.setText("Util: --")
        self.total_label.setText("Total: --")
        
        # 색상 초기화
        default_style = """
            QLabel {
                font-weight: bold;
                color: #666;
                padding: 5px;
                text-align: center;
            }
        """
        self.mat_label.setStyleSheet(default_style + "font-size: 12pt;")
        self.sop_label.setStyleSheet(default_style + "font-size: 12pt;")
        self.util_label.setStyleSheet(default_style + "font-size: 12pt;")
        self.total_label.setStyleSheet(default_style + "font-size: 14pt; border-top: 1px solid #eee; margin-top: 10px;")
    