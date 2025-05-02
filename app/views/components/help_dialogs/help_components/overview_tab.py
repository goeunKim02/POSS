# help_components/overview_tab.py - 개요 탭 컴포넌트
from .base_tab import BaseTabComponent


class OverviewTabComponent(BaseTabComponent):
    """개요 탭 컴포넌트"""

    def __init__(self, parent=None, css_path="app/resources/styles/help_styles/help_style.css"):
        super().__init__(parent, css_path)
        self.init_content()

    def init_content(self):
        """콘텐츠 초기화"""
        self.set_content("""
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