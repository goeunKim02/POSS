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
        for error in failures.get('preassign'):
            line = error.get('line')
            reason = error.get('reason')
            excess = error.get('excess')
            self.list_widget.addItem(QListWidgetItem(f"{line} 라인이 {reason} 을 {excess} 초과했습니다"))
