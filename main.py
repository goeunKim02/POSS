import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from app.views.main_window import MainWindow

if __name__ == "__main__":
    # 애플리케이션 생성 전에 high DPI 설정
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # # 스케일 팩터 직접 설정 (예: 1.0 = 100%, 0.75 = 75%)
    os.environ["QT_SCALE_FACTOR"] = "1.0"  # 적절한 값으로 조정

    # 자동 스케일링 비활성화
    # QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)

    app = QApplication(sys.argv)
    # # 수동으로 스케일 팩터 설정 (1.0보다 작은 값을 사용하여 크기 줄이기)
    # QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Floor)
    
    # 전체 폰트 설정
    font = app.font()
    font.setPointSize(8)  # 작은 폰트 크기 설정
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())