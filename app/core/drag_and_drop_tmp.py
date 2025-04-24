from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

class DemandWidget(QWidget):
    def __init__(self,item, to_site , mfg, sop):
        pass

class TableWidgetExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('QTableWidget with Multiple Widgets in One Cell')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # QTableWidget 설정
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(2)

        # 첫 번째 열에 텍스트 추가
        self.tableWidget.setItem(0, 0, QTableWidgetItem("물건1"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("물건2"))
        self.tableWidget.setItem(2, 0, QTableWidgetItem("물건3"))

        # 두 번째 열에 여러 위젯을 삽입할 위젯 생성
        for row in range(3):
            containerWidget = QWidget()
            layoutInCell = QHBoxLayout(containerWidget)

            # 첫 번째 위젯: 버튼
            button = QPushButton(f'버튼{row+1}')
            layoutInCell.addWidget(button)

            # 두 번째 위젯: 라벨
            label = QLabel(f'라벨{row+1}')
            layoutInCell.addWidget(label)

            # 위젯을 셀에 추가
            self.tableWidget.setCellWidget(row, 1, containerWidget)

        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication([])
    window = TableWidgetExample()
    window.show()
    app.exec_()
