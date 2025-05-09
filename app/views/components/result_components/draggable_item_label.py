from PyQt5.QtWidgets import QLabel, QApplication, QToolTip
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
import pandas as pd
import json


class DraggableItemLabel(QLabel):
    """드래그 가능한 아이템 라벨"""

    # 아이템 선택 이벤트를 위한 시그널 추가
    itemSelected = pyqtSignal(object)  # 선택된 아이템 참조를 전달

    # 아이템 더블클릭 이벤트를 위한 시그널 추가
    itemDoubleClicked = pyqtSignal(object)  # 더블클릭된 아이템 참조를 전달

    def __init__(self, text, parent=None, item_data=None):
        super().__init__(text, parent)

        # 기본 스타일 정의
        self.default_style = """
            background-color: #F0F0F0;
            border: 1px solid #D0D0D0;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """

        # 선택됐을 때 스타일 정의
        self.selected_style = """
            background-color: #C2E0FF;
            border: 1px solid #0078D7;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """

        # 호버 스타일 정의
        self.hover_style = """
            background-color: #E6E6E6;
            border: 1px solid #B8B8B8;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """

        # 자재 부족 스타일 추가
        self.shortage_style = """
            background-color: #FFE0E0;
            border: 1px solid #FF8080;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """
        
        self.shortage_selected_style = """
            background-color: #FFC0C0;
            border: 1px solid #0078D7;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """
        
        self.shortage_hover_style = """
            background-color: #FFC8C8;
            border: 1px solid #FF6060;
            border-radius: 4px;
            padding: 5px;
            margin: 2px;
        """

        self.setStyleSheet(self.default_style)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(False)  # 아이템 자체는 드롭 받지 않도록 변경
        self.drag_start_position = None
        self.setWordWrap(True)
        self.setMinimumHeight(25)
        self.adjustSize()

        # 선택 상태 추가
        self.is_selected = False

        # 툴팁 관련 설정
        QToolTip.setFont(QFont('SansSerif', 10))

        # 자재 부족 상태 관련 속성 추가
        self.is_shortage = False
        self.shortage_data = None

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

            # 클릭 시 선택 상태 토글
            self.toggle_selected()

            # 선택 상태 변경 이벤트 발생
            self.itemSelected.emit(self)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)  # 마우스 놓을 때 커서 원래대로

    def mouseDoubleClickEvent(self, event):
        """더블클릭 이벤트 처리"""
        if event.button() == Qt.LeftButton:
            # 더블클릭 이벤트 발생
            self.itemDoubleClicked.emit(self)
            event.accept()

    def enterEvent(self, event):
        """마우스가 위젯 위에 올라갔을 때 호출됨"""
        if not self.is_selected:
            if self.is_shortage:
                self.setStyleSheet(self.shortage_hover_style)
            else:
                self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """마우스가 위젯을 벗어났을 때 호출됨"""
        if not self.is_selected:
            self.update_style()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self.drag_start_position is None:
            return

        # 최소 드래그 거리 확인 (맨해튼 거리)
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

            # 디버깅을 위한 출력
            print(f"직렬화된 데이터: {json_data}")

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

    def toggle_selected(self):
        """선택 상태 토글 및 스타일 적용"""
        self.is_selected = not self.is_selected
        self.update_style()

    def set_selected(self, selected):
        """선택 상태 직접 설정"""
        if self.is_selected != selected:
            self.is_selected = selected
            self.update_style()

    # 자재 부족 상태 설정 메서드 추가
    def set_shortage_status(self, is_shortage, shortage_data=None):
        """자재 부족 상태 설정"""
        self.is_shortage = is_shortage
        self.shortage_data = shortage_data
        self.update_style()
        
        # 자재 부족 상태에 따라 툴팁 업데이트
        if is_shortage and shortage_data:
            self.setToolTip(self._create_shortage_tooltip())
        else:
            # 기본 툴팁 사용
            if self.item_data is not None:
                self.setToolTip(self._create_tooltip_text())
            else:
                self.setToolTip(self.text())

    def _create_shortage_tooltip(self):
        """자재 부족 정보 툴팁 생성"""
        if not self.shortage_data:
            return self._create_tooltip_text()
        
        item_code = self.item_data.get('Item', 'Unknown Item') if self.item_data else 'Unknown Item'
        
        tooltip = f"<b>{item_code}</b> Material Shortage Details:<br><br>"
        tooltip += "<table border='1' cellspacing='0' cellpadding='3'>"
        tooltip += "<tr style='background-color:#f0f0f0'><th>Material</th><th>Required</th><th>Available</th><th>Shortage</th></tr>"
        
        for shortage in self.shortage_data:
            tooltip += f"<tr>"
            tooltip += f"<td>{shortage['Material']}</td>"
            tooltip += f"<td align='right'>{int(shortage['Required']):,}</td>"
            tooltip += f"<td align='right'>{int(shortage['Available']):,}</td>"
            tooltip += f"<td align='right' style='color:red'>{int(shortage['Shortage']):,}</td>"
            tooltip += f"</tr>"
        
        tooltip += "</table>"
        return tooltip

    def update_style(self):
        """현재 상태에 맞게 스타일 업데이트"""
        if self.is_selected:
            if self.is_shortage:
                self.setStyleSheet(self.shortage_selected_style)
            else:
                self.setStyleSheet(self.selected_style)
        else:
            if self.is_shortage:
                self.setStyleSheet(self.shortage_style)
            else:
                self.setStyleSheet(self.default_style)

    def update_text_from_data(self):
        """아이템 데이터로부터 표시 텍스트 업데이트"""
        if self.item_data and 'Item' in self.item_data:
            item_info = str(self.item_data['Item'])

            # MFG 정보가 있으면 수량 정보로 추가
            if 'Qty' in self.item_data and pd.notna(self.item_data['Qty']):
                item_info += f" ({self.item_data['Qty']}개)"

            self.setText(item_info)

            # 툴팁도 업데이트
            self.setToolTip(self._create_tooltip_text())

    def update_item_data(self, new_data):
        """아이템 데이터 업데이트"""
        if new_data:
            # 데이터 변경 전 검증 (부모 위젯을 통해 validator 찾기)
            validator = None
            parent = self.parent()
            while parent:
                if hasattr(parent, 'validator'):
                    validator = parent.validator
                    break
                # 그리드 위젯을 통해 validator 찾기
                if hasattr(parent, 'grid_widget') and hasattr(parent.grid_widget, 'validator'):
                    validator = parent.grid_widget.validator
                    break
                parent = parent.parent()
            
            # validator가 있으면 검증 수행
            if validator:
                # 현재 데이터와 신규 데이터 비교하여 변경 항목 검출
                is_move = False
                if self.item_data:
                    if ('Line' in new_data and 'Line' in self.item_data and 
                        new_data['Line'] != self.item_data['Line']):
                        is_move = True
                    if ('Time' in new_data and 'Time' in self.item_data and 
                        new_data['Time'] != self.item_data['Time']):
                        is_move = True
                
                # 검증 실행
                valid, message = validator.validate_adjustment(
                    new_data.get('Line'), 
                    new_data.get('Time'),
                    new_data.get('Item', ''),
                    new_data.get('Qty', 0),
                    self.item_data.get('Line') if is_move else None,
                    self.item_data.get('Time') if is_move else None
                )
                
                # 검증 실패 시 데이터 변경하지 않고 False 반환
                if not valid:
                    # 오류 메시지는 호출자에서 표시 (여기서는 표시하지 않음)
                    return False, message
            
            # 검증 통과 또는 validator 없음 - 데이터 업데이트 진행
            # 데이터 직접 할당 (데이터 참조 복사)
            self.item_data = new_data.copy() if new_data else None

            # 텍스트와 툴팁 업데이트
            self.update_text_from_data()
            self.setToolTip(self._create_tooltip_text())
            return True, ""
        return False, "데이터가 없습니다."