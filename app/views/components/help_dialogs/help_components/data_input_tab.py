# help_components/data_input_tab.py 수정 코드
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
        # 콘텐츠 프레임 생성
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #F9F9F9;
                border-radius: 10px;
                border: 1px solid #cccccc;
                margin: 10px;
            }
        """)

        # 콘텐츠 프레임 레이아웃 생성
        frame_layout = QVBoxLayout(self.content_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)

        # 제목 레이블 생성
        title_label = QLabel("Data Entry Guidelines")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            "color: #1428A0; border:none; padding-bottom: 10px; border-bottom: 2px solid #1428A0; background-color: transparent;")
        title_label.setMinimumHeight(40)

        # 설명 레이블
        desc_label = QLabel("This page provides instructions for entering and managing data in the system.")
        desc_label.setWordWrap(True)
        desc_font = QFont("Arial", 11)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("margin-bottom: 15px; background-color: transparent; border:none;")

        # 섹션들을 담을 프레임
        sections_frame = QFrame()
        sections_frame.setStyleSheet("background-color: transparent; border:none;")
        sections_layout = QVBoxLayout(sections_frame)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(15)  # 섹션간 간격

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
            title="Upload File",
            description="Click the 'Browse' button to upload the required Excel file.",
            image_path="app/resources/help_images/browse_btn.png"
        )

        # 섹션 2에 리스트 아이템 추가
        section2.add_list_item("master_*.xlsx ")
        section2.add_list_item("demand_*.xlsx ")
        section2.add_list_item("dynamic_*.xlsx ")

        # 섹션 3 - 파일 내용 확인
        section3 = HelpSectionComponent(
            number=3,
            title="Verify File Contents",
            description="Select a file or sheet from the file explorer on the left to review its contents. Data can be edited as needed.",
            image_path="app/resources/help_images/data_content.png"
        )

        # 섹션 4 - 파라미터 설정
        section4 = HelpSectionComponent(
            number=4,
            title="Parameter Settings",
            description="Adjust optimization settings in the parameter section at the bottom."
        )

        # 섹션 5 - 실행
        section5 = HelpSectionComponent(
            number=5,
            title="Run",
            description="Initiate the optimization process by clicking the 'Run' button.",
            image_path="app/resources/help_images/run_btn.png"
        )

        # 섹션 프레임에 모든 섹션 추가
        sections_layout.addWidget(section1)
        sections_layout.addWidget(section2)
        sections_layout.addWidget(section3)
        sections_layout.addWidget(section4)
        sections_layout.addWidget(section5)

        # 메모 레이블
        note_label = QLabel("Ensure all required files are uploaded before starting the optimization process.")
        note_label.setStyleSheet(
            "font-style: italic; color: #666; margin-top: 20px; background-color: transparent; border:none;")

        # 프레임 레이아웃에 위젯 추가
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(desc_label)
        frame_layout.addWidget(sections_frame)
        frame_layout.addWidget(note_label)
        frame_layout.addStretch(1)  # 하단 여백용 스트레치 추가

        # 메인 레이아웃에 콘텐츠 프레임 추가
        self.content_layout.addWidget(self.content_frame)