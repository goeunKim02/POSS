# from PyQt5.QtGui import QFont, QCursor, QPainter
# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
#     QTableWidget, QTableView, QHeaderView, QMenu, QWidgetAction,
#     QCheckBox, QPushButton, QTableWidgetItem
# )
# from PyQt5.QtCore import (
#     pyqtSignal, Qt, QAbstractTableModel, QModelIndex,
#     QVariant, QSortFilterProxyModel, QPoint
# )
# import pandas as pd
#
#
# class FilterHeader(QHeaderView):
#     """헤더 필터링을 위한 사용자 정의 헤더"""
#
#     def __init__(self, orientation, parent=None):
#         super().__init__(orientation, parent)
#         self.setSectionsClickable(True)  # 헤더 클릭 가능하게 설정
#
#     def paintSection(self, painter, rect, logicalIndex):
#         super().paintSection(painter, rect, logicalIndex)
#         # 필터 아이콘이나 추가 표시가 필요한 경우 여기에 구현
#
#
# class MultiFilterProxy(QSortFilterProxyModel):
#     """다중 필터 프록시 모델"""
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         # 컬럼 인덱스 -> 선택된 값 리스트
#         self.filters = {}
#
#     def filterAcceptsRow(self, sourceRow, sourceParent):
#         if not self.filters:
#             return True
#
#         model = self.sourceModel()
#         for col, vals in self.filters.items():
#             if not vals:  # 필터 값이 없으면 모든 행 표시
#                 continue
#
#             cell = model.data(model.index(sourceRow, col), Qt.DisplayRole)
#             if cell not in vals:
#                 return False
#
#         return True
#
#     def sort(self, column, order=Qt.AscendingOrder):
#         super().sort(column, order)
#
#
# class PandasModel(QAbstractTableModel):
#     """pandas DataFrame을 위한 테이블 모델"""
#
#     def __init__(self, df=None, parent=None):
#         super().__init__(parent)
#         self._df = pd.DataFrame() if df is None else df
#
#     def rowCount(self, parent=QModelIndex()):
#         return len(self._df.index)
#
#     def columnCount(self, parent=QModelIndex()):
#         return len(self._df.columns)
#
#     def data(self, index, role=Qt.DisplayRole):
#         if not index.isValid() or role != Qt.DisplayRole:
#             return QVariant()
#         return str(self._df.iat[index.row(), index.column()])
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
#             return self._df.columns[section]
#         if orientation == Qt.Vertical and role == Qt.DisplayRole:
#             return str(self._df.index[section])
#         return QVariant()
#
#
# class EnhancedTableFilterComponent(QWidget):
#     """
#     향상된 테이블 필터 컴포넌트
#     헤더 클릭으로 다중 필터 선택 기능 제공
#     """
#     filter_applied = pyqtSignal()  # 필터가 적용되었을 때 발생하는 시그널
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.table_view = None
#         self.proxy_model = None
#         self._df = pd.DataFrame()
#         self.init_ui()
#
#     def init_ui(self):
#         # 메인 레이아웃
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#
#         # 제목 프레임
#         title_frame = QFrame()
#         title_frame.setFrameShape(QFrame.StyledPanel)
#         title_frame.setStyleSheet("""
#             background-color: #F5F5F5;
#             border: none;
#         """)
#         title_frame.setFixedHeight(40)
#
#         title_layout = QHBoxLayout(title_frame)
#         title_layout.setContentsMargins(10, 0, 0, 0)
#
#         # 제목 레이블
#         title_label = QLabel("데이터 필터링")
#         title_font = QFont()
#         title_font.setFamily("Arial")
#         title_font.setPointSize(9)
#         title_font.setBold(True)
#         title_font.setWeight(99)
#         title_label.setFont(title_font)
#         title_layout.addWidget(title_label)
#
#         # 메인 레이아웃에 프레임 추가
#         main_layout.addWidget(title_frame)
#
#         # 테이블 뷰 생성
#         self.table_view = QTableView()
#         self.table_view.setAlternatingRowColors(True)
#
#         # 사용자 정의 헤더 설정
#         header = FilterHeader(Qt.Horizontal, self.table_view)
#         self.table_view.setHorizontalHeader(header)
#         header.setStretchLastSection(True)
#         self.table_view.verticalHeader().setVisible(False)  # 행 번호 숨김
#
#         # 다중 필터 프록시 모델 설정
#         self.proxy_model = MultiFilterProxy(self)
#         self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
#         self.table_view.setModel(self.proxy_model)
#
#         # 헤더 클릭 이벤트 연결
#         header.sectionClicked.connect(self.on_header_clicked)
#
#         # 레이아웃에 테이블 뷰 추가
#         main_layout.addWidget(self.table_view)
#
#         # 버튼 영역
#         button_frame = QFrame()
#         button_frame.setStyleSheet("background-color: white; border: none;")
#         button_layout = QHBoxLayout(button_frame)
#
#         # 필터 리셋 버튼
#         self.reset_btn = QPushButton("필터 초기화")
#         self.reset_btn.setFont(QFont("Arial"))
#         self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
#         self.reset_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #808080;
#                 color: white;
#                 border-radius: 10px;
#                 padding: 5px 10px;
#                 border: none;
#             }
#             QPushButton:hover {
#                 background-color: #606060;
#             }
#         """)
#         self.reset_btn.clicked.connect(self.reset_filter)
#
#         button_layout.addStretch(1)
#         button_layout.addWidget(self.reset_btn)
#
#         main_layout.addWidget(button_frame)
#
#     def _update_filter(self, col, value, checked):
#         """필터 업데이트 (체크박스 상태 변경시 호출)"""
#         current = set(self.proxy_model.filters.get(col, []))
#         if checked:
#             current.add(value)
#         else:
#             current.discard(value)
#         self.proxy_model.filters[col] = list(current)
#         self.proxy_model.invalidateFilter()
#         self.filter_applied.emit()
#
#     def on_header_clicked(self, logicalIndex):
#         """헤더 클릭 시 필터 메뉴 표시"""
#         # 현재 컬럼의 고유 값 가져오기
#         col_name = self._df.columns[logicalIndex]
#         raw = self._df[col_name].dropna().tolist()
#
#         # 숫자인 경우 숫자 정렬로 처리, 아닌 경우 문자열 정렬
#         try:
#             nums = sorted({float(v) for v in raw})
#             vals = [str(int(n)) if n.is_integer() else str(n) for n in nums]
#         except ValueError:
#             vals = sorted(set(raw), key=lambda x: str(x))
#
#         # 메뉴 생성
#         menu = QMenu(self)
#         header = self.table_view.horizontalHeader()
#         width = header.sectionSize(logicalIndex)
#         menu.setFixedWidth(max(width, 200))  # 최소 너비 설정
#
#         # 현재 선택된 필터 항목 가져오기
#         current = set(self.proxy_model.filters.get(logicalIndex, []))
#
#         # 체크박스 추가
#         for v in vals:
#             act = QWidgetAction(menu)
#             cb = QCheckBox(v, menu)
#             cb.setChecked(v in current)
#             cb.toggled.connect(
#                 lambda checked, val=v, col=logicalIndex:
#                 self._update_filter(col, val, checked)
#             )
#             act.setDefaultWidget(cb)
#             menu.addAction(act)
#
#         # 정렬 옵션 추가
#         menu.addSeparator()
#         asc = menu.addAction("오름차순")
#         desc = menu.addAction("내림차순")
#
#         # 메뉴 표시 위치 계산
#         pos = header.mapToGlobal(
#             QPoint(header.sectionViewportPosition(logicalIndex), header.height())
#         )
#
#         # 메뉴 실행 및 선택 처리
#         sel = menu.exec(pos)
#         if sel == asc:
#             self.proxy_model.sort(logicalIndex, Qt.AscendingOrder)
#         elif sel == desc:
#             self.proxy_model.sort(logicalIndex, Qt.DescendingOrder)
#
#     def set_data(self, df):
#         """데이터프레임 설정"""
#         self._df = df.copy()
#         model = PandasModel(self._df, self)
#         self.proxy_model.filters.clear()
#         self.proxy_model.setSourceModel(model)
#         self.filter_applied.emit()
#
#     def reset_filter(self):
#         """필터 초기화"""
#         self.proxy_model.filters.clear()
#         self.proxy_model.invalidateFilter()
#         self.filter_applied.emit()
#
#     def convert_table_to_dataframe(self, table_widget):
#         """QTableWidget을 DataFrame으로 변환"""
#         rows = table_widget.rowCount()
#         cols = table_widget.columnCount()
#
#         # 컬럼명 추출
#         headers = []
#         for col in range(cols):
#             item = table_widget.horizontalHeaderItem(col)
#             headers.append(item.text() if item else f"Column {col}")
#
#         # 데이터 추출
#         data = []
#         for row in range(rows):
#             row_data = []
#             for col in range(cols):
#                 item = table_widget.item(row, col)
#                 row_data.append(item.text() if item else "")
#             data.append(row_data)
#
#         # DataFrame 생성
#         return pd.DataFrame(data, columns=headers)
#
#     def get_filtered_data(self):
#         """필터링된 데이터를 DataFrame으로 반환"""
#         model = self.proxy_model
#         source_model = model.sourceModel()
#
#         # 필터링된 행 인덱스 가져오기
#         rows = []
#         for row in range(model.rowCount()):
#             source_idx = model.mapToSource(model.index(row, 0)).row()
#             rows.append(source_idx)
#
#         # 원본 데이터에서 필터링된 행만 선택
#         if not rows:
#             return pd.DataFrame(columns=self._df.columns)
#         return self._df.iloc[rows].copy()