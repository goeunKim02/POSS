# help_components/planning_tab.py - 계획 수립 탭 컴포넌트
from .base_tab import BaseTabComponent


class PlanningTabComponent(BaseTabComponent):
    """계획 수립 탭 컴포넌트"""

    def __init__(self, parent=None, css_path="app/resources/styles/help_styles/help_style.css"):
        super().__init__(parent, css_path)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        self.set_content("""
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