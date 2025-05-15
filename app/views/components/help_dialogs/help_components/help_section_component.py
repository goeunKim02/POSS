from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


"""
도움말 섹션 컴포넌트 - 제목, 설명, 이미지를 포함할 수 있는 섹션
"""
class HelpSectionComponent(QFrame):

    """
    도움말 섹션 초기화

    Args:
        number (int): 섹션 번호
        title (str): 섹션 제목
        description (str): 섹션 설명
        image_path (str, optional): 이미지 경로
        parent (QWidget, optional): 부모 위젯
    """
    def __init__(self, number, title, description, image_path=None, parent=None):
        super().__init__(parent)
        
        self.number = number
        self.title = title
        self.description = description
        self.image_path = image_path

        # 고정된 이미지 크기 설정
        self.IMAGE_WIDTH = 600
        self.IMAGE_HEIGHT = 400

        self.init_ui()

    """
    UI 초기화
    """
    def init_ui(self):
        # 기본 스타일 설정
        self.setStyleSheet(
            "background-color: white; border:none; border-left: 4px solid #1428A0; padding: 5px; border-radius: 0 5px 5px 0;")

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 텍스트 위젯
        self.text_widget = QWidget()
        self.text_widget.setStyleSheet("border: none; background-color: transparent;")
        text_layout = QVBoxLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        # 제목 레이블
        title_text = f"{self.number}. {self.title}" if self.number else self.title
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: #1428A0; border:none; margin-bottom: 0px;")
        title_label.setAlignment(Qt.AlignBottom)

        # 설명 컨테이너
        desc_container = QWidget()
        desc_container.setStyleSheet("border: none;")
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(20, -10, 20, 0)
        desc_layout.setSpacing(0)

        # 설명 레이블
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Arial", 9, QFont.Bold))
        desc_label.setStyleSheet("border:none;")
        desc_label.setAlignment(Qt.AlignTop)

        desc_layout.addWidget(desc_label)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_container)

        main_layout.addWidget(self.text_widget)

        # 이미지 레이블
        if self.image_path:
            # 이미지 컨테이너
            image_container = QWidget()
            image_container.setStyleSheet("""
                background-color: transparent;
                border: none;
            """)

            # 이미지 컨테이너 레이아웃
            image_container_layout = QVBoxLayout(image_container)
            image_container_layout.setContentsMargins(0, 0, 0, 0)
            image_container_layout.setAlignment(Qt.AlignCenter)

            # 이미지 레이블
            self.image_label = QLabel()
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("background-color: transparent; border:none;")

            # 이미지 로드
            pixmap = QPixmap(self.image_path)

            if not pixmap.isNull():
                # 이미지 크기 조정
                pixmap = pixmap.scaled(
                    self.IMAGE_WIDTH,
                    self.IMAGE_HEIGHT,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("이미지를 찾을 수 없습니다")
                self.image_label.setStyleSheet("color: red;")

            image_container_layout.addWidget(self.image_label)

            main_layout.addWidget(image_container)

        main_layout.addStretch(1)

    """
    섹션에 리스트 아이템 추가

    Args:
        item_text (str): 리스트 아이템 텍스트
    """
    def add_list_item(self, item_text):
        layout = self.text_widget.layout()

        list_container = None

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()

            if isinstance(widget, QWidget) and widget.objectName() == "list_container":
                list_container = widget
                break

        if not list_container:
            list_container = QWidget()
            list_container.setObjectName("list_container")
            list_container.setStyleSheet("border: none; background-color: transparent; font-family: Arial;")

            list_layout = QVBoxLayout(list_container)
            list_layout.setContentsMargins(20, 5, 5, 5)
            list_layout.setSpacing(5)

            layout.addWidget(list_container)
        else:
            list_layout = list_container.layout()

        # 리스트 아이템 레이블
        item_label = QLabel(f"• {item_text}")
        item_label.setWordWrap(True)
        item_label.setStyleSheet("font-size: 15px; border: none; font-family: Arial;")
        list_layout.addWidget(item_label)