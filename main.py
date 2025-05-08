import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from app.views.main_window import MainWindow


def exception_hook(exctype, value, traceback_obj):
    """글로벌 예외 처리기"""
    error_msg = ''.join(traceback.format_exception(exctype, value, traceback_obj))
    print("예외 발생:", error_msg)  # 콘솔에도 출력

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("프로그램에서 오류가 발생했습니다")
    msg.setInformativeText("자세한 오류 내용은 아래를 참조하세요:")
    msg.setDetailedText(error_msg)
    msg.setWindowTitle("오류 발생")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 글로벌 예외 처리기 설정
    sys.excepthook = exception_hook

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())