from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt

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

        self.buttons = {}
        self._init_ui()
        self._build_metric_buttons()
        self.failure_table.header().hide()
        self.show_failures.connect(self._on_failures)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 버튼 바
        self.button_bar = QHBoxLayout()
        self.button_bar.setSpacing(8)
        layout.addLayout(self.button_bar)

        # 실패 테이블
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

    def _build_metric_buttons(self):
        # 기존 버튼 제거
        for i in reversed(range(self.button_bar.count())):
            w = self.button_bar.takeAt(i).widget()
            if w:
                w.deleteLater()
        self.buttons.clear()

        # 새 버튼 생성
        for label in self.metric_key_map:
            btn = QPushButton(label)
            btn.setFont(QFont('Arial', 9, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, lb=label: self._on_metric_clicked(lb))
            self.button_bar.addWidget(btn)
            self.buttons[label] = btn

        self.button_bar.addStretch()
        self._update_button_styles()

    def _on_failures(self, failures: dict):
        self.failures = failures
        self._build_metric_buttons()

        if failures.get('production_capacity'):
            self.current_metric = 'Production Capacity'
        elif failures.get('plan_adherence_rate'):
            self.current_metric = 'Plan Adherence Rate'
        else:
            for lbl, key in self.metric_key_map.items():
                if failures.get(key):
                    self.current_metric = lbl
                    break

        self._populate_for_metric(self.current_metric)

    def _on_metric_clicked(self, label: str):
        if label == 'Plan Adherence Rate':
            self._pa_view = 'rmc' if self._pa_view == 'item' else 'item'
        else:
            self.current_metric = label

        self._populate_for_metric(label)

    def _populate_for_metric(self, label: str):
        self.current_metric = label
        key = self.metric_key_map[label]

        if label == 'Plan Adherence Rate':
            pa = self.failures.get('plan_adherence_rate', {})
            data = pa.get(f"{self._pa_view}_failures", [])
            fields = self.header_map[label][self._pa_view]
        else:
            data = self.failures.get(key, []) or []
            fields = self.header_map[label]

        # 테이블 헤더 구성
        headers = [h for h, _ in fields]
        self.failure_table.clear()
        self.failure_table.setColumnCount(len(headers))
        self.failure_table.setHeaderLabels(headers)
        self.failure_table.header().show()

        red = QBrush(QColor('#e74c3c'))
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

        for label, btn in self.buttons.items():
            key = self.metric_key_map[label]
            has_data = bool(self.failures.get(key))
            if label == self.current_metric and has_data:
                color, hover = selected_data_color, selected_data_hover
            elif label == self.current_metric:
                color, hover = selected_no_data_color, selected_no_data_hover
            elif has_data:
                color, hover = data_color, data_hover
            else:
                color, hover = default_color, default_hover

            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; color: white;"
                f" border: none; border-radius: 4px; padding: 4px 12px; }}"
                f"QPushButton:hover {{ background-color: {hover}; }}"
            )
