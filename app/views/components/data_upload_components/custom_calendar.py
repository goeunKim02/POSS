from PyQt5.QtWidgets import QCalendarWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QLocale


class CustomCalendarWidget(QCalendarWidget):
    """커스텀 캘린더 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 영어 로케일 설정
        english_locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.setLocale(english_locale)

        # 기본 설정
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)

        # 폰트 설정
        font = QFont("Arial", 9)
        self.setFont(font)

        # 스타일시트 적용
        self.setStyleSheet("""
            /* 전체 캘린더 배경 */
            QCalendarWidget {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 10px;
            }

            /* 날짜 그리드 */
            QCalendarWidget QTableView {
                alternate-background-color: #F1F1F1;
                background-color: white;
                selection-background-color: #1428A0;
                selection-color: white;
            }

            /* 헤더 (요일 표시 부분) */
            QCalendarWidget QTableView QHeaderView {
                background-color: #1428A0;
                color: white;
            }

            /* 네비게이션 바 (월/년 선택 부분) */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1428A0;
                color: white;
            }

            /* 네비게이션 바 버튼 */
            QCalendarWidget QToolButton {
                background-color: #1428A0;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }

            /* 버튼 호버 효과 */
            QCalendarWidget QToolButton:hover {
                background-color: #5c7fc1;
            }

            /* 월 표시 */
            QCalendarWidget QSpinBox {
                background-color: white;
                color: black;
                selection-background-color: #4b6eaf;
                selection-color: white;
            }
        """)