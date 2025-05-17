from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QHeaderView, QMenu, QWidgetAction,
    QCheckBox, QScrollArea
)
from PyQt5.QtCore import (
    pyqtSignal, Qt, QAbstractTableModel, QModelIndex,
    QVariant, QSortFilterProxyModel, QPoint, QTimer
)
import pandas as pd
from app.resources.fonts.font_manager import font_manager
from app.models.common.screen_manager import *

"""
헤더 필터링을 위한 사용자 정의 헤더
"""
class FilterHeader(QHeaderView):

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        # 필터 아이콘이나 추가 표시가 필요한 경우 여기에 구현


"""
다중 필터 프록시 모델
"""
class MultiFilterProxy(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        # 컬럼 인덱스 -> 선택된 값 리스트
        self.filters = {}

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if not self.filters:
            return True

        model = self.sourceModel()
        for col, vals in self.filters.items():
            if not vals:
                continue

            cell = model.data(model.index(sourceRow, col), Qt.DisplayRole)
            if cell not in vals:
                return False

        return True

    def sort(self, column, order=Qt.AscendingOrder):
        super().sort(column, order)


"""
pandas DataFrame을 위한 테이블 모델
"""
class PandasModel(QAbstractTableModel):

    def __init__(self, df=None, parent=None):
        super().__init__(parent)
        self._df = pd.DataFrame() if df is None else df

    def rowCount(self, parent=QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    # PandasModel 클래스의 data 메서드에 다음 코드 추가:
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        value = self._df.iat[index.row(), index.column()]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # None이나 NaN 값 처리
            if pd.isna(value):
                return ""
            return str(value)

        # 폰트 역할 추가
        elif role == Qt.FontRole:
            font = QFont(font_manager.get_just_font("SamsungOne-700").family(), f(6))
            return font

        # 배경색 역할 추가 (필요 시)
        elif role == Qt.BackgroundRole:
            # 특정 조건에 따라 다른 배경색 반환 가능
            # 예: 특정 값에 따라 배경색 변경
            return QBrush(QColor("white"))

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._df.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._df.index[section])
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        try:
            # 빈 문자열이 입력되면 원래 값 유지
            if value == "":
                return False

            row, col = index.row(), index.column()
            original_value = self._df.iat[row, col]
            column_dtype = self._df[self._df.columns[col]].dtype

            # 데이터 타입에 따른 적절한 변환
            try:
                if pd.api.types.is_integer_dtype(column_dtype):
                    converted_value = int(value)
                elif pd.api.types.is_float_dtype(column_dtype):
                    converted_value = float(value)
                else:
                    converted_value = str(value)
            except ValueError:
                # 변환 실패시 문자열로 처리
                converted_value = str(value)

            # 데이터프레임 업데이트 - 명시적 형변환
            self._df.loc[self._df.index[row], self._df.columns[col]] = converted_value
            self.dataChanged.emit(index, index)
            return True
        except Exception as e:
            print("데이터 수정 오류:", e)
            return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


"""
커스텀 메뉴 클래스 - 구분선 없는 스타일 적용
"""
class CustomMenu(QMenu):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 0px;
                margin: 0px;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
                border: none;
                margin: 0px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
                color: black;
            }
            QMenu::separator {
                height: 0px;
                margin: 0px;
                padding: 0px;
                border: none;
                background: transparent;
            }
            QCheckBox {
                border: none;
                margin: 0px;
                padding: 3px;
                spacing: 5px;
                background: transparent;
            }
            QWidget {
                border: none;
                margin: 0px;
                padding: 0px;
            }
            QScrollArea {
                border-bottom: 1px solid #cccccc; 
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)


