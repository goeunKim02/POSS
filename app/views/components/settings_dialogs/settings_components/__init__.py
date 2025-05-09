# app/views/components/settings_dialogs/settings_components/__init__.py - 설정 컴포넌트 패키지 초기화
from .basic_tab import BasicTabComponent
from .pre_option_tab import PreOptionTabComponent
from .detail_tab import DetailTabComponent

# 외부에서 import 가능하도록 설정
__all__ = [
    'BasicTabComponent',
    'PreOptionTabComponent',
    'DetailTabComponent'
]