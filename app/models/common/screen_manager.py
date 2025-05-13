# utils/screen_manager.py
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtGui import QScreen, QGuiApplication
import sys
import platform


class ScreenManager:
    # 기준 해상도 (FHD 기준)
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    BASE_DPI = 96

    # 스케일 캐시 (성능 최적화)
    _scale_cache = {}
    _last_update_time = 0

    def __init__(self):
        # 주기적으로 스케일 캐시 업데이트 (모니터 이동 감지)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_scale_cache)
        self.update_timer.start(1000)  # 1초마다 체크

    @staticmethod
    def get_current_screen(widget: QWidget = None) -> QScreen:
        """현재 위젯이 있는 스크린 또는 마우스 커서가 있는 스크린 반환"""
        app = QApplication.instance() or QGuiApplication.instance()
        if not app:
            return None

        if widget:
            # 위젯의 중심점으로 스크린 찾기
            center = widget.geometry().center()
            global_center = widget.mapToGlobal(center) if hasattr(widget, 'mapToGlobal') else center
            screen = app.screenAt(global_center)
            if screen:
                return screen

        # 마우스 커서 위치로 스크린 찾기
        desktop = QDesktopWidget()
        cursor_pos = desktop.cursor().pos()
        return app.screenAt(cursor_pos)

    @staticmethod
    def get_screen_info(screen: QScreen = None) -> dict:
        """스크린의 상세 정보 반환"""
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

    @staticmethod
    def get_scale_factor(screen: QScreen = None, force_update: bool = False) -> float:
        """현재 스크린의 스케일 팩터 계산"""
        if not screen:
            screen = ScreenManager.get_current_screen()

        if not screen:
            return 1.0

        # 캐시 체크 (성능 최적화)
        screen_name = screen.name()
        if not force_update and screen_name in ScreenManager._scale_cache:
            return ScreenManager._scale_cache[screen_name]

        info = ScreenManager.get_screen_info(screen)

        # 1. Windows/Linux/Mac별 시스템 스케일 감지
        system_scale = 1.0
        if platform.system() == 'Windows':
            # Windows의 디스플레이 스케일 설정
            system_scale = info['logical_dpi'] / ScreenManager.BASE_DPI
        elif platform.system() == 'Darwin':  # macOS
            # macOS Retina 디스플레이
            system_scale = info['device_pixel_ratio']
        else:  # Linux
            # Linux의 경우 logical DPI 사용
            system_scale = info['logical_dpi'] / ScreenManager.BASE_DPI

        # 2. 해상도 기반 스케일
        resolution_scale = info['width'] / ScreenManager.BASE_WIDTH

        # 3. 최종 스케일 계산
        if info['width'] >= 2560:  # QHD 이상
            # 고해상도에서는 해상도 스케일을 우선
            final_scale = max(system_scale, resolution_scale)
        else:  # FHD 이하
            # 저해상도에서는 시스템 스케일을 우선
            final_scale = system_scale

        # 4. 스케일 범위 제한 (0.75 ~ 2.5)
        final_scale = max(0.75, min(2.5, final_scale))

        # 캐시 저장
        ScreenManager._scale_cache[screen_name] = final_scale

        return final_scale

    @staticmethod
    def update_scale_cache():
        """모든 스크린의 스케일 캐시 업데이트"""
        app = QApplication.instance() or QGuiApplication.instance()
        if not app:
            return

        for screen in app.screens():
            ScreenManager.get_scale_factor(screen, force_update=True)

    @staticmethod
    def size(value: int, widget: QWidget = None) -> int:
        """크기 값을 현재 스크린에 맞게 조정"""
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        return round(value * scale)

    @staticmethod
    def font_size(value: int, widget: QWidget = None) -> int:
        """폰트 크기를 현재 스크린에 맞게 조정"""
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        # 폰트는 스케일을 약간 보수적으로 적용
        font_scale = 0.9 + (scale - 1) * 0.7
        return round(value * font_scale)

    @staticmethod
    def width(value: int, widget: QWidget = None) -> int:
        """너비 값을 현재 스크린에 맞게 조정"""
        return ScreenManager.size(value, widget)

    @staticmethod
    def height(value: int, widget: QWidget = None) -> int:
        """높이 값을 현재 스크린에 맞게 조정"""
        return ScreenManager.size(value, widget)

    @staticmethod
    def margin(value: int, widget: QWidget = None) -> int:
        """여백 값을 현재 스크린에 맞게 조정"""
        return ScreenManager.size(value, widget)

    @staticmethod
    def padding(value: int, widget: QWidget = None) -> int:
        """패딩 값을 현재 스크린에 맞게 조정"""
        return ScreenManager.size(value, widget)

    @staticmethod
    def spacing(value: int, widget: QWidget = None) -> int:
        """간격 값을 현재 스크린에 맞게 조정"""
        return ScreenManager.size(value, widget)

    @staticmethod
    def icon_size(value: int, widget: QWidget = None) -> int:
        """아이콘 크기를 현재 스크린에 맞게 조정"""
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        # 아이콘은 스케일을 더 보수적으로 적용
        icon_scale = 0.95 + (scale - 1) * 0.6
        return round(value * icon_scale)

    @staticmethod
    def get_size_tuple(width: int, height: int, widget: QWidget = None) -> tuple:
        """너비와 높이를 튜플로 반환"""
        return (
            ScreenManager.width(width, widget),
            ScreenManager.height(height, widget)
        )

    @staticmethod
    def get_margins(top: int, right: int, bottom: int, left: int, widget: QWidget = None) -> tuple:
        """여백을 튜플로 반환"""
        scale = ScreenManager.get_scale_factor(ScreenManager.get_current_screen(widget))
        return (
            round(top * scale),
            round(right * scale),
            round(bottom * scale),
            round(left * scale)
        )

    @staticmethod
    def is_high_dpi(widget: QWidget = None) -> bool:
        """현재 스크린이 High DPI인지 확인"""
        screen = ScreenManager.get_current_screen(widget)
        if not screen:
            return False

        info = ScreenManager.get_screen_info(screen)
        return info['logical_dpi'] > 120 or info['device_pixel_ratio'] > 1.5

    @staticmethod
    def is_qhd_or_higher(widget: QWidget = None) -> bool:
        """현재 스크린이 QHD 이상인지 확인"""
        screen = ScreenManager.get_current_screen(widget)
        if not screen:
            return False

        info = ScreenManager.get_screen_info(screen)
        return info['width'] >= 2560

# 싱글톤 인스턴스
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
