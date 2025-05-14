from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import (
    QWidget, QPushButton,
    QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout,
    QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from app.utils.error_handler import (
    error_handler, safe_operation, DataError, ValidationError, AppError
)
from app.resources.fonts.font_manager import font_manager


class RightParameterComponent(QWidget):
    show_failures = pyqtSignal(dict)
    close_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

        try:
            self.show_failures.connect(self._on_failures)
        except Exception as e:
            raise AppError(f'Failed to connect signals : {str(e)}')

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

        # 전체 배경색 설정
        self.setStyleSheet("background-color: white; border: none;")

        # 제목 영역을 위한 프레임
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: none;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 8, 10, 8)

        title_label = QLabel("Problems")
        title_font = font_manager.get_font("SamsungOne-700", 12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333333; background-color: transparent; border: none;")

        minimize_button = QPushButton()
        minimize_button.setIcon(self.style().standardIcon(self.style().SP_TitleBarMinButton))
        minimize_button.setFixedSize(24, 24)
        minimize_button.setCursor(Qt.PointingHandCursor)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #1428A0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        minimize_button.clicked.connect(self.close_button_clicked.emit)

        # Problems 와 최소화버튼
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)

        layout.addWidget(title_frame)

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

        # 리스트 컨테이너
        list_container = QFrame()
        list_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 8px;
            }
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { 
                border: none; 
                outline: none;
                background-color: white;
                border-radius: 8px;
                font-family: %s;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #F5F5F5;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QListWidget::item:selected {
                background-color: #E8ECFF;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #F5F7FF;
            }
            QScrollBar{
                border: none;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle {
                background: #CCCCCC;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page, QScrollBar::sub-page {
                background: none;
            }
        """ % font_manager.get_just_font("SamsungOne-700").family())

        list_layout.addWidget(self.list_widget)
        content_layout.addWidget(list_container)
        layout.addWidget(content_frame)

    """
    파일 선택 이벤트 처리
    """

    @error_handler(
        default_return=None
    )
    def on_file_selected(self, filepath: str):
        pass

    """
    실패 정보 표시 처리
    """

    @error_handler(
        default_return=None
    )
    def _on_failures(self, failures: dict):
        if not isinstance(failures, dict):
            raise DataError('Failures must be a dictionary', {'type': type(failures)})

        safe_operation(
            self.list_widget.clear,
            'Error clearing list widget'
        )

        # Production Capacity Issues
        try:
            production_capacity_issues = failures.get('production_capacity', [])

            if production_capacity_issues:
                # 섹션 헤더 추가
                header_item = QListWidgetItem("Production Capacity Issues")
                header_item.setFont(font_manager.get_font('SamsungOne-700', 11))
                header_item.setBackground(QColor('#F5F5F5'))
                header_item.setForeground(QColor('#333333'))
                header_item.setFlags(Qt.ItemIsEnabled)  # 선택 불가능하게
                self.list_widget.addItem(header_item)

                for issue in production_capacity_issues:
                    line = issue.get('line', 'Unknown')
                    reason = issue.get('reason', 'capacity exceeded')
                    available = issue.get('available', 0)
                    excess = issue.get('excess', 0)
                    center = issue.get('center', '')

                    center_info = f'({center})' if center else ''
                    item_text = f'{reason} : {line}{center_info}, Available capacity : {available}, Excess amount : {excess}'

                    item = QListWidgetItem(item_text)
                    item_font = font_manager.get_font('SamsungOne-700', 10)
                    item.setFont(item_font)

                    # 에러 아이템 스타일링
                    item.setForeground(QColor('#E74C3C'))

                    safe_operation(
                        self.list_widget.addItem,
                        'Error adding capacity issue item',
                        item
                    )
        except Exception as e:
            raise DataError(f'Error processing production capacity issues : {str(e)}')

        # Plan Retention
        try:
            if failures.get('plan_retention') is not None:
                plan_retention = failures.get('plan_retention', {})

                item_plan_retention_rate = plan_retention.get('item_plan_retention')
                rmc_plan_retention = plan_retention.get('rmc_plan_retention')

                # 섹션 헤더 추가
                header_item = QListWidgetItem("Plan Retention")
                header_item.setFont(font_manager.get_font('SamsungOne-700', 11))
                header_item.setBackground(QColor('#F5F5F5'))
                header_item.setForeground(QColor('#333333'))
                header_item.setFlags(Qt.ItemIsEnabled)
                self.list_widget.addItem(header_item)

                item1 = QListWidgetItem(f'최대 Item 계획유지율 : {item_plan_retention_rate}')
                item2 = QListWidgetItem(f'최대 RMC 계획유지율 : {rmc_plan_retention}')

                item_font = font_manager.get_font('SamsungOne-700', 10)
                item1.setFont(item_font)
                item2.setFont(item_font)
                item1.setForeground(QColor('#666666'))
                item2.setForeground(QColor('#666666'))

                safe_operation(
                    self.list_widget.addItem,
                    'Error adding plan retention item', item1
                )
                safe_operation(
                    self.list_widget.addItem,
                    'Error adding plan retention item', item2
                )
        except Exception as e:
            raise DataError(f'Error processing plan retention data : {str(e)}')

        # Preassign Failures
        try:
            preassign_failures = failures.get('preassign', [])

            if preassign_failures:
                # 섹션 헤더 추가
                header_item = QListWidgetItem("Preassignment Issues")
                header_item.setFont(font_manager.get_font('SamsungOne-700', 11))
                header_item.setBackground(QColor('#F5F5F5'))
                header_item.setForeground(QColor('#333333'))
                header_item.setFlags(Qt.ItemIsEnabled)
                self.list_widget.addItem(header_item)

                for error in preassign_failures:
                    line = error.get('line', 'Unknown')
                    reason = error.get('reason', 'Unknown')
                    excess = error.get('excess', 'Unknown')

                    item = QListWidgetItem(f"{line} 라인이 {reason} 을 {excess} 초과했습니다")
                    item_font = font_manager.get_font('SamsungOne-700', 10)
                    item.setFont(item_font)
                    item.setForeground(QColor('#E74C3C'))

                    safe_operation(
                        self.list_widget.addItem,
                        'Error adding preassign failure item',
                        item
                    )
        except Exception as e:
            raise DataError(f'Error processing preassign failures : {str(e)}')

        # Materials Negative Stock
        try:
            if failures.get('materials_negative_stock'):
                negative_stock_materials = failures.get('materials_negative_stock', {})

                # 섹션 헤더 추가
                header_item = QListWidgetItem("Materials - Negative Stock")
                header_item.setFont(font_manager.get_font('SamsungOne-700', 11))
                header_item.setBackground(QColor('#F5F5F5'))
                header_item.setForeground(QColor('#333333'))
                header_item.setFlags(Qt.ItemIsEnabled)
                self.list_widget.addItem(header_item)

                for date, materials in negative_stock_materials.items():
                    # 날짜 헤더
                    date_item = QListWidgetItem(f'Negative initial stock materials:')
                    date_item.setFont(font_manager.get_font('SamsungOne-700', 10))
                    date_item.setForeground(QColor('#E74C3C'))
                    self.list_widget.addItem(date_item)

                    for material in materials:
                        material_id = material.get('material_id', 'Unknown')
                        stock = material.get('stock', 0)

                        detail_item = QListWidgetItem(f'  • {material_id} : {stock}')
                        detail_item.setFont(font_manager.get_font('SamsungOne-700', 10))
                        detail_item.setForeground(QColor('#E74C3C'))

                        safe_operation(
                            self.list_widget.addItem,
                            'Error adding material item',
                            detail_item
                        )
        except Exception as e:
            raise DataError(f'Error processing negative stock materials : {str(e)}')