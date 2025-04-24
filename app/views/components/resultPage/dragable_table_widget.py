# from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QApplication
# from PyQt5.QtCore import Qt, QMimeData
# from PyQt5.QtGui import QDrag
#
#
# class DraggableTableWidget(QTableWidget):
#     """드래그 앤 드롭이 가능한 테이블 위젯"""
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setDragEnabled(True)
#         self.setAcceptDrops(True)
#         self.viewport().setAcceptDrops(True)
#         self.setDragDropOverwriteMode(False)
#         self.setDropIndicatorShown(True)
#         self.drag_start_position = None  # 드래그 시작 위치 변수 초기화
#
#         # 다른 속성 설정
#         self.setSelectionBehavior(QTableWidget.SelectItems)
#         self.setSelectionMode(QTableWidget.SingleSelection)
#         self.setAlternatingRowColors(True)
#         self.horizontalHeader().setStretchLastSection(True)
#         self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#
#         # 스타일 설정
#         self.setStyleSheet("""
#             QTableWidget {
#                 background-color: white;
#                 gridline-color: #D9D9D9;
#                 font-size: 12px;
#             }
#             QTableWidget::item {
#                 padding: 5px;
#             }
#             QTableWidget::item:selected {
#                 background-color: #E0E0FF;
#             }
#             QHeaderView::section {
#                 background-color: #F0F0F0;
#                 padding: 5px;
#                 font-weight: bold;
#                 border: 1px solid #D9D9D9;
#             }
#         """)
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.drag_start_position = event.pos()
#         super().mousePressEvent(event)
#
#     def mouseMoveEvent(self, event):
#         # 왼쪽 버튼이 아니거나 드래그 시작 위치가 설정되지 않은 경우 종료
#         if not (event.buttons() & Qt.LeftButton) or self.drag_start_position is None:
#             return
#
#         # 드래그 최소 거리 확인
#         if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
#             return
#
#         # 현재 선택된 셀의 위치와 데이터 확인
#         current_row = self.currentRow()
#         current_column = self.currentColumn()
#
#         # 선택된 셀이 유효한지 확인
#         if current_row < 0 or current_column < 0:
#             return
#
#         current_item = self.item(current_row, current_column)
#
#         # 셀에 아이템이 없으면 종료
#         if current_item is None:
#             return
#
#         # 아이템에 텍스트가 없으면 종료
#         if not current_item.text():
#             return
#
#         # 드래그 객체 생성
#         drag = QDrag(self)
#         mime_data = QMimeData()
#
#         # MIME 데이터 설정
#         mime_data.setText(current_item.text())
#         mime_data.setData("application/x-cell-position", f"{current_row},{current_column}".encode())
#         drag.setMimeData(mime_data)
#
#         # 드래그 실행
#         drop_action = drag.exec_(Qt.MoveAction)
#
#     def dragEnterEvent(self, event):
#         if event.mimeData().hasText():
#             event.acceptProposedAction()
#         else:
#             event.ignore()
#
#     def dragMoveEvent(self, event):
#         if event.mimeData().hasText():
#             event.acceptProposedAction()
#         else:
#             event.ignore()
#
#     def dropEvent(self, event):
#         try:
#             if event.mimeData().hasText():
#                 # 드롭 위치에 있는 셀 가져오기
#                 drop_position = event.pos()
#                 drop_row = self.rowAt(drop_position.y())
#                 drop_column = self.columnAt(drop_position.x())
#
#                 # 유효한 셀 위치인지 확인
#                 if drop_row < 0 or drop_column < 0:
#                     event.ignore()
#                     return
#
#                 # 드래그 시작 위치 데이터 가져오기
#                 position_data = event.mimeData().data("application/x-cell-position")
#                 if position_data:
#                     try:
#                         source_position = position_data.data().decode()
#                         source_row, source_column = map(int, source_position.split(","))
#
#                         # 소스와 타겟이 같은 위치인지 확인
#                         if source_row == drop_row and source_column == drop_column:
#                             event.ignore()
#                             return
#
#                         # 드래그 소스 셀의 데이터 가져오기
#                         source_text = event.mimeData().text()
#
#                         # 타겟 셀의 데이터 가져오기
#                         target_item = self.item(drop_row, drop_column)
#                         target_text = target_item.text() if target_item else ""
#
#                         # 타겟 셀에 소스 셀의 데이터 설정
#                         self.setItem(drop_row, drop_column, QTableWidgetItem(source_text))
#
#                         # 소스 셀에 타겟 셀의 데이터 설정 (값 교환)
#                         self.setItem(source_row, source_column, QTableWidgetItem(target_text))
#
#                         event.acceptProposedAction()
#                     except Exception as e:
#                         print(f"드롭 처리 중 오류 발생: {str(e)}")
#                         event.ignore()
#                 else:
#                     # 외부에서 텍스트 드롭
#                     self.setItem(drop_row, drop_column, QTableWidgetItem(event.mimeData().text()))
#                     event.acceptProposedAction()
#             else:
#                 event.ignore()
#         except Exception as e:
#             print(f"dropEvent에서 예외 발생: {str(e)}")
#             event.ignore()