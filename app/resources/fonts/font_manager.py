# app/resources/fonts/font_manager.py
import os
import sys
from pathlib import Path
from PyQt5.QtGui import QFont, QFontDatabase


class FontManager:
    def __init__(self):
        self.fonts = {}
        self.font_dir = None
        self._initialized = False

    def _lazy_init(self):
        """필요할 때 초기화 수행"""
        if self._initialized:
            return

        try:
            # 현재 파일의 디렉토리 경로
            self.font_dir = Path(__file__).parent
            print(f"폰트 디렉토리: {self.font_dir}")

            self.load_all_fonts()
            self._initialized = True
        except Exception as e:
            print(f"폰트 매니저 초기화 오류: {e}")
            self._initialized = True  # 재시도 방지

    def load_all_fonts(self):
        """fonts 폴더의 모든 폰트 로드"""
        try:
            if not self.font_dir.exists():
                print(f"폰트 디렉토리를 찾을 수 없습니다: {self.font_dir}")
                return

            # .ttf와 .otf 파일들 찾기
            font_files = list(self.font_dir.glob("*.ttf")) + list(self.font_dir.glob("*.otf"))

            if not font_files:
                print(f"폰트 파일을 찾을 수 없습니다: {self.font_dir}")
                return

            print(f"찾은 폰트 파일 수: {len(font_files)}")

            for font_file in font_files:
                self.load_font(font_file)

        except Exception as e:
            print(f"폰트 로드 중 오류: {e}")

    def load_font(self, font_path):
        """개별 폰트 파일 로드"""
        try:
            print(f"폰트 로드 시도: {font_path.name}")
            font_id = QFontDatabase.addApplicationFont(str(font_path))

            if font_id >= 0:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    font_key = font_path.stem  # 파일명 (확장자 제외)
                    self.fonts[font_key] = families[0]
                    print(f"폰트 로드 성공: {font_key} -> {families[0]}")
                else:
                    print(f"폰트 패밀리 없음: {font_path.name}")
            else:
                print(f"폰트 로드 실패: {font_path.name} (ID: {font_id})")

        except Exception as e:
            print(f"폰트 로드 오류 {font_path.name}: {e}")

    def get_font(self, font_key, size=12, weight=QFont.Normal):
        """폰트 객체 반환"""
        self._lazy_init()

        if font_key in self.fonts:
            font = QFont(self.fonts[font_key], size, weight)
            return font
        else:
            print(f"폰트를 찾을 수 없습니다: {font_key}")
            print(f"사용 가능한 폰트: {list(self.fonts.keys())}")
            return QFont()  # 기본 폰트

    def get_bold_font(self, font_key, size,weight=QFont.Bold):
        self._lazy_init()
        if font_key in self.fonts:
            font = QFont(self.fonts[font_key],size,weight)
            return font
        else:
            return QFont()

    def get_just_font(self, font_key):
        self._lazy_init()
        if font_key in self.fonts:
            font = QFont(self.fonts[font_key])
            return font
        else:
            return QFont()

    def set_app_font(self, app, font_key):
        """애플리케이션 폰트 패밀리만 변경 (크기는 유지)"""
        self._lazy_init()

        try:
            if font_key in self.fonts:
                current_font = app.font()
                current_font.setFamily(self.fonts[font_key])
                app.setFont(current_font)
                print(f"애플리케이션 폰트 설정 성공: {font_key}")
                return True
            else:
                print(f"폰트를 찾을 수 없습니다: {font_key}")
                print(f"사용 가능한 폰트: {list(self.fonts.keys())}")
                return False
        except Exception as e:
            print(f"폰트 설정 오류: {e}")
            return False


# 싱글톤 인스턴스 생성
try:
    font_manager = FontManager()
except Exception as e:
    print(f"FontManager 생성 오류: {e}")
    font_manager = None