from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class KpiWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.init_ui()
        self.base_scores = {}
        self.adjust_scores = {}

    """
    KPI 위젯 UI 초기화"""
    def init_ui(self):
        # 메인 레이아웃
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # 헤더 행 추가
        headers = ["", "Total", "Mat.", "SOP", "Util."]
        for j, header in enumerate(headers):
            label = QLabel(header)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.layout.addWidget(label, 0, j)
        
        # Base/Adjust 행 추가
        rows = ["Base", "Adjust"]
        for i, row_name in enumerate(rows):
            row_label = QLabel(row_name)
            row_label.setFont(QFont("Arial", 10, QFont.Bold))
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.layout.addWidget(row_label, i+1, 0)
            
        # KPI 라벨 초기화
        self.kpi_labels = {}
        
        # 각 행의 점수 라벨들 생성
        for i, row_name in enumerate(rows):
            for j, col_name in enumerate(["Total", "Mat", "SOP", "Util"]):
                score_label = QLabel("--")
                score_label.setFont(QFont("Arial", 10, QFont.Bold))
                score_label.setAlignment(Qt.AlignCenter)
                score_label.setStyleSheet("color: #555; border: none; padding: 5px;")
                self.layout.addWidget(score_label, i+1, j+1)
                
                # 라벨을 참조할 수 있도록 저장
                self.kpi_labels[f"{row_name}_{col_name}"] = score_label


    """
    점수 업데이트
    """
    def update_scores(self, base_scores=None, adjust_scores=None):
        print(f"3. update_scores 호출됨: base_scores={base_scores}, adjust_scores={adjust_scores}")
        # 기본 점수
        if base_scores:
            self.base_scores = base_scores
            self.update_base_scores()

        # 조정 점수
        if adjust_scores:
            self.adjust_scores = adjust_scores
            self.update_adjust_scores()
        elif adjust_scores == {}:  # 없다면 점수 초기화
            self.adjust_scores = {}
            self.reset_adjust_scores()

    """
    기본 점수 라벨 업데이트
    """
    def update_base_scores(self):
        print(f"4. kpi_labels 키: {list(self.kpi_labels.keys())}")
        for score_type, score in self.base_scores.items():
            label_key = f"Base_{score_type}"
            if label_key in self.kpi_labels:
                # 소수점 한자리까지 표시
                score_text = f"{score:.1f}" if isinstance(score, (int, float)) else str(score)
                self.kpi_labels[label_key].setText(score_text)
                self.kpi_labels[label_key].setStyleSheet(f"""
                    QLabel {{
                        color: #333;
                        font-weight: bold;
                        border: none;
                        padding: 5px;
                    }}
                """)

    """
    조정 점수 라벨 업데이트
    """
    def update_adjust_scores(self):
        for score_type, adjust_score in self.adjust_scores.items():
            label_key = f"Adjust_{score_type}"
            if label_key in self.kpi_labels:
                # 기본 점수 참조
                base_score = self.base_scores.get(score_type, 0)

                # 점수 차이에 따라 스타일 변경
                if adjust_score > base_score:
                    color = "#1428A0"  # 파란색 (향상)
                    arrow = "↑"
                elif adjust_score < base_score:
                    color = "#FF0000"  # 빨간색 (하락)
                    arrow = "↓"
                else:
                    color = "#888888"  # 회색 (변화 없음)
                    arrow = "-"

                # 소수점 한자리까지 표시
                score_text = f"{adjust_score:.1f}" if isinstance(adjust_score, (int, float)) else str(adjust_score)
                self.kpi_labels[label_key].setText(f"{score_text} {arrow}")
                self.kpi_labels[label_key].setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-weight: bold;
                        font-size: 10pt;
                        border: none;
                        padding: 5px;
                    }}
                """)


    """
    조정 점수 리셋
    """
    def reset_adjust_scores(self):
        for score_type in ['Total', 'Mat', 'SOP', 'Util']:
            label_key = f"Adjust_{score_type}"
            if label_key in self.kpi_labels:
                    self.kpi_labels[label_key].setText("--")
                    self.kpi_labels[label_key].setStyleSheet("""
                        QLabel {
                            color: #555;
                            font-weight: bold;
                            font-size: 10pt;
                            border: none;
                            padding: 5px;
                        }
                    """)