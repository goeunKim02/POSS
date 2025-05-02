from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTabWidget, QWidget, QTextBrowser, QScrollArea)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QFile, QTextStream


class HelpDialog(QDialog):
    """도움말 다이얼로그 창"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Samsung Production Planning Optimization System")
        self.resize(800, 600)  # 적절한 크기로 설정
        # 아이콘 설정 (있을 경우)
        # self.setWindowIcon(QIcon('../resources/icon/help_icon.png'))
        self.init_ui()

    def load_css_file(self, path):
        """CSS 파일 로드"""
        css_content = ""
        css_file = QFile(path)
        if css_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(css_file)
            css_content = stream.readAll()
            css_file.close()
        else:
            print(f"CSS 파일을 열 수 없습니다: {path}")
        return css_content

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        # 제목 레이블
        title_label = QLabel("Help Guide")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # CSS 파일 로드
        self.style_sheet = self.load_css_file("app/resources/styles/help_style.css")

        # 탭 위젯 생성
        tab_widget = QTabWidget()
        # 각 탭 페이지 생성
        overview_tab = self.create_overview_tab()
        data_input_tab = self.create_data_input_tab()
        planning_tab = self.create_planning_tab()
        result_tab = self.create_result_tab()
        # 탭 추가
        tab_widget.addTab(overview_tab, "개요")
        tab_widget.addTab(data_input_tab, "데이터 입력")
        tab_widget.addTab(planning_tab, "계획 수립")
        tab_widget.addTab(result_tab, "결과 분석")
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)  # 다이얼로그 닫기
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)
        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(title_label)
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)

    def create_overview_tab(self):
        """개요 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)  # 외부 링크 열기 허용

        # CSS 적용
        text_browser.document().setDefaultStyleSheet(self.style_sheet)

        # HTML 형식으로 내용 추가 (CSS 클래스 사용)
        text_browser.setHtml("""
        <h2 class="title">Samsung Production Planning Optimization System</h2>
        <p class="description">이 시스템은 삼성전자의 생산 계획을 최적화하기 위한 도구입니다.</p>
        <p class="subtitle">주요 기능:</p>
        <ul class="feature-list">
            <li>생산 데이터 분석</li>
            <li>최적 생산 계획 수립</li>
            <li>리소스 할당 최적화</li>
            <li>결과 시각화 및 분석</li>
        </ul>
        <p class="note">자세한 내용은 각 탭을 참조하세요.</p>
        """)

        layout.addWidget(text_browser)
        return tab

    def create_data_input_tab(self):
        """데이터 입력 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)

        # CSS 적용
        text_browser.document().setDefaultStyleSheet(self.style_sheet)

        # HTML 형식으로 내용 추가
        text_browser.setHtml("""
        <h2 class="title">데이터 입력 사용법</h2>
        <div class="box">
            <h3 class="subtitle">1. 날짜 범위 선택</h3>
            <p class="description">좌측 상단의 날짜 선택기를 사용하여 계획 기간을 설정합니다.</p>
        </div>

        <div class="box">
            <h3 class="subtitle">2. 파일 업로드</h3>
            <p class="description">'Browse' 버튼을 클릭하여 필요한 엑셀 파일을 업로드합니다.</p>
            <p class="description">지원되는 파일 형식:</p>
            <ul class="feature-list">
                <li>master_*.xlsx - 마스터 데이터</li>
                <li>demand_*.xlsx - 수요 데이터</li>
                <li>dynamic_*.xlsx - 동적 데이터</li>
            </ul>
        </div>

        <div class="box">
            <h3 class="subtitle">3. 파일 내용 확인</h3>
            <p class="description">왼쪽 파일 탐색기에서 파일이나 시트를 클릭하여 내용을 확인합니다.</p>
            <p class="description">필요한 경우 데이터를 편집할 수 있습니다.</p>
        </div>

        <div class="box">
            <h3 class="subtitle">4. 파라미터 설정</h3>
            <p class="description">하단 파라미터 섹션에서 최적화를 위한 설정을 조정합니다.</p>
        </div>

        <div class="box">
            <h3 class="subtitle">5. 실행</h3>
            <p class="description">'Run' 버튼을 클릭하여 최적화 프로세스를 시작합니다.</p>
        </div>
        """)

        layout.addWidget(text_browser)
        return tab

    def create_planning_tab(self):
        """계획 수립 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)

        # CSS 적용
        text_browser.document().setDefaultStyleSheet(self.style_sheet)

        text_browser.setHtml("""
        <h2 class="title">사전 할당 결과 사용법</h2>
        <p class="description">이 페이지에서는 초기 계획 결과를 확인하고 조정할 수 있습니다.</p>

        <h3 class="subtitle">기능:</h3>
        <ul class="feature-list">
            <li><span class="highlight">결과 확인</span>: 테이블에서 사전 할당된 작업들을 확인합니다.</li>
            <li><span class="highlight">필터링</span>: 헤더를 클릭하여 특정 조건으로 데이터를 필터링합니다.</li>
            <li><span class="highlight">정렬</span>: 헤더를 클릭하여 오름차순/내림차순 정렬을 적용합니다.</li>
            <li><span class="highlight">내보내기</span>: 'Export Excel' 버튼을 클릭하여 결과를 엑셀 파일로 저장합니다.</li>
            <li><span class="highlight">초기화</span>: 'Reset' 버튼을 클릭하여 변경 사항을 초기화합니다.</li>
        </ul>

        <div class="box">
            <h3 class="subtitle">팁:</h3>
            <p class="description">최적의 결과를 얻기 위해 데이터 입력 단계에서 정확한 정보를 제공하는 것이 중요합니다.</p>
        </div>
        """)

        layout.addWidget(text_browser)
        return tab

    def create_result_tab(self):
        """결과 분석 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)

        # CSS 적용
        text_browser.document().setDefaultStyleSheet(self.style_sheet)

        text_browser.setHtml("""
        <h2 class="title">결과 분석 사용법</h2>
        <p class="description">이 페이지에서는 최적화 결과를 분석하고 시각화할 수 있습니다.</p>

        <h3 class="subtitle">주요 기능:</h3>
        <ul class="feature-list">
            <li><span class="highlight">결과 테이블</span>: 왼쪽 패널에서 상세 결과를 확인합니다.</li>
            <li><span class="highlight">시각화</span>: 오른쪽 패널에서 다양한 그래프를 통해 결과를 시각적으로 확인합니다.</li>
            <li><span class="highlight">데이터 내보내기</span>: 'Export' 버튼을 클릭하여 결과를 CSV 파일로 저장합니다.</li>
            <li><span class="highlight">보고서 생성</span>: 'Report' 버튼을 클릭하여 보고서를 생성합니다.</li>
        </ul>

        <div class="box">
            <h3 class="subtitle">시각화 유형:</h3>
            <div class="buttons-container">
                <span class="button">Capa</span>
                <span class="button">Utilization</span>
                <span class="button">PortCapa</span>
                <span class="button">Plan</span>
            </div>
            <p class="description">각 버튼을 클릭하여 해당 유형의 시각화를 확인할 수 있습니다.</p>
        </div>

        <p class="note">시각화 패널에서 각 버튼을 클릭하여 다른 유형의 데이터를 확인할 수 있습니다.</p>
        """)

        layout.addWidget(text_browser)
        return tab