# help_components/result_tab.py - 결과 분석 탭 컴포넌트
from .base_tab import BaseTabComponent


class ResultTabComponent(BaseTabComponent):
    """결과 분석 탭 컴포넌트"""

    def __init__(self, parent=None, css_path="app/resources/styles/help_styles/help_style.css"):
        super().__init__(parent, css_path)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        self.set_content("""
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