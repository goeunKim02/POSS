# from PyQt5.QtCore import pyqtSignal, Qt
# from PyQt5.QtGui import QFont
# from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QFrame
#
#
# class SheetSelectorComponent(QWidget):
#
#     # 엑셀 시트 선택 컴포넌트
#     #엑셀 파일의 시트를 선택할 수 있는 드롭다운 UI 제공
#
#     sheet_changed = pyqtSignal(str)  # 시트가 변경되었을 때 발생하는 시그널 (선택된 시트명 전달)
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         # 기본 레이아웃 설정
#         self.frame = QFrame(self)  # QFrame 추가
#         self.frame.setFrameShape(QFrame.StyledPanel)
#
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.frame)
#
#         sheet_frame = QFrame()
#         sheet_frame.setStyleSheet("background-color: white; border: 3px solid #cccccc; border-radius: 10px; padding: 5px 10px; margin-top: 8px;")
#
#         layout.addWidget(sheet_frame)
#
#         frame_layout = QHBoxLayout(sheet_frame)
#         frame_layout.setContentsMargins(5, 5, 5, 5)
#
#         # 레이블 생성
#         sheet_label = QLabel("Select Sheet:")
#         sheet_label_font = QFont()
#         sheet_label_font.setFamily("Arial")
#         sheet_label.setFont(sheet_label_font)
#         sheet_label.setStyleSheet("border:none")
#
#         # 콤보박스 생성
#         self.sheet_combo = QComboBox()
#         self.sheet_combo.setStyleSheet("""
#             QComboBox {
#                 border: 1px solid #cccccc;
#                 border-radius: 10px;
#                 padding: 3px 5px;
#                 min-width: 150px;
#                 background-color: white;
#             }
#             QComboBox::drop-down {
#                 subcontrol-origin: padding;
#                 subcontrol-position: top right;
#                 width: 20px;
#                 border-left: 1px solid #cccccc;
#                 border-radius: 10px;
#             }
#             QComboBox QAbstractItemView {
#                 background-color: white;
#                 border: 1px solid #cccccc;
#                 border-radius: 10px;
#                 selection-background-color: #1428A0;
#                 selection-color: white;
#                 padding: 3px;
#             }
#         """)
#         self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
#
#         # 레이아웃에 위젯 추가
#         frame_layout.addWidget(sheet_label)
#         frame_layout.addWidget(self.sheet_combo, 1)
#
#         # 처음에는 숨김
#         self.setVisible(False)
#
#     def set_sheets(self, sheet_names):
#         """시트 목록 설정"""
#         if not sheet_names:
#             self.setVisible(False)
#             return
#
#         # 콤보박스 내용 초기화
#         self.sheet_combo.blockSignals(True)
#         self.sheet_combo.clear()
#
#         # 시트 이름 추가
#         self.sheet_combo.addItems(sheet_names)
#
#         self.sheet_combo.blockSignals(False)
#         self.setVisible(True)
#
#     def get_current_sheet(self):
#         """현재 선택된 시트 이름 반환"""
#         return self.sheet_combo.currentText()
#
#     def on_sheet_changed(self, sheet_name):
#         """시트 선택이 변경되면 시그널 발생"""
#         self.sheet_changed.emit(sheet_name)