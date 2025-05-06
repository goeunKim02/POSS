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
        self.metric_key_map = {
            'Production Capacity': 'production_capacity',
            'Materials': 'materials',
            'Current Shipment': 'current_shipment',
            'Preassignment': 'preassign',
            'Shippable Quantity': 'shippable_quantity',
            'Plan Adherence Rate': 'plan_adherence_rate'
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
            'Plan Adherence Rate': [
                ('Plan Date', 'plan_date'),
                ('Line', 'line'),
                ('Deviation', 'reason'),
                ('Adherence%', 'available'),
                ('Variance', 'excess'),
            ],
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
            QTreeWidget {
                border: none;
                outline: none;
            }
            QTreeView::branch {
                background: none;
            }
            QTreeView::header {
                background-color: transparent;
                border: none;
                margin: 0px;
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
        """)
        layout.addWidget(self.failure_table, 1)

    def _on_failures(self, failures: dict):
        self.failures = failures
        self._build_metric_buttons()

        default_label = 'Production Capacity'
        default_key = self.metric_key_map[default_label]
        if failures.get(default_key):
            self._populate_for_metric(default_label)
        else:
            for label, key in self.metric_key_map.items():
                if failures.get(key):
                    self._populate_for_metric(label)
                    break

    def _build_metric_buttons(self):
        # 이전 버튼 제거
        for i in reversed(range(self.button_bar.count())):
            w = self.button_bar.takeAt(i).widget()
            if w:
                w.deleteLater()
        self.buttons.clear()

        # 새 버튼 생성
        for label in self.metric_key_map.keys():
            btn = QPushButton(label)
            btn.setFont(QFont('Arial', 9, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, lb=label: self._populate_for_metric(lb))
            self.button_bar.addWidget(btn)
            self.buttons[label] = btn

        self.button_bar.addStretch()
        self._update_button_styles()

    def _populate_for_metric(self, label: str):
        self.current_metric = label
        key = self.metric_key_map[label]
        data_list = self.failures.get(key, []) or []

        # 헤더 설정
        headers = [h for h, _ in self.header_map[label]]
        self.failure_table.clear()
        self.failure_table.setColumnCount(len(headers))
        self.failure_table.setHeaderLabels(headers)
        self.failure_table.header().show()

        # 데이터 추가
        red_brush = QBrush(QColor('#e74c3c'))
        for info in data_list:
            values = [str(info.get(field, '')) for _, field in self.header_map[label]]
            item = QTreeWidgetItem(values)
            for col in range(len(values)):
                item.setForeground(col, red_brush)
            self.failure_table.addTopLevelItem(item)

        self.failure_table.sortItems(0, Qt.AscendingOrder)
        self._update_button_styles()

    def _update_button_styles(self):
        default_color = '#1428A0'
        default_hover = '#1b36c1'
        data_color = '#e74c3c'
        data_hover = '#c0392b'
        selected_data_color = '#922b21'
        selected_data_hover = '#7a1f1a'
        selected_no_data_color = '#0f196e'
        selected_no_data_hover = '#0c1155'

        for label, btn in self.buttons.items():
            has_data = bool(self.failures.get(self.metric_key_map[label]))
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