import os
import pandas as pd
from PyQt5.QtGui import QFont, QCursor, QPainter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTableView, QMenu, QWidgetAction,
    QCheckBox, QFileDialog, QMessageBox, QHeaderView, QStyle
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QAbstractTableModel, QStandardPaths,
    QModelIndex, QVariant, QSortFilterProxyModel, QPoint
)

from .pre_assigned_components.style import (
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE
)

class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._df = df

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

class FilterHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)

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

def create_button(text, style="primary", parent=None):
    btn = QPushButton(text, parent)
    font = QFont("Arial", 9)
    font.setBold(True)
    btn.setFont(font)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setFixedSize(150, 50)
    btn.setStyleSheet(
        PRIMARY_BUTTON_STYLE if style == "primary" else SECONDARY_BUTTON_STYLE
    )
    return btn

class PlanningPage(QWidget):
    optimization_requested = pyqtSignal(dict)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._df = pd.DataFrame()
        self.default_column_widths = {2: 240, 3: 240}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # 상단 제목 및 버튼
        title_hbox = QHBoxLayout()
        lbl = QLabel("Pre-Assigned Result")
        font_title = QFont("Arial", 15)
        font_title.setBold(True)
        lbl.setFont(font_title)
        title_hbox.addWidget(lbl)
        title_hbox.addStretch()
        btn_export = create_button("Export Excel", "primary", self)
        btn_export.clicked.connect(self.on_export_click)
        btn_reset = create_button("Reset", "secondary", self)
        btn_reset.clicked.connect(self.on_reset_click)
        title_hbox.addWidget(btn_export)
        title_hbox.addWidget(btn_reset)
        layout.addLayout(title_hbox)

        # 테이블 뷰 + 필터 프록시
        self.table_view = QTableView(self)
        self.table_view.setAlternatingRowColors(True)
        # 사용자 정의 헤더 설정
        header = FilterHeader(Qt.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(False)

        self.proxy_model = MultiFilterProxy(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)
        header.sectionClicked.connect(self.on_header_clicked)
        layout.addWidget(self.table_view, 1)


    def _update_filter(self, col, value, checked):
        current = set(self.proxy_model.filters.get(col, []))
        if checked:
            current.add(value)
        else:
            current.discard(value)
        self.proxy_model.filters[col] = list(current)
        self.proxy_model.invalidateFilter()

    def on_header_clicked(self, logicalIndex):
        col_name = self._df.columns[logicalIndex]
        raw = self._df[col_name].dropna().tolist()
        try:
            nums = sorted({float(v) for v in raw})
            vals = [str(int(n)) if n.is_integer() else str(n) for n in nums]
        except ValueError:
            vals = sorted(set(raw), key=lambda x: str(x))

        menu = QMenu(self)
        header = self.table_view.horizontalHeader()
        width = header.sectionSize(logicalIndex)
        menu.setFixedWidth(width)

        # 체크박스 추가
        current = set(self.proxy_model.filters.get(logicalIndex, []))
        for v in vals:
            act = QWidgetAction(menu)
            cb = QCheckBox(v, menu)
            cb.setChecked(v in current)
            cb.toggled.connect(lambda checked, val=v, col=logicalIndex: self._update_filter(col, val, checked))
            act.setDefaultWidget(cb)
            menu.addAction(act)

        menu.addSeparator()
        asc = menu.addAction("Ascending")
        desc = menu.addAction("Descending")

        pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(logicalIndex), header.height()))
        sel = menu.exec(pos)
        if sel == asc:
            self.proxy_model.sort(logicalIndex, Qt.AscendingOrder)
        elif sel == desc:
            self.proxy_model.sort(logicalIndex, Qt.DescendingOrder)

    def on_export_click(self):
        options = QFileDialog.Options()
        desktop_dir = QStandardPaths.writableLocation(
            QStandardPaths.DesktopLocation
        )
        default_path = os.path.join(desktop_dir, "preassign_result.xlsx")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as Excel",
            default_path,
            "Excel Files (*.xlsx);;All Files (*)",
            options=options
        )
        if not file_path:
            return
        
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'

        try:
            # DataFrame을 엑셀로 저장
            self._df.to_excel(file_path, index=False)
            QMessageBox.information(
                self,
                "Export Success",
                f"파일이 다음 경로로 저장되었습니다:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"엑셀 파일 저장 중 오류가 발생했습니다:\n{e}"
            )
            
    def on_reset_click(self):
        # 데이터 초기화
        self._df = pd.DataFrame()
        model = PandasModel(self._df, self)
        self.proxy_model.filters.clear()
        self.proxy_model.setSourceModel(model)

    def on_optimization_click(self):
        self.optimization_requested.emit({})
        self.main_window.run_optimization()

    def display_preassign_result(self, df: pd.DataFrame):
        # 테이블에 결과 표시
        self._df = df.astype(str)
        model = PandasModel(self._df, self)
        self.proxy_model.filters.clear()
        self.proxy_model.setSourceModel(model)
        for col, width in self.default_column_widths.items():
            if 0 <= col < model.columnCount():
                self.table_view.setColumnWidth(col, width)
