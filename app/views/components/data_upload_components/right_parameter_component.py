from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QDialog, QMessageBox, QLabel, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import pyqtSignal, Qt

from .open_dynamic_properties_dialog import DynamicPropertiesDialog
from app.models.common.fileStore import FilePaths
from app.models.common.event_bus import EventBus

class RightParameterComponent(QWidget):
    show_failures = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.show_failures.connect(self._on_failures)
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(QLabel("Problems"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    def on_file_selected(self, filepath: str):
        pass

    def _on_failures(self, failures: dict):
        self.list_widget.clear()

        if failures.get('plan_retention') is not None:
            item_plan_retention_rate = failures.get('plan_retention').get('item_plan_retention')
            rmc_plan_retention = failures.get('plan_retention').get('rmc_plan_retention')
            self.list_widget.addItem(QListWidgetItem(f"최대 Item 계획유지율 : {item_plan_retention_rate}"))
            self.list_widget.addItem(QListWidgetItem(f"최대 RMC 계획유지율 : {rmc_plan_retention}"))

        for error in failures.get('preassign'):
            line = error.get('line')
            reason = error.get('reason')
            excess = error.get('excess')
            self.list_widget.addItem(QListWidgetItem(f"{line} 라인이 {reason} 을 {excess} 초과했습니다"))


        # 기초 재고가 0 미만인 자재 표시
        if failures.get('materials_negative_stock') :
            negative_stock_materials = failures.get('materials_negative_stock')

            for date, materials in negative_stock_materials.items() :
                date_item = QListWidgetItem(f'Negative Initial Stock Materials :')
                date_item.setForeground(QColor("#e74c3c"))
                date_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.list_widget.addItem(date_item)

                for material in materials :
                    material_id = material.get('material_id', 'Unknown')
                    stock = material.get('stock', 0)

                    detail_item = QListWidgetItem(f'  - {material_id} : {stock}')
                    detail_item.setForeground(QColor("#e74c3c"))
                    self.list_widget.addItem(detail_item)