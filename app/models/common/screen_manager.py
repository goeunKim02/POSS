from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtGui import QScreen, QGuiApplication

"""
해상도를 설정하는 클래스
"""
class ScreenManager:
    # 기준 해상도
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    BASE_DPI = 96

    # FHD를 QHD처럼 보이게 하는 스케일
    FHD_TO_QHD_SCALE = 0.6

    def __init__(self):
        pass

    """
    현재 위젯이 있는 스크린 또는 마우스 커서가 있는 스크린 반환
    """
    @staticmethod
    def get_current_screen(widget: QWidget = None) -> QScreen:
        app = QApplication.instance() or QGuiApplication.instance()
        if not app:
            return None

        # 위젯의 중심점으로 스크린 찾기
        if widget:
            center = widget.geometry().center()
            global_center = widget.mapToGlobal(center) if hasattr(widget, 'mapToGlobal') else center
            screen = app.screenAt(global_center)
            if screen:
                return screen

        # 마우스 커서 위치로 스크린 찾기
        desktop = QDesktopWidget()
        cursor_pos = desktop.cursor().pos()
        return app.screenAt(cursor_pos)

    """
    스크린의 상세 정보 반환
    """
    @staticmethod
    def get_screen_info(screen: QScreen = None) -> dict:
        if not screen:
            screen = ScreenManager.get_current_screen()

        if not screen:
            return {
                'width': ScreenManager.BASE_WIDTH,
                'height': ScreenManager.BASE_HEIGHT,
                'dpi': ScreenManager.BASE_DPI,
                'scale': 1.0
            }

        geometry = screen.geometry()
        available = screen.availableGeometry()

        return {
            'name': screen.name(),
            'width': geometry.width(),
            'height': geometry.height(),
            'available_width': available.width(),
            'available_height': available.height(),
            'physical_dpi': screen.physicalDotsPerInch(),
            'logical_dpi': screen.logicalDotsPerInch(),
            'device_pixel_ratio': screen.devicePixelRatio(),
            'orientation': screen.orientation(),
            'is_primary': screen == QGuiApplication.primaryScreen()
        }

    """
    현재 스크린의 스케일 팩터 계산 (FHD를 QHD처럼 보이게 하는 용도)
    """
    @staticmethod
    def get_scale_factor(screen: QScreen = None) -> float:
        if not screen:
            screen = ScreenManager.get_current_screen()

        if not screen:
            return 1.0

        info = ScreenManager.get_screen_info(screen)
        width = info['width']

        # FHD인 경우 0.75 스케일 적용
        if width == 1920:
            return ScreenManager.FHD_TO_QHD_SCALE
        # QHD 이상은 그대로 (스케일 1.0)
        else:
            return 1

    """
    크기 값을 현재 스크린에 맞게 조정
    """
    @staticmethod
    def size(value: int, widget: QWidget = None) -> int:
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        return round(value * scale)

    """
    폰트 크기를 현재 스크린에 맞게 조정
    """
    @staticmethod
    def font_size(value: int, widget: QWidget = None) -> int:
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        return round(value * scale)

    """
    너비 값을 현재 스크린에 맞게 조정
    """
    @staticmethod
    def width(value: int, widget: QWidget = None) -> int:
        return ScreenManager.size(value, widget)

    """
    높이 값을 현재 스크린에 맞게 조정
    """
    @staticmethod
    def height(value: int, widget: QWidget = None) -> int:
        return ScreenManager.size(value, widget)

    """
    여백 값을 현재 스크린에 맞게 조정
    """
    @staticmethod
    def margin(value: int, widget: QWidget = None) -> int:
        return ScreenManager.size(value, widget)

    """
    패딩 값을 현재 스크린에 맞게 조정
    """
    @staticmethod
    def padding(value: int, widget: QWidget = None) -> int:
        return ScreenManager.size(value, widget)

    """
    간격 값을 현재 스크린에 맞게 조정
    """
    @staticmethod
    def spacing(value: int, widget: QWidget = None) -> int:
        return ScreenManager.size(value, widget)

    """
    아이콘 크기를 현재 스크린에 맞게 조정
    """
    @staticmethod
    def icon_size(value: int, widget: QWidget = None) -> int:
        return ScreenManager.size(value, widget)

    """
    너비와 높이를 튜플로 반환
    """
    @staticmethod
    def get_size_tuple(width: int, height: int, widget: QWidget = None) -> tuple:
        return (
            ScreenManager.width(width, widget),
            ScreenManager.height(height, widget)
        )

    """
    여백을 튜플로 반환
    """
    @staticmethod
    def get_margins(top: int, right: int, bottom: int, left: int, widget: QWidget = None) -> tuple:
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        return (
            round(top * scale),
            round(right * scale),
            round(bottom * scale),
            round(left * scale)
        )

screen_mgr = ScreenManager()

# 편의를 위한 짧은 별칭
s = screen_mgr.size
w = screen_mgr.width
h = screen_mgr.height
m = screen_mgr.margin
p = screen_mgr.padding
sp = screen_mgr.spacing
fs = screen_mgr.font_size
ics = screen_mgr.icon_size
st = screen_mgr.get_size_tuple
gm = screen_mgr.get_margins