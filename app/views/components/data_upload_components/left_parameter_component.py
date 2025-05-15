from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush, QCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QTabWidget, QPushButton, QSizePolicy, QHBoxLayout,
    QFrame, QHeaderView, QSplitter
)
from app.resources.fonts.font_manager import font_manager
from app.resources.styles.result_style import ResultStyles
from app.utils.error_handler import (
    error_handler, safe_operation,
    DataError, ValidationError
)
from app.models.common.screen_manager import *

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
    def _initialize_all_tabs(self):
        for metric in self.metrics:
            if metric in self.pages:
                page = self.pages[metric]
                table = page['table']
                table.clear()
                table.setColumnCount(0)
                page['summary_label'].setText('No analysis data')

    """
    UI 요소 초기화 및 배치
    """

    @error_handler(
        show_dialog=False,
        default_return=None
    )
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 전체 컨테이너에 스타일 적용
        self.setStyleSheet("background-color: white; border: none;")

        self.tab_buttons = []
        self.metrics = [
            "Production Capacity",
            "Materials",
            "Current Shipment",
            "Plan Retention",
        ]

        # 버튼 영역을 위한 프레임
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #F5F5F5;
                border: none;
                border-bottom: {s(1)}px solid #E0E0E0;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
        """)

        button_group_layout = QHBoxLayout(button_frame)
        button_group_layout.setSpacing(s(2))
        button_group_layout.setContentsMargins(m(10), m(8), m(10), m(8))

        for i, btn_text in enumerate(self.metrics):
            btn = QPushButton(btn_text)
            btn_font = font_manager.get_font("SamsungOne-700", fs(11))  # 폰트 크기 9로 축소
            btn_font.setBold(True)
            btn.setFont(btn_font)
            btn.setCursor(QCursor(Qt.PointingHandCursor))

            btn.setMinimumWidth(w(80))  # 최소 너비 80px

            # 버튼 스타일 업데이트
            if i == 0:
                btn.setStyleSheet("""
                            QPushButton {
                                background-color: #1428A0;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                padding: 4px 8px;
                                min-height: 26px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #0F1F8A;
                            }
                        """)
            else:
                btn.setStyleSheet("""
                            QPushButton {
                                background-color: white;
                                color: #666666;
                                border: 1px solid #E0E0E0;
                                border-radius: 5px;
                                padding: 4px 8px;
                                min-height: 26px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #F5F5F5;
                                color: #1428A0;
                                border-color: #1428A0;
                            }
                        """)

            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Fixed로 변경
            button_group_layout.addWidget(btn)
            self.tab_buttons.append(btn)

        layout.addWidget(button_frame)

        # 컨텐츠 영역
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().hide()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
        """)

        for metric in self.metrics:
            try:
                page = QWidget()
                page_layout = QVBoxLayout(page)
                page_layout.setContentsMargins(0, 0, 0, 0)
                page_layout.setSpacing(0)

                # 가로 분할기 생성
                horizontal_splitter = QSplitter(Qt.Horizontal)
                horizontal_splitter.setHandleWidth(5)
                horizontal_splitter.setStyleSheet("""
                    QSplitter::handle {
                        background-color: white;
                        border-radius: 2px;
                    }
                    QSplitter::handle:hover {
                        background-color: #1428A0;
                    }
                """)

                # 왼쪽: 테이블 컨테이너
                table_container = QFrame()
                table_container.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #E0E0E0;
                        border-radius: 8px;
                    }
                """)
                table_layout = QVBoxLayout(table_container)
                table_layout.setContentsMargins(0, 0, 0, 0)

                table = QTreeWidget()
                table.setRootIsDecorated(False)
                table.setSortingEnabled(True)
                table.setHeaderHidden(True)
                table.setStyleSheet(f"""
                    QTreeWidget {{ 
                        border: none; 
                        outline: none;
                        background-color: white;
                        border-radius: 8px;
                        font-family: {font_manager.get_just_font("SamsungOne-700").family()};
                        font-size: {fs(18)}px;
                    }}
                    QTreeWidget::item {{
                        padding: 6px;
                        border-bottom: 1px solid #F5F5F5;
                    }}
                    QTreeWidget::item:selected {{
                        background-color: #E8ECFF;
                        color: black;
                    }}
                    QTreeWidget::item:hover {{
                        background-color: #F5F7FF;
                    }}
                    QHeaderView::section {{ 
                        background-color: #F5F5F5;
                        color: #333333;
                        border: none;
                        padding: 8px;
                        font-weight: bold;
                        border-bottom: 2px solid #E0E0E0;
                    }}
                    QScrollBar:vertical {{
                        border: none;
                        width: 10px;
                        margin: 0px;
                    }}
                    QScrollBar::handle:vertical {{
                        background: #CCCCCC;
                        min-height: 20px;
                        border-radius: 5px;
                    }}
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                        border: none;
                        background: none;
                        height: 0px;
                    }}
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                        background: none;
                    }}
                    QScrollBar:horizontal {{
                        border: none;
                        height: 10px;
                        margin: 0px;
                    }}
                    QScrollBar::handle:horizontal {{
                        background: #CCCCCC;
                        min-width: 20px;
                        border-radius: 5px;
                    }}
                    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                        border: none;
                        background: none;
                        width: 0px;
                    }}
                    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                        background: none;
                    }}
                """ )

                table_layout.addWidget(table)

                # 오른쪽: Summary 레이블 컨테이너
                summary_container = QFrame()
                summary_container.setStyleSheet("""
                    QFrame {
                        background-color: #F8F9FA;
                        border: 1px solid #E0E0E0;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                summary_layout = QVBoxLayout(summary_container)
                summary_layout.setContentsMargins(15, 15, 15, 15)

                summary_label = QLabel("Analysis Summary")
                summary_label.setStyleSheet("""
                    QLabel {
                        color: #333333;
                        font-size: 14px;
                        line-height: 1.5;
                        background-color: transparent;
                        border: none;
                    }
                """)
                summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                summary_label.setWordWrap(True)

                summary_font = font_manager.get_font("SamsungOne-700", 12)
                summary_font.setBold(True)
                summary_label.setFont(summary_font)

                summary_layout.addWidget(summary_label)

                # 스플리터에 위젯 추가 (왼쪽: 테이블, 오른쪽: 써머리)
                horizontal_splitter.addWidget(table_container)
                horizontal_splitter.addWidget(summary_container)

                # 초기 비율 설정 (7:3)
                horizontal_splitter.setSizes([800, 200])

                # 페이지 레이아웃에 스플리터 추가
                page_layout.addWidget(horizontal_splitter)

                self.tab_widget.addTab(page, metric)

                self.pages[metric] = {
                    "table": table,
                    "summary_label": summary_label,
                    "splitter": horizontal_splitter
                }

            except Exception as e:
                raise ValidationError(f'Failed to set up UI for metric \'{metric}\' : {str(e)}')

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        content_layout.addWidget(self.tab_widget)
        layout.addWidget(content_frame)

    """
    프로젝트 분석 데이터 설정
    """

    @error_handler(
        default_return=None
    )
    def set_project_analysis_data(self, data_dict):
        if not isinstance(data_dict, dict):
            raise DataError('Analysis data must be a dictionary', {'type': type(data_dict)})

        self.all_project_analysis_data = data_dict

        if not self.metrics or len(self.metrics) == 0:
            raise ValidationError('No metrics defined')

        safe_operation(
            self._update_tab_content,
            'Error updating first tab content',
            self.metrics[0]
        )

    """
    탭을 변경할 때 호출
    """

    @error_handler(
        default_return=None
    )
    def _on_tab_changed(self, index):
        if index < 0 or index >= len(self.metrics):
            raise IndexError(f'Invalid tab index : {index}')

        metric = self.metrics[index]

        safe_operation(
            self._update_tab_content,
            f'Error updating {metric} tab content',
            metric
        )

    """
    탭 내용 업데이트
    """

    @error_handler(
        default_return=None
    )
    def _update_tab_content(self, metric):
        data = self.all_project_analysis_data.get(metric)
        page_widgets = self.pages.get(metric)

        if data is None or page_widgets is None:
            if page_widgets:
                table = page_widgets['table']
                safe_operation(table.clear, 'Error clearing table')
                safe_operation(table.setColumnCount, 'Error setting column count', 0)
                safe_operation(table.setHeaderHidden, 'Error hiding header', True)

                page_widgets["summary_label"].setText("analysis summary")
            return

        display_df = data.get('display_df')
        summary = data.get('summary')

        table = page_widgets["table"]
        safe_operation(table.clear, 'Error clearing table')

        if display_df is None or (hasattr(display_df, 'empty') and display_df.empty):
            safe_operation(table.setColumnCount, 'Error setting column count', 0)
            safe_operation(table.setHeaderHidden, 'Error hiding header', True)
            page_widgets['summary_label'].setText('No analysis data')
            return

        safe_operation(table.setHeaderHidden, 'Error setting header visibility', False)

        # 표 헤더 설정
        try:
            if display_df is None or display_df.empty:
                table.setColumnCount(0)
            else:
                if metric == 'Production Capacity':
                    headers = ["PJT Group", "PJT", "MFG", "SOP", "CAPA", "MFG/CAPA", "SOP/CAPA"]
                elif metric == 'Materials':
                    headers = list(display_df.columns)
                elif metric == 'Current Shipment':
                    headers = ["Category", "Name", "SOP", "Production", "Fulfillment Rate", "Status"]
                else:
                    headers = list(display_df.columns) if hasattr(display_df, 'columns') else []

                table.setColumnCount(len(headers))
                table.setHeaderLabels(headers)

                # 헤더의 열 너비를 균등하게 분배
                header = table.header()
                header.setSectionResizeMode(QHeaderView.Stretch)

                red_brush = QBrush(QColor('#e74c3c'))
                yellow_brush = QBrush(QColor('#f39c12'))
                green_brush = QBrush(QColor('#2ecc71'))
                bold_font = QFont()
                bold_font.setBold(True)

                for _, row in display_df.iterrows():
                    row_data = []

                    for col in headers:
                        val = row.get(col, '')

                        if isinstance(val, (int, float)):
                            row_data.append(f'{val :,.0f}')
                        else:
                            row_data.append(str(val))

                    item = QTreeWidgetItem(row_data)

                    # 탭에 따른 표시 그래프(표) 내용 설정
                    try:
                        if metric == "Production Capacity":
                            if str(row.get('PJT', '')) == 'Total':
                                for col in range(len(headers)):
                                    item.setFont(col, bold_font)
                                if row.get('status', '') == 'Error':
                                    for col in range(len(headers)):
                                        item.setForeground(col, red_brush)
                        elif metric == 'Materials':
                            if 'Shortage Amount' in headers:
                                shortage_col = headers.index('Shortage Amount')

                                try:
                                    shortage_amount = float(row.get('Shortage Amount', 0))

                                    if shortage_amount > 0:
                                        for col in range(len(headers)):
                                            item.setForeground(col, red_brush)
                                except (ValueError, TypeError):
                                    pass
                        elif metric == 'Current Shipment':
                            status = row.get('Status', '')
                            category = row.get('Category', '')

                            if category == 'Total':
                                for col in range(len(headers)):
                                    item.setFont(col, bold_font)

                            if status == 'Error':
                                for col in range(len(headers)):
                                    item.setForeground(col, red_brush)
                            elif status == 'Warning':
                                for col in range(len(headers)):
                                    item.setForeground(col, yellow_brush)
                            elif status == 'OK':
                                for col in range(len(headers)):
                                    item.setForeground(col, green_brush)
                    except Exception as style_error:
                        pass

                    table.addTopLevelItem(item)

        except Exception as e:
            raise DataError(f'Error displaying data : {str(e)}', {'metric': metric})

        summary_label = page_widgets["summary_label"]

        # 표에 들어갈 데이터 출력
        try:
            if summary is not None:
                if metric == 'Production Capacity':
                    text = (
                        f"Total number of groups : {summary.get('Total number of groups', 0)}<br>"
                        f"Number of error groups : {summary.get('Number of error groups', 0)}<br>"
                        f"Total MFG : {summary.get('Total MFG', 0):,}<br>"
                        f"Total SOP : {summary.get('Total SOP', 0):,}<br>"
                        f"Total CAPA : {summary.get('Total CAPA', 0):,}<br>"
                        f"Total MFG/CAPA ratio : {summary.get('Total MFG/CAPA ratio', '0%')}<br>"
                        f"Total SOP/CAPA ratio : {summary.get('Total SOP/CAPA ratio', '0%')}"
                    )
                elif metric == 'Materials':
                    text = (
                        f"Total materials: {summary.get('Total materials', 0)}<br>"
                        f"Weekly shortage materials: {summary.get('Weekly shortage materials', 0)}<br>"
                        f"Full period shortage materials: {summary.get('Full period shortage materials', 0)}<br>"
                        f"Shortage rate: {summary.get('Shortage rate (%)', 0)}%<br>"
                        f"Period: {summary.get('Period', 'N/A')}<br>"
                    )
                elif metric == 'Current Shipment':
                    text = (
                        f"Overall fulfillment rate: {summary.get('Overall fulfillment rate', '0%')}<br>"
                        f"Total demand (SOP): {summary.get('Total demand(SOP)', 0):,}<br>"
                        f"Total production: {summary.get('Total production', 0):,}<br>"
                        f"Project count: {summary.get('Project count', 0)}<br>"
                        f"Site count: {summary.get('Site count', 0)}<br>"
                        f"Bottleneck items: {summary.get('Bottleneck items', 0)}"
                    )
                else:
                    text = 'Analysis summary'

                summary_label.setText(text)
            else:
                summary_label.setText("Analysis summary")
        except Exception as summary_error:
            summary_label.setText('Error displaying summary')

    """
    선택된 탭 새로고침
    """

    def refresh_current_tab(self):
        current_index = self.tab_widget.currentIndex()

        if 0 <= current_index < len(self.metrics):
            metric = self.metrics[current_index]
            self._update_tab_content(metric)

    def switch_tab(self, index):
        """
        index 번째 탭으로 전환
        """
        for i, btn in enumerate(self.tab_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1428A0;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 4px 8px;
                        min-height: 26px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0F1F8A;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #666666;
                        border: 1px solid #E0E0E0;
                        border-radius: 5px;
                        padding: 4px 8px;
                        min-height: 26px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #F5F5F5;
                        color: #1428A0;
                        border-color: #1428A0;
                    }
                """)
        self.tab_widget.setCurrentIndex(index)
        self._on_tab_changed(index)