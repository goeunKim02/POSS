from PyQt5.QtGui import QFont, QCursor, QPainter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableView, QHeaderView, QMenu, QWidgetAction,
    QCheckBox, QPushButton, QTableWidgetItem, QScrollArea
)
from PyQt5.QtCore import (
    pyqtSignal, Qt, QAbstractTableModel, QModelIndex,
    QVariant, QSortFilterProxyModel, QPoint, QSize
)
import pandas as pd


class FilterHeader(QHeaderView):
    """헤더 필터링을 위한 사용자 정의 헤더"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)  # 헤더 클릭 가능하게 설정

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        # 필터 아이콘이나 추가 표시가 필요한 경우 여기에 구현


class MultiFilterProxy(QSortFilterProxyModel):
    """다중 필터 프록시 모델"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 컬럼 인덱스 -> 선택된 값 리스트
        self.filters = {}

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if not self.filters:
            return True

        model = self.sourceModel()
        for col, vals in self.filters.items():
            if not vals:  # 필터 값이 없으면 모든 행 표시
                continue

            cell = model.data(model.index(sourceRow, col), Qt.DisplayRole)
            if cell not in vals:
                return False

        return True

    def sort(self, column, order=Qt.AscendingOrder):
        super().sort(column, order)


class PandasModel(QAbstractTableModel):
    """pandas DataFrame을 위한 테이블 모델"""

    def __init__(self, df=None, parent=None):
        super().__init__(parent)
        self._df = pd.DataFrame() if df is None else df

    def rowCount(self, parent=QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()
        return str(self._df.iat[index.row(), index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._df.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._df.index[section])
        return QVariant()


class CustomMenu(QMenu):
    """커스텀 메뉴 클래스 - 구분선 없는 스타일 적용"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 구분선을 제거하는 스타일 적용
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
            /* 이 부분이 중요: 체크박스 주변의 선 완전히 제거 */
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


class NoOutlineCheckBox(QCheckBox):
    """테두리가 없는 체크박스"""

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


class EnhancedTableFilterComponent(QWidget):
    """
    향상된 테이블 필터 컴포넌트
    헤더 클릭으로 다중 필터 선택 기능 제공
    """
    filter_applied = pyqtSignal()  # 필터가 적용되었을 때 발생하는 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_view = None
        self.proxy_model = None
        self._df = pd.DataFrame()
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 테이블 뷰 생성
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)

        # 사용자 정의 헤더 설정
        header = FilterHeader(Qt.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(False)  # 행 번호 숨김

        # 다중 필터 프록시 모델 설정
        self.proxy_model = MultiFilterProxy(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)

        # 헤더 클릭 이벤트 연결
        header.sectionClicked.connect(self.on_header_clicked)

        # 레이아웃에 테이블 뷰 추가
        main_layout.addWidget(self.table_view)

        # 버튼 영역
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: white; border: none;")
        button_layout = QHBoxLayout(button_frame)

        # 필터 리셋 버튼
        self.reset_btn = QPushButton("필터 초기화")
        self.reset_btn.setFont(QFont("Arial"))
        self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #808080; 
                color: white; 
                border-radius: 10px;
                padding: 5px 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_filter)

        button_layout.addStretch(1)
        button_layout.addWidget(self.reset_btn)

        main_layout.addWidget(button_frame)

    def _update_filter(self, col, value, checked):
        """필터 업데이트 (체크박스 상태 변경시 호출)"""
        current = set(self.proxy_model.filters.get(col, []))
        if checked:
            current.add(value)
        else:
            current.discard(value)
        self.proxy_model.filters[col] = list(current)
        self.proxy_model.invalidateFilter()
        self.filter_applied.emit()

    def create_checkbox_widget(self, val, is_checked, col_index):
        """체크박스 위젯 생성"""
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

    def on_header_clicked(self, logicalIndex):
        """헤더 클릭 시 필터 메뉴 표시"""
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
        if len(vals) > 10:  # 아이템이 많은 경우에만 스크롤 적용
            # 컨테이너 생성
            container = QWidget()
            container.setStyleSheet(" background-color: transparent;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)  # 간격 없음

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

    def set_data(self, df):
        """데이터프레임 설정"""
        self._df = df.copy()
        model = PandasModel(self._df, self)
        self.proxy_model.filters.clear()
        self.proxy_model.setSourceModel(model)
        self.filter_applied.emit()

    def reset_filter(self):
        """필터 초기화"""
        self.proxy_model.filters.clear()
        self.proxy_model.invalidateFilter()
        self.filter_applied.emit()

    def convert_table_to_dataframe(self, table_widget):
        """QTableWidget을 DataFrame으로 변환"""
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

    def get_filtered_data(self):
        """필터링된 데이터를 DataFrame으로 반환"""
        model = self.proxy_model
        source_model = model.sourceModel()

        # 필터링된 행 인덱스 가져오기
        rows = []
        for row in range(model.rowCount()):
            source_idx = model.mapToSource(model.index(row, 0)).row()
            rows.append(source_idx)

        # 원본 데이터에서 필터링된 행만 선택
        if not rows:
            return pd.DataFrame(columns=self._df.columns)
        return self._df.iloc[rows].copy()