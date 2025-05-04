# help_components/data_input_tab.py - 수정된 데이터 입력 탭 컴포넌트
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent


class DataInputTabComponent(BaseTabComponent):
    """데이터 입력 탭 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 제목 레이블 생성
        title_label = QLabel("데이터 입력 사용법")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; padding-bottom: 10px; border-bottom: 2px solid #1428A0;")
        title_label.setMinimumHeight(40)

        # 1. 날짜 범위 선택 섹션
        section1_frame = QFrame()
        section1_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        section1_layout = QVBoxLayout(section1_frame)

        section1_title = QLabel("1. 날짜 범위 선택")
        section1_title.setFont(QFont("Arial", 10, QFont.Bold))
        section1_title.setStyleSheet("color: #1428A0;")

        section1_desc = QLabel("좌측 상단의 날짜 선택기를 사용하여 계획 기간을 설정합니다.")
        section1_desc.setWordWrap(True)
        section1_desc.setStyleSheet("font-size: 15px;")

        section1_layout.addWidget(section1_title)
        section1_layout.addWidget(section1_desc)

        # 2. 파일 업로드 섹션
        section2_frame = QFrame()
        section2_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        section2_layout = QVBoxLayout(section2_frame)

        section2_title = QLabel("2. 파일 업로드")
        section2_title.setFont(QFont("Arial", 10, QFont.Bold))
        section2_title.setStyleSheet("color: #1428A0;")

        section2_desc = QLabel("'Browse' 버튼을 클릭하여 필요한 엑셀 파일을 업로드합니다.")
        section2_desc.setWordWrap(True)
        section2_desc.setStyleSheet("font-size: 15px;")

        section2_format = QLabel("지원되는 파일 형식:")
        section2_format.setStyleSheet("font-size: 15px; margin-top: 5px;")

        # 파일 형식 목록
        formats_frame = QFrame()
        formats_layout = QVBoxLayout(formats_frame)
        formats_layout.setContentsMargins(20, 0, 0, 0)
        formats_layout.setSpacing(5)

        formats = [
            "master_*.xlsx - 마스터 데이터",
            "demand_*.xlsx - 수요 데이터",
            "dynamic_*.xlsx - 동적 데이터"
        ]

        for fmt in formats:
            fmt_label = QLabel("• " + fmt)
            fmt_label.setStyleSheet("font-size: 15px;")
            formats_layout.addWidget(fmt_label)

        section2_layout.addWidget(section2_title)
        section2_layout.addWidget(section2_desc)
        section2_layout.addWidget(section2_format)
        section2_layout.addWidget(formats_frame)

        # 3. 파일 내용 확인 섹션
        section3_frame = QFrame()
        section3_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        section3_layout = QVBoxLayout(section3_frame)

        section3_title = QLabel("3. 파일 내용 확인")
        section3_title.setFont(QFont("Arial", 10, QFont.Bold))
        section3_title.setStyleSheet("color: #1428A0;")

        section3_desc = QLabel("왼쪽 파일 탐색기에서 파일이나 시트를 클릭하여 내용을 확인합니다.\n필요한 경우 데이터를 편집할 수 있습니다.")
        section3_desc.setWordWrap(True)
        section3_desc.setStyleSheet("font-size: 15px;")

        section3_layout.addWidget(section3_title)
        section3_layout.addWidget(section3_desc)

        # 4. 파라미터 설정 섹션
        section4_frame = QFrame()
        section4_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        section4_layout = QVBoxLayout(section4_frame)

        section4_title = QLabel("4. 파라미터 설정")
        section4_title.setFont(QFont("Arial", 10, QFont.Bold))
        section4_title.setStyleSheet("color: #1428A0;")

        section4_desc = QLabel("하단 파라미터 섹션에서 최적화를 위한 설정을 조정합니다.")
        section4_desc.setWordWrap(True)
        section4_desc.setStyleSheet("font-size: 15px;")

        section4_layout.addWidget(section4_title)
        section4_layout.addWidget(section4_desc)

        # 5. 실행 섹션
        section5_frame = QFrame()
        section5_frame.setStyleSheet(
            "background-color: #f0f5ff; border-left: 4px solid #1428A0; border-radius: 0 5px 5px 0; padding: 10px;")
        section5_layout = QVBoxLayout(section5_frame)

        section5_title = QLabel("5. 실행")
        section5_title.setFont(QFont("Arial", 10, QFont.Bold))
        section5_title.setStyleSheet("color: #1428A0;")

        section5_desc = QLabel("'Run' 버튼을 클릭하여 최적화 프로세스를 시작합니다.")
        section5_desc.setWordWrap(True)
        section5_desc.setStyleSheet("font-size: 15px;")

        section5_layout.addWidget(section5_title)
        section5_layout.addWidget(section5_desc)

        # 메인 레이아웃에 위젯 추가
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(section1_frame)
        self.content_layout.addWidget(section2_frame)
        self.content_layout.addWidget(section3_frame)
        self.content_layout.addWidget(section4_frame)
        self.content_layout.addWidget(section5_frame)
        self.content_layout.addStretch(1)  # 하단 여백용 스트레치 추가