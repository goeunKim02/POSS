from PyQt5.QtWidgets import QLabel, QApplication, QToolTip
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
import pandas as pd
import json
from app.resources.styles.item_style import ItemStyle


"""드래그 가능한 아이템 라벨"""
class DraggableItemLabel(QLabel):

    # 아이템 선택 이벤트를 위한 시그널 추가
    itemSelected = pyqtSignal(object)  # 선택된 아이템 참조를 전달

    # 아이템 더블클릭 이벤트를 위한 시그널 추가
    itemDoubleClicked = pyqtSignal(object)  # 더블클릭된 아이템 참조를 전달

    def __init__(self, text, parent=None, item_data=None):
        super().__init__(text, parent)

        # 검증 에러상태 변수
        self.is_validation_error = False
        self.validation_error_message = None
        
        # 출하 실패 상태 변수
        self.is_shipment_failure = False
        self.shipment_failure_reason = None

        self.setStyleSheet(ItemStyle.DEFAULT_STYLE)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(False)  # 아이템 자체는 드롭 받지 않도록 변경
        self.drag_start_position = None
        self.setWordWrap(True)
        self.setMinimumHeight(25)
        self.adjustSize()

        # 사전할당 상태 관련 속성 
        self.is_pre_assigned = False

        # 선택 상태 추가
        self.is_selected = False

        # 툴팁 관련 설정
        QToolTip.setFont(QFont('Arial', 10))

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
        if self.item_data is None:
            return self.text()

        # 통일된 테이블 스타일
        tooltip = """
        <style>
            table.tooltip-table {
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 10pt;
            }
            table.tooltip-table th {
                background-color: #1428A0;
                color: white;
                padding: 4px 8px;
            }
            table.tooltip-table td {
                background-color: #F5F5F5;
                padding: 4px 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            table.tooltip-table tr:last-child td {
                border-bottom: none;
            }
        </style>
        <table class='tooltip-table'>
            <tr><th colspan='2'>Item Information</th></tr>
        """

        for key, value in self.item_data.items():
            if pd.notna(value):
                tooltip += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"

        if self.is_pre_assigned:
            tooltip += "<tr><td><b>Pre-Assigned</b></td><td style='color:green;'>Yes</td></tr>"
        if self.is_shortage:
            tooltip += "<tr><td><b>Material Shortage</b></td><td style='color:red;'>Yes</td></tr>"
        if self.is_shipment_failure:
            tooltip += "<tr><td><b>Shipment Status</b></td><td style='color:red;'>Failure</td></tr>"
            if self.shipment_failure_reason:
                tooltip += f"<tr><td><b>Failure Reason</b></td><td>{self.shipment_failure_reason}</td></tr>"
        if self.is_validation_error:
            tooltip += "<tr><td><b>Validation Error</b></td><td style='color:red;'>Yes</td></tr>"
            if self.validation_error_message:
                tooltip += f"<tr><td><b>Error Details</b></td><td style='color:red;'>{self.validation_error_message}</td></tr>"

        tooltip += "</table>"
        return tooltip


    def _create_shortage_tooltip(self):
        if not self.shortage_data:
            return self._create_tooltip_text()
        item_code = self.item_data.get('Item', 'Unknown Item') if self.item_data else 'Unknown Item'
        tooltip = """
        <style>
            table.tooltip-table {
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 10pt;
            }
            table.tooltip-table th {
                background-color: #1428A0;
                color: white;
                padding: 4px 8px;
            }
            table.tooltip-table td {
                background-color: #F5F5F5;
                padding: 4px 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            table.tooltip-table tr:last-child td {
                border-bottom: none;
            }
        </style>
        <table class='tooltip-table'>
            <tr><th colspan='4'>{item_code} Material Shortage Details</th></tr>
            <tr>
                <th>Material</th>
                <th>Required</th>
                <th>Available</th>
                <th>Shortage</th>
            </tr>
        """
        for shortage in self.shortage_data:
            tooltip += f"<tr><td>{shortage['Material']}</td>"
            tooltip += f"<td align='right'>{int(shortage['Required']):,}</td>"
            tooltip += f"<td align='right'>{int(shortage['Available']):,}</td>"
            tooltip += f"<td align='right' style='color:red'>{int(shortage['Shortage']):,}</td></tr>"
        tooltip += "</table><br/>"
        tooltip += self._create_tooltip_text()
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

    """더블클릭 이벤트 처리"""
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 더블클릭 이벤트 발생
            self.itemDoubleClicked.emit(self)
            event.accept()

    """마우스가 위젯 위에 올라갔을 때 호출됨"""
    def enterEvent(self, event):
        if not self.is_selected:
            if self.is_validation_error:  # 조정 검증 에러
                self.setStyleSheet(ItemStyle.VALIDATION_ERROR_HOVER_STYLE) 
            elif self.is_pre_assigned and self.is_shortage and self.is_shipment_failure:  # 사전할당/자재부족/출하실패
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHORTAGE_SHIPMENT_HOVER_STYLE)
            elif self.is_pre_assigned and self.is_shortage:  # 사전할당/자재부족
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHORTAGE_HOVER_STYLE)
            elif self.is_pre_assigned and self.is_shipment_failure:  # 사전할당/출하실패
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHIPMENT_HOVER_STYLE)
            elif self.is_shortage and self.is_shipment_failure:  # 자재부족/출하실패
                self.setStyleSheet(ItemStyle.SHORTAGE_SHIPMENT_HOVER_STYLE) 
            elif self.is_pre_assigned:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_HOVER_STYLE)
            elif self.is_shortage:
                self.setStyleSheet(ItemStyle.SHORTAGE_HOVER_STYLE)
            elif self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.SHIPMENT_FAILURE_HOVER_STYLE)
            else:
                self.setStyleSheet(ItemStyle.HOVER_STYLE)
        super().enterEvent(event)

    """마우스가 위젯을 벗어났을 때 호출됨"""
    def leaveEvent(self, event):
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
                elif isinstance(v, (int, float, bool)):  #  숫자타입은 그대로 유지
                    serializable_data[k] = v
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

    """선택 상태 토글 및 스타일 적용"""
    def toggle_selected(self):
        self.is_selected = not self.is_selected
        self.update_style()

    """선택 상태 직접 설정"""
    def set_selected(self, selected):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update_style()

    """사전할당 상태 설정"""
    def set_pre_assigned_status(self, is_pre_assigned):
        self.is_pre_assigned = is_pre_assigned
        self.update_style()

        # 툴팁에도 사전할당 정보 표시
        if self.item_data is not None:
            self.setToolTip(self._create_tooltip_text())

    """자재 부족 상태 설정"""
    def set_shortage_status(self, is_shortage, shortage_data=None):
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

    """자재 부족 정보 툴팁 생성"""
    def _create_shortage_tooltip(self):
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

    """현재 상태에 맞게 스타일 업데이트"""
    def update_style(self):
        if self.is_selected:
            if self.is_validation_error:
                self.setStyleSheet(ItemStyle.VALIDATION_ERROR_SELECTED_STYLE)
            elif self.is_pre_assigned and self.is_shortage and self.is_shipment_failure:  
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHORTAGE_SHIPMENT_SELECTED_STYLE)
            elif self.is_pre_assigned and self.is_shortage:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHORTAGE_SELECTED_STYLE)
            elif self.is_pre_assigned and self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHIPMENT_SELECTED_STYLE)
            elif self.is_shortage and self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.SHORTAGE_SHIPMENT_SELECTED_STYLE)  
            elif self.is_pre_assigned:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SELECTED_STYLE)
            elif self.is_shortage:
                self.setStyleSheet(ItemStyle.SHORTAGE_SELECTED_STYLE)
            elif self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.SHIPMENT_FAILURE_SELECTED_STYLE)
            else:
                self.setStyleSheet(ItemStyle.SELECTED_STYLE)
        else:
            if self.is_validation_error:
                self.setStyleSheet(ItemStyle.VALIDATION_ERROR_STYLE)
            elif self.is_pre_assigned and self.is_shortage and self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHORTAGE_SHIPMENT_STYLE)
            elif self.is_pre_assigned and self.is_shortage:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHORTAGE_STYLE)
            elif self.is_pre_assigned and self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_SHIPMENT_STYLE)
            elif self.is_shortage and self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.SHORTAGE_SHIPMENT_STYLE) 
            elif self.is_pre_assigned:
                self.setStyleSheet(ItemStyle.PRE_ASSIGNED_STYLE)
            elif self.is_shortage:
                self.setStyleSheet(ItemStyle.SHORTAGE_STYLE)
            elif self.is_shipment_failure:
                self.setStyleSheet(ItemStyle.SHIPMENT_FAILURE_STYLE)
            else:
                self.setStyleSheet(ItemStyle.SELECTED_STYLE)

    """아이템 데이터로부터 표시 텍스트 업데이트"""
    def update_text_from_data(self):
        if self.item_data and 'Item' in self.item_data:
            item_info = str(self.item_data['Item'])

            # MFG 정보가 있으면 수량 정보로 추가
            if 'Qty' in self.item_data and pd.notna(self.item_data['Qty']):
                item_info += f" ({self.item_data['Qty']}개)"

            self.setText(item_info)

            # 툴팁도 업데이트
            self.setToolTip(self._create_tooltip_text())

    """아이템 데이터 업데이트"""
    def update_item_data(self, new_data):
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

            # 검증 상태 변수
            validation_failed = False
            validation_mesasge = ""
            
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
                    validation_failed = True
                    validation_mesasge = message
                    print(f"검증 실패지만 변경 허용: {message}")
                
            # 검증 상관없이 데이터 업데이트 진행
            self.item_data = new_data.copy() if new_data else None

            # 텍스트와 툴팁 업데이트
            self.update_text_from_data()
            self.setToolTip(self._create_tooltip_text())

            if validation_failed:
                self.set_validation_error(True, validation_mesasge)
                return True, validation_mesasge  # 성공이지만 에러메세지 표시
            else:
                self.set_validation_error(False)  # 에러상태 해제
                return True, ""
            
        return False, "데이터가 없습니다."
    
    """출하 실패 상태 설정"""
    def set_shipment_failure(self, is_failure, reason=None):
        self.is_shipment_failure = is_failure
        self.shipment_failure_reason = reason if is_failure else None
        self.update_style()  # 스타일 업데이트
        
        # 툴팁 업데이트 - 전체 툴팁 다시 생성
        self.setToolTip(self._create_tooltip_text())
        
        # 툴팁 업데이트
        if is_failure and reason:
            # 기존 툴팁에 출하 실패 정보 추가
            base_tooltip = self._create_tooltip_text()
            # failure_info = f"<tr><td colspan='2' style='background-color:#FFCCCC; color:red;'><b>Shipment Failure:</b> {reason}</td></tr>"
            
            # 테이블 닫기 태그 앞에 실패 정보 삽입
            # new_tooltip = base_tooltip.replace("</table>", failure_info + "</table>")
            # self.setToolTip(new_tooltip)
        else:
            # 기본 툴팁으로 복원
            self.setToolTip(self._create_tooltip_text())


    """검증 에러상태 설정"""
    def set_validation_error(self, is_error, error_message=None):
        self.is_validation_error = is_error
        self.validation_error_message = error_message if is_error else None
        self.update_style()

        # 툴팁 업데이트
        self.setToolTip(self._create_tooltip_text())

