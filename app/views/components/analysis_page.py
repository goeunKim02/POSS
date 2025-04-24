from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QFont
from ..components.resultPage.modified_left_section import ModifiedLeftSection


class AnalysisPage(QWidget):
    # 시그널 추가
    export_requested = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
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
        font.setPointSize(20)
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

        # 메인 콘텐츠 레이아웃
        result_container = QHBoxLayout()
        result_container.setContentsMargins(25, 25, 25, 25)
        result_container.setSpacing(20)

        # 왼쪽 조정 결과 컨테이너
        adjust_frame = QFrame()
        adjust_frame.setFrameShape(QFrame.StyledPanel)
        adjust_frame.setStyleSheet("background-color: white; border-radius: 5px; border: 2px solid #D9D9D9;")

        adjust_result_container = QVBoxLayout(adjust_frame)
        adjust_result_container.setContentsMargins(10, 10, 10, 10)

        # 드래그 가능한 테이블 위젯 추가
        self.left_section = ModifiedLeftSection()
        adjust_result_container.addWidget(self.left_section)

        # 데이터 변경 시그널 연결 (필요한 경우)
        self.left_section.data_changed.connect(self.on_data_changed)

        # 오른쪽 통계 결과 컨테이너
        statis_frame = QFrame()
        statis_frame.setFrameShape(QFrame.StyledPanel)
        statis_frame.setStyleSheet("background-color: white; border-radius: 5px; border: 2px solid #D9D9D9;")

        statis_result_container = QVBoxLayout(statis_frame)
        statis_result_container.setContentsMargins(10, 10, 10, 10)

        # 통계 정보 표시를 위한 레이블 추가
        self.stats_label = QLabel("통계 정보가 여기에 표시됩니다.")
        self.stats_label.setAlignment(Qt.AlignCenter)
        statis_result_container.addWidget(self.stats_label)

        # 프레임을 주 레이아웃에 추가
        result_container.addWidget(adjust_frame, 7)
        result_container.addWidget(statis_frame, 3)

        result_layout.addLayout(result_container)

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

    def on_data_changed(self, data):
        """테이블 데이터가 변경되었을 때 호출되는 메서드"""
        # 통계 정보 업데이트
        try:
            # 기본 통계 계산 (pandas DataFrame 가정)
            if data is not None and not data.empty:
                numeric_data = data.select_dtypes(include=['number'])
                if not numeric_data.empty:
                    stats_text = "<h3>기본 통계 정보</h3>"
                    stats_text += "<table border='1' cellpadding='5'>"

                    # 열 이름 헤더
                    stats_text += "<tr><th>통계량</th>"
                    for col in numeric_data.columns:
                        stats_text += f"<th>{col}</th>"
                    stats_text += "</tr>"

                    # 평균
                    stats_text += "<tr><td>평균</td>"
                    for col in numeric_data.columns:
                        stats_text += f"<td>{numeric_data[col].mean():.2f}</td>"
                    stats_text += "</tr>"

                    # 중앙값
                    stats_text += "<tr><td>중앙값</td>"
                    for col in numeric_data.columns:
                        stats_text += f"<td>{numeric_data[col].median():.2f}</td>"
                    stats_text += "</tr>"

                    # 최대값
                    stats_text += "<tr><td>최대값</td>"
                    for col in numeric_data.columns:
                        stats_text += f"<td>{numeric_data[col].max():.2f}</td>"
                    stats_text += "</tr>"

                    # 최소값
                    stats_text += "<tr><td>최소값</td>"
                    for col in numeric_data.columns:
                        stats_text += f"<td>{numeric_data[col].min():.2f}</td>"
                    stats_text += "</tr>"

                    # 표준편차
                    stats_text += "<tr><td>표준편차</td>"
                    for col in numeric_data.columns:
                        stats_text += f"<td>{numeric_data[col].std():.2f}</td>"
                    stats_text += "</tr>"

                    stats_text += "</table>"

                    self.stats_label.setText(stats_text)
                    self.stats_label.setTextFormat(Qt.RichText)
                else:
                    self.stats_label.setText("수치형 데이터가 없습니다.")
            else:
                self.stats_label.setText("데이터가 없습니다.")
        except Exception as e:
            self.stats_label.setText(f"통계 계산 오류: {str(e)}")
            print(f"통계 계산 오류: {e}")