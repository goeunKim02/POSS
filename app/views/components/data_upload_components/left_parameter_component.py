from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QTabWidget
)
from app.utils.error_handler import error_handler, safe_operation

"""
좌측 파라미터 영역에 프로젝트 분석 결과 표시
"""
class LeftParameterComponent(QWidget):
    def __init__(self):
        super().__init__()

        self.all_project_analysis_data = {}
        self.pages = {}
        self._init_ui()

        self._initialize_all_tabs()

    """
    모든 탭의 컨텐츠 초기화
    """
    @error_handler(
        show_dialog=False,
        default_return=None
    )
    def _initialize_all_tabs(self) :
        for metric in self.metrics :
            if metric in self.pages :
                page = self.pages[metric]
                table = page['table']
                table.clear()
                table.setColumnCount(0)
                page['summary_label'].setText('No analysis data')

    @error_handler(
        show_dialog=False,
        default_return=None
    )
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.metrics = [
            "Production Capacity",
            "Materials",
            "Current Shipment"
        ]
        for metric in self.metrics :
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)

            table = QTreeWidget()
            table.setRootIsDecorated(False)
            table.setSortingEnabled(True)
            table.setHeaderHidden(True)
            table.setStyleSheet(
                "QTreeWidget { border: none; outline: none; }"
                "QTreeView::branch { background: none; }"
                "QTreeView::header { background-color: #1428A0; color: white; font-weight: bold; }"
                "QHeaderView::section { background-color: #1428A0; color: white; border: none; padding: 6px; }"
            )

            summary_label = QLabel("analysis summary")
            summary_label.setStyleSheet("font-weight: bold; font-size: 18px;")
            summary_label.setAlignment(Qt.AlignTop)

            page_layout.addWidget(table, 1)
            page_layout.addWidget(summary_label)
            self.tab_widget.addTab(page, metric)

            self.pages[metric] = {"table": table, "summary_label": summary_label}

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_widget)

    def set_project_analysis_data(self, data_dict) :
        self.all_project_analysis_data = data_dict
        self._update_tab_content(self.metrics[0])

    def _on_tab_changed(self, index):
        metric = self.metrics[index]
        self._update_tab_content(metric)

    def _update_tab_content(self, metric) :
        data = self.all_project_analysis_data.get(metric)
        page_widgets = self.pages.get(metric)
        
        if data is None or page_widgets is None :
            if page_widgets :
                table = page_widgets['table']
                table.clear()
                table.setColumnCount(0)
                table.setHeaderHidden(True)
                
                page_widgets["summary_label"].setText("analysis summary")
            return

        display_df = data.get('display_df')
        summary = data.get('summary')

        table = page_widgets["table"]
        table.clear()

        if display_df is None or (hasattr(display_df, 'empty') and display_df.empty) :
            table.setColumnCount(0)
            table.setHeaderHidden(True)
            page_widgets['summary_label'].setText('No analysis data')
            return
        table.setHeaderHidden(False)

        if display_df is None or display_df.empty:
            table.setColumnCount(0)
        else:
            if metric == 'Production Capacity' :
                headers = ["PJT Group", "PJT", "MFG", "SOP", "CAPA", "MFG/CAPA", "SOP/CAPA"]
            elif metric == 'Materials' :
                headers = list(display_df.columns)
            
            table.setColumnCount(len(headers))
            table.setHeaderLabels(headers)

            red_brush = QBrush(QColor('#e74c3c'))
            bold_font = QFont()
            bold_font.setBold(True)

            for _, row in display_df.iterrows():
                row_data = []

                for col in headers :
                    val = row.get(col, '')

                    if isinstance(val, (int, float)) :
                        row_data.append(f'{val :,.0f}')
                    else :
                        row_data.append(str(val))

                item = QTreeWidgetItem(row_data)

                if metric == "Production Capacity":
                    if str(row.get('PJT', '')) == 'Total' :
                        for col in range(len(headers)) :
                            item.setFont(col, bold_font)
                        if row.get('status', '') == 'Error' :
                            for col in range(len(headers)) :
                                item.setForeground(col, red_brush)
                elif metric == 'Materials' :
                    if 'Shortage Amount' in headers :
                        shortage_col = headers.index('Shortage Amount')

                        try :
                            shortage_amount = float(row.get('Shortage Amount', 0))

                            if shortage_amount > 0 :
                                for col in range(len(headers)) :
                                    item.setForeground(col, red_brush)
                        except (ValueError, TypeError) :
                            pass

                table.addTopLevelItem(item)

            for i in range(len(headers)) :
                table.resizeColumnToContents(i)

        summary_label = page_widgets["summary_label"]

        if summary is not None :
            if metric == 'Production Capacity' :
                text = (
                    f"Total number of groups : {summary.get('Total number of groups', 0)}<br>"
                    f"Number of error groups : {summary.get('Number of error groups', 0)}<br>"
                    f"Total MFG : {summary.get('Total MFG', 0):,}<br>"
                    f"Total SOP : {summary.get('Total SOP', 0):,}<br>"
                    f"Total CAPA : {summary.get('Total CAPA', 0):,}<br>"
                    f"Total MFG/CAPA ratio : {summary.get('Total MFG/CAPA ratio', '0%')}<br>"
                    f"Total SOP/CAPA ratio : {summary.get('Total SOP/CAPA ratio', '0%')}"
                )
            elif metric == 'Materials' :
                text = (
                    f"Total materials: {summary.get('Total materials', 0)}<br>"
                    f"Weekly shortage materials: {summary.get('Weekly shortage materials', 0)}<br>"
                    f"Full period shortage materials: {summary.get('Full period shortage materials', 0)}<br>"
                    f"Shortage rate: {summary.get('Shortage rate (%)', 0)}%<br>"
                    f"Period: {summary.get('Period', 'N/A')}<br>"
                )
                
            summary_label.setText(text)
        else:
            summary_label.setText("Analysis summary")
