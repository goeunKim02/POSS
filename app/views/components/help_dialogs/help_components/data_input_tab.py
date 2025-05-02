# help_components/data_input_tab.py - 데이터 입력 탭 컴포넌트
from .base_tab import BaseTabComponent


class DataInputTabComponent(BaseTabComponent):
    """데이터 입력 탭 컴포넌트"""

    def __init__(self, parent=None, css_path="app/resources/styles/help_styles/help_style.css"):
        super().__init__(parent, css_path)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        self.set_content("""
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