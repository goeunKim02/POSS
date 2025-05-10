from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt

from .open_dynamic_properties_dialog import DynamicPropertiesDialog
from app.models.common.fileStore import FilePaths
from app.models.common.event_bus import EventBus

class ParameterComponent(QWidget):
    show_failures = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.failures = {}
        self.current_metric = 'Production Capacity'
        self._pa_view = 'item'

        self.metric_key_map = {
            'Production Capacity': 'production_capacity',
            'Materials': 'materials',
            'Current Shipment': 'current_shipment',
            'Preassignment': 'preassign',
            'Shippable Quantity': 'shippable_quantity',
            'Plan Adherence Rate': 'plan_adherence_rate',
        }

        self.header_map = {
            'Production Capacity': [
                ('Center', 'center'),
                ('Line', 'line'),
                ('Cap Limit', 'cap_limit'),
                ('Available', 'available'),
                ('Excess', 'excess'),
            ],
            'Materials': [
                ('Material ID', 'material_id'),
                ('Line', 'line'),
                ('Issue', 'reason'),
                ('Stock Avail', 'available'),
                ('Shortage', 'excess'),
            ],
            'Current Shipment': [
                ('Ship ID', 'ship_id'),
                ('Line', 'line'),
                ('Delay Reason', 'reason'),
                ('Can Ship', 'available'),
                ('OverQty', 'excess'),
            ],
            'Preassignment': [
                ('Line', 'line'),
                ('Alloc Reason', 'reason'),
                ('Pending', 'excess'),
            ],
            'Shippable Quantity': [
                ('Ship Date', 'ship_date'),
                ('Line', 'line'),
                ('Shippable', 'available'),
                ('Avail Qty', 'available'),
                ('Excess', 'excess'),
            ],
            'Plan Adherence Rate': {
                'item': [
                    ('Line', 'line'),
                    ('Item', 'item'),
                    ('Prev Qty', 'prev_qty'),
                    ('New Qty', 'new_qty'),
                    ('Maint Qty', 'maintain_qty'),
                    ('Rate', 'maint_rate'),
                ],
                'rmc': [
                    ('Line', 'line'),
                    ('RMC', 'rmc'),
                    ('Prev Qty', 'prev_qty'),
                    ('New Qty', 'new_qty'),
                    ('Maint Qty', 'maintain_qty'),
                    ('Rate', 'maint_rate'),
                ]
            },
        }

        self.dynamic_props_btn = QPushButton("Dynamic 속성 설정")
        self.dynamic_props_btn.setFont(QFont('Arial', 9, QFont.Bold))
        self.dynamic_props_btn.setCursor(Qt.PointingHandCursor)
        self.dynamic_props_btn.setFixedHeight(30)
        self.dynamic_props_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.dynamic_props_btn.clicked.connect(self.open_dynamic_properties_dialog)
        
        self.dynamic_props_btn.setVisible(bool(FilePaths.get("dynamic_excel_file")))

        self.buttons = {}
        self._init_ui()
        self._build_metric_buttons()
        self.failure_table.header().hide()
        self.show_failures.connect(self._on_failures)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.button_bar = QHBoxLayout()
        self.button_bar.setSpacing(8)
        layout.addLayout(self.button_bar)

        self.failure_table = QTreeWidget()
        self.failure_table.setRootIsDecorated(False)
        self.failure_table.setSortingEnabled(True)
        self.failure_table.setStyleSheet("""
            QTreeWidget { border: none; outline: none; }
            QTreeView::branch { background: none; }
            QTreeView::header { background-color: transparent; border: none; }
            QHeaderView::section { background-color: transparent; border: none; padding: 4px; }
        """)
        layout.addWidget(self.failure_table, 1)

    def _build_metric_buttons(self) :
        for i in reversed(range(self.button_bar.count())) :
            w = self.button_bar.takeAt(i).widget()
            if w :
                w.deleteLater()
        self.buttons.clear()

        for label in self.metric_key_map :
            btn = QPushButton(label)
            btn.setFont(QFont('Arial', 9, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, lb=label: self._on_metric_clicked(lb))
            self.button_bar.addWidget(btn)
            self.buttons[label] = btn

        self.button_bar.addStretch()
        self.button_bar.addWidget(self.dynamic_props_btn)
        self._update_button_styles()

    def _on_failures(self, failures: dict) :
        self.failures = failures
        self._build_metric_buttons()

        if failures.get('production_capacity') :
            self.current_metric = 'Production Capacity'
        elif failures.get('plan_adherence_rate') :
            self.current_metric = 'Plan Adherence Rate'
        else:
            for lbl, key in self.metric_key_map.items() :
                if failures.get(key) :
                    self.current_metric = lbl
                    break

        self._populate_for_metric(self.current_metric)

    def _on_metric_clicked(self, label: str) :
        self.current_metric = label

        if label == 'Production Capacity' :
            EventBus.emit('show_project_analysis', True)
        else:
            EventBus.emit('show_project_analysis', False)

        if label == 'Plan Adherence Rate' :
            self._pa_view = 'rmc' if self._pa_view == 'item' else 'item'
        else:
            self.current_metric = label

        self._populate_for_metric(label)
        self._update_button_styles()

    def _populate_for_metric(self, label: str):
        # self.current_metric = label
        key = self.metric_key_map[label]

        if label == 'Plan Adherence Rate':
            pa = self.failures.get('plan_adherence_rate', {})
            data = pa.get(f"{self._pa_view}_failures", [])
            fields = self.header_map[label][self._pa_view]
        else:
            data = self.failures.get(key, []) or []
            fields = self.header_map[label]

        headers = [h for h, _ in fields]
        self.failure_table.clear()
        self.failure_table.setColumnCount(len(headers))
        self.failure_table.setHeaderLabels(headers)
        self.failure_table.header().show()

        red = QBrush(QColor('#e74c3c'))

        if not hasattr(data, '__iter__') or isinstance(data, bool):
            print(f"경고: '{label}'의 데이터는 반복 가능한 객체가 아닙니다. 타입: {type(data)}")
            data = []

        for info in data:
            vals = []
            for _, field in fields:
                if isinstance(info, dict):
                    v = info.get(field, '')
                else:
                    v = getattr(info, field, '')
                vals.append(str(v))

            item = QTreeWidgetItem(vals)
            for col in range(len(vals)):
                item.setForeground(col, red)
            self.failure_table.addTopLevelItem(item)

        self.failure_table.sortItems(0, Qt.AscendingOrder)
        self._update_button_styles()

    def _update_button_styles(self):
        default_color = '#1428A0'
        default_hover = '#1428A1'
        data_color = '#e74c3c'
        data_hover = '#c0392b'
        selected_data_color = '#922b21'
        selected_data_hover = '#7a1f1a'
        selected_no_data_color = '#0f196e'
        selected_no_data_hover = '#0c1155'

        for label, btn in self.buttons.items() :
            key = self.metric_key_map[label]
            failure_data = self.failures.get(key)
            has_data = failure_data is not None and (not isinstance(failure_data, list) or len(failure_data) > 0)

            if label == self.current_metric and has_data :
                color, hover = selected_data_color, selected_data_hover
            elif label == self.current_metric :
                color, hover = selected_no_data_color, selected_no_data_hover
            elif has_data :
                color, hover = data_color, data_hover
            else:
                color, hover = default_color, default_hover

            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; color: white;"
                f" border: none; border-radius: 4px; padding: 4px 12px; }}"
                f"QPushButton:hover {{ background-color: {hover}; }}"
            )

    def open_dynamic_properties_dialog(self) :
        dlg = DynamicPropertiesDialog(self)
        result = dlg.exec_()
        if result == QDialog.Accepted:
            QMessageBox.information(
            self,
            "설정 저장됨",
            "라인/시프트별 Item 및 RMC 임계값이 저장되었습니다."
        )

    def on_file_selected(self, filepath: str):
        if FilePaths.get("dynamic_excel_file"):
            self.dynamic_props_btn.setVisible(True)

    """
    프로젝트 분석 데이터 설정
    """
    def set_project_analysis_data(self, data) :
        self.project_analysis_data = data

        if not data :
            self.failures['production_capacity'] = None
            self._update_button_styles()
            return
        
        if isinstance(data, dict) and 'display_df' in data :
            display_df = data.get('display_df')

            if display_df is None or (hasattr(display_df, 'empty') and display_df.empty) :
                self.failures['production_capacity'] = None
                self._update_button_styles()
                return
        
            has_issues = False

            try :
                for _, row in display_df.iterrows():
                    if row.get('PJT') == 'Total' and row.get('status') == '이상':
                        has_issues = True
                        break
            except Exception :
                has_issues = False

            if has_issues :
                issues = []

                try :
                    for _, row in display_df.iterrows() :
                        if row.get('PJT') == 'Total' and row.get('status') == '이상' :
                            issues.append({
                                'line': row.get('PJT Group', ''),
                                'reason': '용량 초과',
                                'available': row.get('CAPA', 0),
                                'excess': int(row.get('MFG', 0)) - int(row.get('CAPA', 0)) if row.get('MFG') and row.get('CAPA') else 0,
                                'cap_limit': row.get('CAPA', 0),
                                'center': row.get('PJT Group', '').split('_')[0] if isinstance(row.get('PJT Group', ''), str) and '_' in row.get('PJT Group', '') else ''
                            })
                except Exception :
                    pass

                self.failures['production_capacity'] = issues if issues else None
            else :
                self.failures['production_capacity'] = None

            self._update_button_styles()
        else :
            self.failures['production_capacity'] = None
            self._update_button_styles()

        # if self.current_metric == 'Production Capacity':
        #     self._populate_project_analysis_table()
        #     self.stacked_widget.setCurrentWidget(self.project_analysis_table)
