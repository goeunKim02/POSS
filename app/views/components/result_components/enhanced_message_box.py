from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from app.resources.styles.pre_assigned_style import PRIMARY_BUTTON_STYLE

"""메시지 박스 클래스"""
class EnhancedMessageBox:
    
    """검증 오류 메시지 박스 표시"""
    @staticmethod
    def show_validation_error(parent, title, message):
        msg_box = QMessageBox(parent)
        
        # 제목과 텍스트 설정
        msg_box.setWindowTitle(title)
        msg_box.setInformativeText(message)
        
        # 아이콘 설정
        msg_box.setIcon(QMessageBox.Warning)
        
        # 창 크기를 충분히 크게 만들기 위해 최소 너비 설정
        msg_box.setMinimumWidth(500)  # 크기 증가
        msg_box.setMinimumHeight(350)  # 크기 증가

        # 버튼 스타일 - 에러용 빨간색 버튼
        button_style = """
            QPushButton {
                background-color: #DC3545;  /* 에러 메시지는 빨간색 */
                color: white;
                border-radius: 10px;
                min-width: 80px;  /* 버튼 크기 증가 */
                min-height: 30px;  /* 버튼 크기 증가 */
                padding: 8px 15px;
                font-size: 22px;  /* 버튼 텍스트 크기 증가 */
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #C82333;  /* 빨간색 hover */
            }
            QPushButton:pressed {
                background-color: #BD2130;  /* 빨간색 pressed */
            }
        """
        
        # 스타일 적용 - 에러는 빨간색 테마로 변경
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                border: 2px solid #DC3545;  /* 빨간색 테두리 */
                border-radius: 6px;
                font-family: Arial;
            }}
            QLabel {{
                color: #333333;
                font-size: 26px;  /* 텍스트 크기 증가 */
                padding: 15px;  /* 패딩 증가 */
                border: none;
                min-width: 400px;  /* 너비 증가 */
            }}
            /* 헤더 텍스트 (첫 번째 라벨) */
            QLabel:first {{
                font-size: 30px;  /* 헤더 텍스트 크기 증가 */
                color: #DC3545;  /* 에러 메시지는 빨간색 */
            }}
            {button_style}
        """)
        
        # 폰트 설정 - 굵기 제거
        title_font = QFont("Arial", 26)  
        msg_box.setFont(title_font)
        
        # 버튼 커스터마이징
        for button in msg_box.buttons():
            button_font = QFont("Arial", 22)
            button_font.setBold(True)  # 버튼 텍스트는 굵게 설정
            button.setFont(button_font)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumSize(80, 50)  # 크기 증가
        
        # 실행
        return msg_box.exec_()
    
    
    """검증 성공 메시지 박스 표시"""
    @staticmethod
    def show_validation_success(parent, title, message):
        msg_box = QMessageBox(parent)
        
        # 제목과 텍스트 설정
        msg_box.setWindowTitle(title)
        msg_box.setInformativeText(message)
        
        # 아이콘 설정
        msg_box.setIcon(QMessageBox.Information)
        
        # 창 크기를 충분히 크게 만들기 위해 최소 너비 설정
        msg_box.setMinimumWidth(500)  # 크기 증가
        msg_box.setMinimumHeight(350)  # 크기 증가

        # 버튼 스타일 - 성공용 파란색 버튼
        button_style = """
            QPushButton {
                background-color: #1428A0;  /* 성공 메시지는 파란색 */
                color: white;
                border-radius: 10px;
                min-width: 80px;  /* 버튼 크기 증가 */
                min-height: 30px;  /* 버튼 크기 증가 */
                padding: 8px 15px;
                font-size: 22px;  /* 버튼 텍스트 크기 증가 */
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #004C99;
            }
            QPushButton:pressed {
                background-color: #003366;
            }
        """
        
        # 스타일 적용 - 성공은 파란색 테마로 변경
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                border: 2px solid #1428A0;  /* 파란색 테두리 */
                border-radius: 6px;
                font-family: Arial;
            }}
            QLabel {{
                color: #333333;
                font-size: 26px;  /* 텍스트 크기 증가 */
                padding: 15px;  /* 패딩 증가 */
                border: none;
                min-width: 500px;  /* 너비 증가 */
            }}
            /* 헤더 텍스트 (첫 번째 라벨) */
            QLabel:first {{
                font-size: 30px;  /* 헤더 텍스트 크기 증가 */
                color: #1428A0;  /* 성공 메시지는 파란색 */
            }}
            {button_style}
        """)
        
        # 폰트 설정 - 굵기 제거
        title_font = QFont("Arial", 26)  
        msg_box.setFont(title_font)
        
        # 버튼 커스터마이징
        for button in msg_box.buttons():
            button_font = QFont("Arial", 22)
            button_font.setBold(True)  
            button.setFont(button_font)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumSize(80, 50)  
        
        # 실행
        return msg_box.exec_()