# app/views/components/settings_dialogs/__init__.py - 설정 다이얼로그 패키지 초기화
from .settings_components.basic_tab import BasicTabComponent
from .settings_components.pre_option_tab import PreOptionTabComponent
from .settings_components.detail_tab import DetailTabComponent
from .settings_dialog import SettingsDialog

# 외부에서 import 가능하도록 설정
__all__ = [
    'SettingsDialog'
]