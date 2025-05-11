# main.py
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from splash_start import SamsungSplashScreen  # 스플래시 스크린 클래스 임포트


def exception_hook(exctype, value, traceback_obj):
    """글로벌 예외 처리기"""
    error_msg = ''.join(traceback.format_exception(exctype, value, traceback_obj))
    print("예외 발생:", error_msg)  # 콘솔에도 출력

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("An error has occurred in the application.")
    msg.setInformativeText("Please refer to the details below for more information about the error.")
    msg.setDetailedText(error_msg)
    msg.setWindowTitle("Error Occurred")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 글로벌 예외 처리기 설정
    sys.excepthook = exception_hook

    # 스플래시 스크린 생성 및 표시
    splash = SamsungSplashScreen()
    splash.show()

    # 이벤트 루프 시작
    sys.exit(app.exec_())