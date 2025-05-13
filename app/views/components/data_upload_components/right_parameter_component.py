from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import (
    QWidget, QPushButton,
    QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal
from app.utils.error_handler import (
    error_handler, safe_operation, DataError, ValidationError, AppError
)

class RightParameterComponent(QWidget):
    show_failures = pyqtSignal(dict)
    close_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._init_ui()

        try :
            self.show_failures.connect(self._on_failures)
        except Exception as e :
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
        layout.setContentsMargins(10, 10, 10, 10)

        title_layout = QHBoxLayout(self)
        title_label = QLabel("Problems")
        title_label.setFont(QFont("Arial", 9, QFont.Bold))

        minimize_button = QPushButton()
        minimize_button.setIcon(self.style().standardIcon(self.style().SP_TitleBarMinButton))
        minimize_button.setStyleSheet("border: 1px solid gray; border-radius: 5px;")
        minimize_button.clicked.connect(self.close_button_clicked.emit)

        # Problems 와 최소화버튼
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)


        layout.addLayout(title_layout)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)


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
        if not isinstance(failures, dict) :
            raise DataError('Failures must be a dictionary', {'type' : type(failures)})
        
        safe_operation(
            self.list_widget.clear,
            'Error clearing list widget'
        )

        try :
            production_capacity_issues = failures.get('production_capacity', [])

            if production_capacity_issues :
                for issue in production_capacity_issues :
                    line = issue.get('line', 'Unknown')
                    reason = issue.get('reason', 'capacity exceeded')
                    available = issue.get('available', 0)
                    excess = issue.get('excess', 0)
                    center = issue.get('center', '')

                    center_info = f'({center})' if center else ''
                    item_text = f'{reason} : {line}{center_info}, Available capacity : {available}, Excess amount : {excess}'

                    item = QListWidgetItem(item_text)
                    item.setForeground(QColor('#e74c3c'))

                    bold_font = QFont('Arial', 9, QFont.Bold)
                    item.setFont(bold_font)

                    safe_operation(
                        self.list_widget.addItem,
                        'Error adding capacity issue item',
                        item
                    )
        except Exception as e :
            raise DataError(f'Error processing production capacity issues : {str(e)}')

        try :
            if failures.get('plan_retention') is not None :
                plan_retention = failures.get('plan_retention', {})

                item_plan_retention_rate = plan_retention.get('item_plan_retention')
                rmc_plan_retention = plan_retention.get('rmc_plan_retention')
                
                item1 = QListWidgetItem(f'최대 Item 계획유지율 : {item_plan_retention_rate}')
                item2 = QListWidgetItem(f'최대 RMC 계획유지율 : {rmc_plan_retention}')

                safe_operation(
                    self.list_widget.addItem,
                    'Error adding plan retention item', item1
                )
                safe_operation(
                    self.list_widget.addItem,
                    'Error adding plan retention item', item2
                )
        except Exception as e :
            raise DataError(f'Error processing plan retention data : {str(e)}')

        try :
            preassign_failures = failures.get('preassign', [])

            for error in preassign_failures :
                line = error.get('line', 'Unknown')
                reason = error.get('reason', 'Unknown')
                excess = error.get('excess', 'Unknown')
                
                item = QListWidgetItem(f"{line} 라인이 {reason} 을 {excess} 초과했습니다")

                safe_operation(
                    self.list_widget.addItem,
                    'Error adding preassign failure item',
                    item
                )
        except Exception as e :
            raise DataError(f'Error processing preassign failures : {str(e)}')


        # 기초 재고가 0 미만인 자재 표시
        try :
            if failures.get('materials_negative_stock') :
                negative_stock_materials = failures.get('materials_negative_stock', {})

                for date, materials in negative_stock_materials.items() :
                    try :
                        date_item = QListWidgetItem(f'Negative initial stock materials : ')
                        date_item.setForeground(QColor('#e74c3c'))

                        bold_font = QFont('Arial', 9, QFont.Bold)
                        date_item.setFont(bold_font)

                        safe_operation(
                            self.list_widget.addItem,
                            'Error adding date item',
                            date_item
                        )
                    except Exception as stype_error :
                        date_item = QListWidgetItem(f'Negative Initial Stock Materials : ')

                        safe_operation(
                            self.list_widget.addItem,
                            'Error adding date item',
                            date_item
                        )

                    for material in materials :
                        material_id = material.get('material_id', 'Unknown')
                        stock = material.get('stock', 0)

                        try :
                            detail_item = QListWidgetItem(f'  - {material_id} : {stock}')
                            detail_item.setForeground(QColor("#e74c3c"))
                            safe_operation(
                                self.list_widget.addItem,
                                'Error adding material item',
                                detail_item
                            )
                        except Exception as detail_error :
                            detail_item = QListWidgetItem(f'  - {material_id} : {stock}')
                            safe_operation(
                                self.list_widget.addItem,
                                'Error adding material item',
                                detail_item
                            )
        except Exception as e :
            raise DataError(f'Error processing negative stock materials : {str(e)}')