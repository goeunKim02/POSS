# help_components/help_section_component.py
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


class HelpSectionComponent(QFrame):
    """도움말 섹션 컴포넌트 - 제목, 설명, 이미지를 포함할 수 있는 섹션"""

    def __init__(self, number, title, description, image_path=None, parent=None):
        """
        도움말 섹션 초기화

        Args:
            number (int): 섹션 번호
            title (str): 섹션 제목
            description (str): 섹션 설명
            image_path (str, optional): 이미지 경로
            parent (QWidget, optional): 부모 위젯
        """
        super().__init__(parent)
        self.number = number
        self.title = title
        self.description = description
        self.image_path = image_path
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        # 기본 스타일 설정
        self.setStyleSheet(
            "background-color: #f0f5ff; border:none; border-left: 4px solid #1428A0; padding: 5px; border-radius: 0 5px 5px 0;")

        # 레이아웃 생성
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 텍스트 위젯 생성
        self.text_widget = QWidget()
        self.text_widget.setStyleSheet("border: none; background-color: transparent;")
        text_layout = QVBoxLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        # 제목 레이블 생성
        title_text = f"{self.number}. {self.title}" if self.number else self.title
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: #1428A0; border:none; margin-bottom: 0px;")
        title_label.setAlignment(Qt.AlignBottom)

        # 설명 컨테이너 생성
        desc_container = QWidget()
        desc_container.setStyleSheet("border: none;")
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(20, -10, 20, 0)
        desc_layout.setSpacing(0)

        # 설명 레이블 생성
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Arial", 9, QFont.Bold))
        desc_label.setStyleSheet("border:none;")
        desc_label.setAlignment(Qt.AlignTop)

        # 설명 컨테이너에 설명 레이블 추가
        desc_layout.addWidget(desc_label)

        # 텍스트 레이아웃에 제목과 설명 컨테이너 추가
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_container)

        # 이미지가 있는 경우 이미지 레이블 생성
        if self.image_path:
            self.image_label = QLabel()
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
                self.image_label.setAlignment(Qt.AlignCenter)
            else:
                self.image_label.setText("이미지를 찾을 수 없습니다")
                self.image_label.setStyleSheet("color: red;")

            # 메인 레이아웃에 텍스트 위젯과 이미지 레이블 추가
            main_layout.addWidget(self.text_widget, 7)  # 텍스트에 더 많은 공간 할당 (비율 7)
            main_layout.addWidget(self.image_label, 3)  # 이미지에 적은 공간 할당 (비율 3)
        else:
            # 이미지가 없는 경우 텍스트 위젯만 추가
            main_layout.addWidget(self.text_widget, 1)

    def add_list_item(self, item_text):
        """
        섹션에 리스트 아이템 추가

        Args:
            item_text (str): 리스트 아이템 텍스트
        """
        # 섹션의 텍스트 위젯 레이아웃 가져오기
        layout = self.text_widget.layout()

        # 리스트 컨테이너가 없으면 생성
        list_container = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QWidget) and widget.objectName() == "list_container":
                list_container = widget
                break

        if not list_container:
            list_container = QWidget()
            list_container.setObjectName("list_container")
            list_container.setStyleSheet("border: none; background-color: transparent;")
            list_layout = QVBoxLayout(list_container)
            list_layout.setContentsMargins(20, 5, 5, 5)
            list_layout.setSpacing(5)
            layout.addWidget(list_container)
        else:
            list_layout = list_container.layout()

        # 리스트 아이템 레이블 생성 및 추가
        item_label = QLabel(f"• {item_text}")
        item_label.setWordWrap(True)
        item_label.setStyleSheet("font-size: 15px; border: none;")
        list_layout.addWidget(item_label)