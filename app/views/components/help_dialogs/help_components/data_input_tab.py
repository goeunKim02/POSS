# help_components/data_input_tab.py 수정 예시
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .base_tab import BaseTabComponent
from .help_section_component import HelpSectionComponent  # 새 컴포넌트 import


class DataInputTabComponent(BaseTabComponent):
    """데이터 입력 탭 컴포넌트"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        # 제목 레이블 생성
        title_label = QLabel("Data Entry Guidelines")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1428A0; padding-bottom: 10px; border-bottom: 2px solid #1428A0;")
        title_label.setMinimumHeight(40)

        # 섹션 1 - 날짜 범위 선택
        section1 = HelpSectionComponent(
            number=1,
            title="Date Range Selection",
            description="The planning period can be set using the date selector located in the top-left corner.",
            image_path="app/resources/help_images/select_date.png"
        )

        # 섹션 2 - 파일 업로드
        section2 = HelpSectionComponent(
            number=2,
            title="파일 업로드",
            description="'Browse' 버튼을 클릭하여 필요한 엑셀 파일을 업로드합니다."
        )

        # 섹션 2에 리스트 아이템 추가
        section2.add_list_item("master_*.xlsx - 마스터 데이터")
        section2.add_list_item("demand_*.xlsx - 수요 데이터")
        section2.add_list_item("dynamic_*.xlsx - 동적 데이터")

        # 섹션 3 - 파일 내용 확인
        section3 = HelpSectionComponent(
            number=3,
            title="파일 내용 확인",
            description="왼쪽 파일 탐색기에서 파일이나 시트를 클릭하여 내용을 확인합니다. 필요한 경우 데이터를 편집할 수 있습니다."
        )

        # 섹션 4 - 파라미터 설정
        section4 = HelpSectionComponent(
            number=4,
            title="파라미터 설정",
            description="하단 파라미터 섹션에서 최적화를 위한 설정을 조정합니다."
        )

        # 섹션 5 - 실행
        section5 = HelpSectionComponent(
            number=5,
            title="실행",
            description="'Run' 버튼을 클릭하여 최적화 프로세스를 시작합니다."
        )

        # 메인 레이아웃에 위젯 추가
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(section1)
        self.content_layout.addWidget(section2)
        self.content_layout.addWidget(section3)
        self.content_layout.addWidget(section4)
        self.content_layout.addWidget(section5)
        self.content_layout.addStretch(1)  # 하단 여백용 스트레치 추가