"""
테두리가 없는 체크박스
"""
class NoOutlineCheckBox(QCheckBox):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                border: none;
                background: transparent;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #b1b1b1;
            }
            QCheckBox::indicator:checked {
                background-color: #1428A0;
                border: 1px solid #1428A0;
            }
        """)


"""
향상된 테이블 필터 컴포넌트
헤더 클릭으로 다중 필터 선택 기능 제공
"""
class EnhancedTableFilterComponent(QWidget):
    filter_applied = pyqtSignal()  # 필터가 적용되었을 때 발생하는 시그널
    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_view = None
        self.proxy_model = None
        self._df = pd.DataFrame()
        self._original_df = pd.DataFrame()
        self.edited_cells = {}
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 테이블 뷰 생성
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        # 테이블 수정가능하게 하는것
        self.table_view.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)

        # 사용자 정의 헤더 설정
        header = FilterHeader(Qt.Horizontal, self.table_view)
        header.setStyleSheet(f"""
            QHeaderView {{
                border: none;
                background-color: transparent;
                border-radius: 0px;
            }}
            QHeaderView::section {{
                background-color: #F5F5F5;
                border-right: 1px solid #cccccc;
                padding: 2px;
                border-radius: 0px; 
                font-size: {f(18)}px;
            }}
        """)
        self.table_view.setHorizontalHeader(header)
        header.setStretchLastSection(False)  # 마지막 열 늘리지 않음
        self.table_view.verticalHeader().setVisible(False)  # 행 번호 숨김

        # 다중 필터 프록시 모델 설정
        self.proxy_model = MultiFilterProxy(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)

        source_model = PandasModel()
        source_model.dataChanged.connect(self.on_data_changed)
        self.proxy_model.setSourceModel(source_model)

        # 헤더 클릭 이벤트 연결
        header.sectionClicked.connect(self.on_header_clicked)

        # 레이아웃에 테이블 뷰 추가
        main_layout.addWidget(self.table_view)

    """
    데이터가 변경되었을 때 호출되는 메서드
    """
    def on_data_changed(self, topLeft, bottomRight) :
        for row in range(topLeft.row(), bottomRight.row() + 1) :
            for col in range(topLeft.column(), bottomRight.column() + 1) :
                source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, col))

                if source_index.isValid() :
                    source_row = source_index.row()
                    source_col = source_index.column()

                    value = self.proxy_model.sourceModel().data(source_index, Qt.DisplayRole)

                    self.edited_cells[(source_row, source_col)] = value

        self.data_changed.emit()

    """
    필터 업데이트 (체크박스 상태 변경시 호출)
    """
    def _update_filter(self, col, value, checked):
        current = set(self.proxy_model.filters.get(col, []))
        if checked:
            current.add(value)
        else:
            current.discard(value)
        self.proxy_model.filters[col] = list(current)
        self.proxy_model.invalidateFilter()
        self.filter_applied.emit()

    """
    체크박스 위젯 생성
    """
    def create_checkbox_widget(self, val, is_checked, col_index):
        widget = QWidget()
        widget.setStyleSheet("border: none; background-color: transparent;")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(0)

        # 테두리가 없는 체크박스 사용
        checkbox = NoOutlineCheckBox(val)
        checkbox.setChecked(is_checked)
        checkbox.toggled.connect(
            lambda checked, v=val, c=col_index: self._update_filter(c, v, checked)
        )

        layout.addWidget(checkbox)
        return widget

    """
    헤더 클릭 시 필터 메뉴 표시
    """
    def on_header_clicked(self, logicalIndex):
        # 현재 컬럼의 고유 값 가져오기
        col_name = self._df.columns[logicalIndex]
        raw = self._df[col_name].dropna().tolist()

        # 숫자인 경우 숫자 정렬로 처리, 아닌 경우 문자열 정렬
        try:
            nums = sorted({float(v) for v in raw})
            vals = [str(int(n)) if n.is_integer() else str(n) for n in nums]
        except ValueError:
            vals = sorted(set(raw), key=lambda x: str(x))

        # 커스텀 메뉴 생성 (구분선 없는 스타일)
        menu = CustomMenu(self)
        header = self.table_view.horizontalHeader()
        width = header.sectionSize(logicalIndex)
        menu.setFixedWidth(max(width, 200))  # 최소 너비 설정

        # 최대 높이 설정 (화면 높이의 절반으로 제한)
        screen_height = self.screen().size().height()
        max_menu_height = int(screen_height * 0.5)  # 화면 높이의 50%로 제한

        # 스크롤 영역 생성
        if len(vals) > 10:
            container = QWidget()
            container.setStyleSheet(" background-color: transparent;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)

            # 현재 선택된 필터 항목 가져오기
            current = set(self.proxy_model.filters.get(logicalIndex, []))

            # 체크박스 추가
            for v in vals:
                checkbox_widget = self.create_checkbox_widget(v, v in current, logicalIndex)
                container_layout.addWidget(checkbox_widget)

            # 스크롤 영역 설정
            scroll_area = QScrollArea()
            scroll_area.setStyleSheet("background-color: transparent;")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setMaximumHeight(max_menu_height)
            scroll_area.setWidget(container)

            # 메뉴에 스크롤 영역 추가
            scroll_action = QWidgetAction(menu)
            scroll_action.setDefaultWidget(scroll_area)
            menu.addAction(scroll_action)
        else:
            # 아이템이 적은 경우 스크롤 없이 직접 메뉴에 추가
            current = set(self.proxy_model.filters.get(logicalIndex, []))
            for v in vals:
                act = QWidgetAction(menu)
                # 테두리가 없는 체크박스 위젯 사용
                cb_widget = self.create_checkbox_widget(v, v in current, logicalIndex)
                act.setDefaultWidget(cb_widget)
                menu.addAction(act)

        # 정렬 옵션 추가
        menu.addSeparator()
        asc = menu.addAction("Ascending")
        desc = menu.addAction("Descending")

        # 메뉴 표시 위치 계산
        pos = header.mapToGlobal(
            QPoint(header.sectionViewportPosition(logicalIndex), header.height())
        )

        # 메뉴 실행 및 선택 처리
        sel = menu.exec(pos)
        if sel == asc:
            self.proxy_model.sort(logicalIndex, Qt.AscendingOrder)
        elif sel == desc:
            self.proxy_model.sort(logicalIndex, Qt.DescendingOrder)

    """
    데이터프레임 설정
    """
    def set_data(self, df):
        self._df = df.copy()
        self._original_df = df.copy()
        self.edited_cells = {}

        model = PandasModel(self._df, self)
        model.dataChanged.connect(self.on_data_changed)

        self.proxy_model.filters.clear()
        self.proxy_model.setSourceModel(model)

        # 사용자가 열 너비를 조정할 수 있도록 Interactive 모드 설정
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # 마지막 열이 남은 공간을 채우지 않도록 설정
        self.table_view.horizontalHeader().setStretchLastSection(False)

        # 위젯이 화면에 표시된 후에 열 너비 균등하게 조정 (100ms 지연)
        column_count = len(df.columns)
        QTimer.singleShot(100, lambda: self._adjust_column_widths_evenly())

        self.filter_applied.emit()

    """
    테이블 뷰의 열 너비를 균등하게 조정
    """
    def _adjust_column_widths_evenly(self):
        if self._df.empty:
            return

        total_width = self.table_view.viewport().width()
        column_count = len(self._df.columns)

        if column_count > 0:
            column_width = total_width // column_count
            for i in range(column_count):
                self.table_view.setColumnWidth(i, column_width)

    """
    필터 초기화
    """
    def reset_filter(self):
        self.proxy_model.filters.clear()
        self.proxy_model.invalidateFilter()
        self.filter_applied.emit()

    """
    QTableWidget을 DataFrame으로 변환
    """
    def convert_table_to_dataframe(self, table_widget):
        rows = table_widget.rowCount()
        cols = table_widget.columnCount()

        # 컬럼명 추출
        headers = []
        for col in range(cols):
            item = table_widget.horizontalHeaderItem(col)
            headers.append(item.text() if item else f"Column {col}")

        # 데이터 추출
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = table_widget.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # DataFrame 생성
        return pd.DataFrame(data, columns=headers)

    """
    필터링된 데이터를 DataFrame으로 반환
    """
    def get_filtered_data(self):
        result_df = self._original_df.copy()

        for (row, col), value in self.edited_cells.items() :
            try :
                if pd.api.types.is_numeric_dtype(result_df.iloc[:, col].dtype) :
                    try :
                        if value.strip() == '' :
                            result_df.iloc[row, col] = np.nan
                        else :
                            if '.' in value :
                                result_df.iloc[row, col] = float(value)
                            else :
                                result_df.iloc[row, col] = int(value)
                    except ValueError :
                        result_df.iloc[row, col] = value
                else :
                    result_df.iloc[row, col] = value
            except (IndexError, ValueError) as e :
                print(f"데이터 업데이트 오류: ({row}, {col}) -> {value}, 에러: {e}")
        
        return result_df