from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QFrame, QTabWidget
)

"""
좌측 파라미터 영역에 프로젝트 분석 결과 표시
"""
class LeftParameterComponent(QWidget):
    def __init__(self):
        super().__init__()
        # 메트릭별 분석 데이터를 저장할 딕셔너리
        self.all_project_analysis_data = {}
        # 각 탭 페이지 위젯 참조를 저장
        self.pages = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 탭 위젯: 메트릭 선택용
        self.tab_widget = QTabWidget()
        # 필요한 세 개의 탭만 설정
        self.metrics = [
            "Production Capacity",
            "Materials",
            "Current Shipment"
        ]
        for metric in self.metrics:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)

            # 테이블
            table = QTreeWidget()
            table.setRootIsDecorated(False)
            table.setSortingEnabled(True)
            table.setStyleSheet(
                "QTreeWidget { border: none; outline: none; }"
                "QTreeView::branch { background: none; }"
                "QTreeView::header { background-color: #1428A0; color: white; font-weight: bold; }"
                "QHeaderView::section { background-color: #1428A0; color: white; border: none; padding: 6px; }"
            )

            # 요약 레이블
            summary_label = QLabel("분석 요약")
            summary_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            summary_label.setAlignment(Qt.AlignTop)

            page_layout.addWidget(table, 1)
            page_layout.addWidget(summary_label)
            self.tab_widget.addTab(page, metric)

            # 페이지 참조 저장
            self.pages[metric] = {"table": table, "summary_label": summary_label}

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_widget)

    def set_project_analysis_data(self, data_dict):
        # 모든 메트릭 데이터 저장
        self.all_project_analysis_data = data_dict
        # 첫 번째 메트릭 데이터로 초기 표시
        self._update_tab_content(self.metrics[0])

    def _on_tab_changed(self, index):
        metric = self.metrics[index]
        self._update_tab_content(metric)

    def _update_tab_content(self, metric):
        data = self.all_project_analysis_data.get(metric)
        page_widgets = self.pages.get(metric)
        # 페이지 혹은 데이터가 없으면 초기화 표시
        if data is None or page_widgets is None:
            if page_widgets:
                page_widgets["table"].clear()
                page_widgets["summary_label"].setText("분석 요약")
            return

        display_df = data.get('display_df')
        summary = data.get('summary')

        # 테이블 업데이트
        table = page_widgets["table"]
        table.clear()
        if display_df is None or display_df.empty:
            table.setColumnCount(0)
        else:
            headers = ["PJT Group", "PJT", "MFG", "SOP", "CAPA", "MFG/CAPA", "SOP/CAPA"]
            if 'status' in display_df.columns:
                headers.append('Status')
            table.setColumnCount(len(headers))
            table.setHeaderLabels(headers)

            red_brush = QBrush(QColor('#e74c3c'))
            bold_font = QFont()
            bold_font.setBold(True)

            for _, row in display_df.iterrows():
                row_data = [str(row.get(col, '')) for col in headers]
                item = QTreeWidgetItem(row_data)
                if str(row.get('PJT', '')) == 'Total':
                    for col in range(len(headers)):
                        item.setFont(col, bold_font)
                    if row.get('status', '') == '이상':
                        for col in range(len(headers)):
                            item.setForeground(col, red_brush)
                table.addTopLevelItem(item)

            for i in range(len(headers)):
                table.resizeColumnToContents(i)

        # 요약 업데이트
        summary_label = page_widgets["summary_label"]
        # summary 객체가 None이 아닌지 명시적으로 확인하여 오류 방지
        if summary is not None:
            text = (
                f"<b>분석 요약:</b><br>"
                f"총 그룹 수: {summary.get('총 그룹 수', 0)}<br>"
                f"이상 그룹 수: {summary.get('이상 그룹 수', 0)}<br>"
                f"전체 MFG: {summary.get('전체 MFG', 0):,}<br>"
                f"전체 SOP: {summary.get('전체 SOP', 0):,}<br>"
                f"전체 CAPA: {summary.get('전체 CAPA', 0):,}<br>"
                f"전체 MFG/CAPA 비율: {summary.get('전체 MFG/CAPA 비율', '0%')}<br>"
                f"전체 SOP/CAPA 비율: {summary.get('전체 SOP/CAPA 비율', '0%')}"
            )
            summary_label.setText(text)
        else:
            summary_label.setText("분석 요약")
