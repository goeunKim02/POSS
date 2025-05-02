# help_components/base_tab.py - 기본 탭 컴포넌트
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import QFile, QTextStream


class BaseTabComponent(QWidget):
    """도움말 탭의 기본 클래스"""

    def __init__(self, parent=None, css_path="app/resources/styles/help_styles/help_style.css"):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        # CSS 로드 및 적용
        self.style_sheet = self.load_css_file(css_path)
        self.text_browser.document().setDefaultStyleSheet(self.style_sheet)

        self.layout.addWidget(self.text_browser)

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

    def set_content(self, html_content):
        """HTML 콘텐츠 설정"""
        self.text_browser.setHtml(html_content)