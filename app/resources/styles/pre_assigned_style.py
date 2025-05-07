# 버튼 스타일
PRIMARY_BUTTON_STYLE = """
QPushButton {
    background-color: #1428A0;
    color: white;
    padding: 8px 10px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #004C99;
}
QPushButton:pressed {
    background-color: #003366;
}
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    background-color: #ACACAC;
    color: white;
    padding: 8px 10px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #C0C0C0;
}
QPushButton:pressed {
    background-color: #848282;
}
"""

# 캘린더 헤더의 요일 레이블 스타일
WEEKDAY_HEADER_STYLE = """
background-color: #cccccc;
color: black;
font-weight: bold;
padding: 10px;
font-size: 14px;
"""

# 구분선 스타일
SEPARATOR_STYLE = """
background-color: #dcdcdc;
border: none;
"""

# 라인 이름 레이블 스타일
LINE_LABEL_STYLE = """
background-color: #1428A0;
color: white;
font-weight: bold;
padding: 8px;
font-size: 13px;
"""

# Day/Night 레이블 스타일
DAY_LABEL_STYLE = """
font-size: 13px;
color: #006400;
font-weight: bold;
padding: 6px;
"""

NIGHT_LABEL_STYLE = """
font-size: 13px;
color: #8B0000;
font-weight: bold;
padding: 6px;
"""

# Day/Night 카드 프레임 스타일
CARD_DAY_FRAME_STYLE = """
QFrame#cardFrameDay {
    background-color: #E8F5E9;
    border: 1px solid #A5D6A7;
    border-radius: 4px;
}
QFrame#cardFrameDay:hover {
    background-color: #C8E6C9;
    border: 1px solid #81C784;
}
QFrame#cardFrameDay:pressed {
    background-color: #A5D6A7;
    border: 1px solid #4CAF50;
}
QFrame#cardFrameDay QLabel {
    background-color: transparent;
}
"""

CARD_NIGHT_FRAME_STYLE = """
QFrame#cardFrameNight {
    background-color: #FFEBEE;
    border: 1px solid #EF9A9A;
    border-radius: 4px;
}
QFrame#cardFrameNight:hover {
    background-color: #FFCDD2;
    border: 1px solid #E57373;
}
QFrame#cardFrameNight:pressed {
    background-color: #EF9A9A;
    border: 1px solid #F44336;
}
QFrame#cardFrameNight QLabel {
    background-color: transparent;
}
"""

# 상세정보 스타일
DETAIL_DIALOG_STYLE = """
QDialog {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}
"""

DETAIL_LABEL_TRANSPARENT = """
QLabel {
    background-color: transparent;
}
"""

DETAIL_FRAME_TRANSPARENT = """
QFrame {
    background-color: transparent;
}
"""

# 필드 이름 레이블 스타일
DETAIL_FIELD_NAME_STYLE = """
QLabel.field-name {
    background-color: transparent;
    font-weight: bold;
    color: #555;
}
"""

# 필드 값 레이블 스타일
DETAIL_FIELD_VALUE_STYLE = """
QLabel.field-value {
    background-color: transparent;
    color: #333;
}
"""

# 상세정보 버튼 스타일
DETAIL_BUTTON_STYLE = """
QPushButton {
    padding: 6px 12px;
    border-radius: 4px;
    background-color: #1428A0;
    color: white;
}
QPushButton:hover {
    background-color: #004C99;
}
QPushButton:pressed {
    background-color: #003366;
}
"""