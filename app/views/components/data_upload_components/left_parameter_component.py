from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush, QCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QTabWidget, QPushButton, QSizePolicy, QHBoxLayout
)
from app.resources.fonts.font_manager import font_manager
from app.resources.styles.result_style import ResultStyles
from app.utils.error_handler import (
    error_handler, safe_operation,
    DataError, ValidationError
)

"""
좌측 파라미터 영역에 프로젝트 분석 결과 표시
"""
class LeftParameterComponent(QWidget):

    """
    클래스 초기화
    """
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
        self.tab_buttons = []
        self.metrics = [
            "Production Capacity",
            "Materials",
            "Current Shipment",
            "Preallocation",
            "Plan Retention",
            "Shipment Capacity"
        ]

        # 지표 버튼
        button_group_layout = QHBoxLayout()
        button_group_layout.setSpacing(5)
        button_group_layout.setContentsMargins(10, 10, 10, 5)

        # 버튼들 사이 균등 간격 설정 (필요시)
        button_group_layout.setAlignment(Qt.AlignCenter)  # 중앙 정렬

        for i, btn_text in enumerate(self.metrics) :
            btn = QPushButton(btn_text)
            btn.setFont(font_manager.get_font("SamsungOne-700", 14))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE if i == 0 else ResultStyles.INACTIVE_BUTTON_STYLE)
            btn.clicked.connect(lambda checked, idx=i :self.switch_tab(idx))

             # 균등한 크기로 설정
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFixedHeight(40)  # 높이만 고정

            button_group_layout.addWidget(btn)
            self.tab_buttons.append(btn)
            # 버튼 스타일 업데이트
          
        layout.addLayout(button_group_layout)


        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().hide()
        for metric in self.metrics :
            try :
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
            except Exception as e :
                raise ValidationError(f'Failed to set up UI for metric \'{metric}\' : {str(e)}')

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_widget)

    """
    프로젝트 분석 데이터 설정
    """
    @error_handler(
            default_return=None
    )
    def set_project_analysis_data(self, data_dict) :
        if not isinstance(data_dict, dict) :
            raise DataError('Analysis data must be a dictionary', {'type' : type(data_dict)})

        self.all_project_analysis_data = data_dict

        if not self.metrics or len(self.metrics) == 0 :
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
    def _on_tab_changed(self, index) :
        if index < 0 or index >= len(self.metrics) :
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
    def _update_tab_content(self, metric) :
        data = self.all_project_analysis_data.get(metric)
        page_widgets = self.pages.get(metric)
        
        if data is None or page_widgets is None :
            if page_widgets :
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

        if display_df is None or (hasattr(display_df, 'empty') and display_df.empty) :
            safe_operation(table.setColumnCount, 'Error setting column count', 0)
            safe_operation(table.setHeaderHidden, 'Error hiding header', True)
            page_widgets['summary_label'].setText('No analysis data')
            return
        
        safe_operation(table.setHeaderHidden, 'Error setting header visibility', False)

        # 표 헤더 설정
        try :
            if display_df is None or display_df.empty:
                table.setColumnCount(0)
            else:
                if metric == 'Production Capacity' :
                    headers = ["PJT Group", "PJT", "MFG", "SOP", "CAPA", "MFG/CAPA", "SOP/CAPA"]
                elif metric == 'Materials' :
                    headers = list(display_df.columns)
                elif metric == 'Current Shipment' :
                    headers = ["Category", "Name", "SOP", "Production", "Fulfillment Rate", "Status"]
                else :
                    headers = list(display_df.columns) if hasattr(display_df, 'columns') else []
                
                table.setColumnCount(len(headers))
                table.setHeaderLabels(headers)

                red_brush = QBrush(QColor('#e74c3c'))
                yellow_brush = QBrush(QColor('#f39c12'))
                green_brush = QBrush(QColor('#2ecc71'))
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

                    # 탭에 따른 표시 그래프(표) 내용 설정
                    try :
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
                        elif metric == 'Current Shipment' :
                            status = row.get('Status', '')
                            category = row.get('Category', '')

                            if category == 'Total' :
                                for col in range(len(headers)) :
                                    item.setFont(col, bold_font)
                            
                            if status == 'Error' :
                                for col in range(len(headers)) :
                                    item.setForeground(col, red_brush)
                            elif status == 'Warning' :
                                for col in range(len(headers)) :
                                    item.setForeground(col, yellow_brush)
                            elif status == 'OK' :
                                for col in range(len(headers)) :
                                    item.setForeground(col, green_brush)
                    except Exception as style_error :
                        pass

                    table.addTopLevelItem(item)

                for i in range(len(headers)) :
                    safe_operation(
                        table.resizeColumnToContents,
                        f'Error resizing column {i}',
                        i
                    )
        except Exception as e :
            raise DataError(f'Error displaying data : {str(e)}', {'metric' : metric})

        summary_label = page_widgets["summary_label"]

        # 표에 들어갈 데이터 출력
        try :
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
                elif metric == 'Current Shipment' :
                    text = (
                        f"Overall fulfillment rate: {summary.get('Overall fulfillment rate', '0%')}<br>"
                        f"Total demand (SOP): {summary.get('Total demand(SOP)', 0):,}<br>"
                        f"Total production: {summary.get('Total production', 0):,}<br>"
                        f"Project count: {summary.get('Project count', 0)}<br>"
                        f"Site count: {summary.get('Site count', 0)}<br>"
                        f"Bottleneck items: {summary.get('Bottleneck items', 0)}"
                    )
                else :
                    text = 'Analysis summary'
                    
                summary_label.setText(text)
            else:
                summary_label.setText("Analysis summary")
        except Exception as summary_error :
            summary_label.setText('Error displaying summary')

    """
    선택된 탭 새로고침
    """
    def refresh_current_tab(self) :
        current_index = self.tab_widget.currentIndex()

        if 0 <= current_index < len(self.metrics) :
            metric = self.metrics[current_index]
            self._update_tab_content(metric)


    def switch_tab(self, index):
        """
        index 번째 탭으로 전환
        """
        for i, btn in enumerate(self.tab_buttons):
            btn.setStyleSheet(ResultStyles.ACTIVE_BUTTON_STYLE if i == index else ResultStyles.INACTIVE_BUTTON_STYLE)
        self.tab_widget.setCurrentIndex(index)
        self._on_tab_changed(index)