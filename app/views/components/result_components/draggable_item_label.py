from PyQt5.QtWidgets import QLabel, QApplication, QToolTip
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
import pandas as pd
import json


class DraggableItemLabel(QLabel):
    """드래그 가능한 아이템 라벨"""

    def __init__(self, text, parent=None, item_data=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            background-color: #F0F0F0;
            border: 1px solid #D0D0D0;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(False)  # 아이템 자체는 드롭 받지 않도록 변경
        self.drag_start_position = None
        self.setWordWrap(True)
        self.setMinimumHeight(25)
        self.adjustSize()

        # 툴팁 관련 설정
        QToolTip.setFont(QFont('SansSerif', 10))

        # 아이템 데이터 저장 (엑셀 행 정보)
        self.item_data = item_data

        # 아이템 데이터가 있으면 툴팁 생성
        if self.item_data is not None:
            self.setToolTip(self._create_tooltip_text())
        else:
            self.setToolTip(text)  # 데이터가 없으면 텍스트만 표시

        # 툴팁 자동 표시 활성화
        self.setMouseTracking(True)

    def _create_tooltip_text(self):
        """아이템 데이터에서 툴팁 텍스트 생성"""
        if self.item_data is None:
            return self.text()

        # 아이템 데이터에서 모든 정보를 포함한 툴팁 생성
        tooltip = "<table border='0' cellspacing='2' cellpadding='2'>"

        # 모든 열에 대해 키-값 쌍으로 테이블 생성
        for key, value in self.item_data.items():
            if pd.notna(value):  # NaN 값이 아닌 경우만 표시
                tooltip += f"<tr><td><b>{key}:</b></td><td>{value}</td></tr>"

        tooltip += "</table>"
        return tooltip

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)  # 마우스 누를 때 커서 변경

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)  # 마우스 놓을 때 커서 원래대로

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self.drag_start_position is None:
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        # 텍스트 데이터 저장
        mime_data.setText(self.text())

        # 아이템 데이터를 JSON으로 직렬화하여 저장
        if self.item_data is not None:
            # 딕셔너리의 모든 값을 문자열로 변환 (JSON 직렬화를 위해)
            serializable_data = {}
            for k, v in self.item_data.items():
                if pd.isna(v):  # NaN 값은 None으로 변환
                    serializable_data[k] = None
                else:
                    serializable_data[k] = str(v)

            # JSON으로 직렬화하여 MIME 데이터에 저장
            json_data = json.dumps(serializable_data)
            mime_data.setData("application/x-item-full-data", json_data.encode())

        # 기본 아이템 식별자도 함께 저장 (이전 버전과의 호환성 유지)
        mime_data.setData("application/x-item-data", self.text().encode())

        drag.setMimeData(mime_data)

        # 드래그 중 표시될 이미지 생성
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)  # 투명 배경으로 시작

        # 아이템의 현재 모습을 픽스맵에 그리기
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)  # 약간 투명하게 만들기
        self.render(painter)
        painter.end()

        # 드래그 이미지 설정
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())  # 마우스 커서 위치 설정

        # 드래그 액션 실행
        drag.exec_(Qt.MoveAction)