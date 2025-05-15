# main.py
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt


def exception_hook(exctype, value, traceback_obj):
    """글로벌 예외 처리기"""
    error_msg = ''.join(traceback.format_exception(exctype, value, traceback_obj))
    print("예외 발생:", error_msg)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("An error has occurred in the application.")
    msg.setInformativeText("Please refer to the details below for more information about the error.")
    msg.setDetailedText(error_msg)
    msg.setWindowTitle("Error Occurred")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


if __name__ == "__main__":
    # # High DPI 설정 (선택사항)
    # if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    #     QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    #     QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # 글로벌 예외 처리기 설정
    sys.excepthook = exception_hook

    try:
        # 폰트 매니저 임포트 및 설정
        from app.resources.fonts.font_manager import font_manager

        success = font_manager.set_app_font(app, "SamsungSharpSans-Bold")

        if not success:
            print("경고: 폰트 설정 실패, 기본 폰트 사용")

        # 스플래시 스크린 임포트 및 표시
        from splash_start import SamsungSplashScreen

        splash = SamsungSplashScreen()
        splash.show()

    except ImportError as e:
        print(f"임포트 오류: {e}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"모듈을 찾을 수 없습니다: {e}")
        msg.setWindowTitle("Import Error")
        msg.exec_()
        sys.exit(1)
    except Exception as e:
        print(f"초기화 오류: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 이벤트 루프 시작
    sys.exit(app.exec_())