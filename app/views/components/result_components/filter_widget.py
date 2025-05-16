from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QCheckBox, QScrollArea, QPushButton, QFrame,
                            QToolButton, QMenu, QAction, QWidgetAction)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QCursor, QIcon

"""필터 위젯 - 라인 및 프로젝트 선택 필터"""
class FilterWidget(QWidget):
    
    # 필터 변경 시그널
    filter_changed = pyqtSignal(dict)  # {필터타입: {선택된 값들}}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_states = {
            'line': {},    # 선택된 라인 정보 저장
            'project': {}  # 선택된 프로젝트 정보 저장
        }
        
        # 필터 데이터
        self.filter_data = {
            'line': [],    # 사용 가능한 라인 목록
            'project': []  # 사용 가능한 프로젝트 목록
        }
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # 라인 필터 버튼
        self.line_filter_btn = QToolButton(self)
        self.line_filter_btn.setText("Line")
        self.line_filter_btn.setStyleSheet("""
            QToolButton {
                background-color: white;
                color: black;
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 4px;
                min-width: 120px;
                border: 1px solid #808080;
                margin-right: 10px;
            }
            QToolButton:hover {
                background-color: #f0f0f0;
            }
            QToolButton:pressed {
                background-color: #e0e0e0;
            }
        """)

        self.line_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.line_filter_btn.setPopupMode(QToolButton.InstantPopup)
        
        # 라인 필터 메뉴 생성
        self.line_filter_menu = QMenu(self.line_filter_btn)
        self.line_filter_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #d0d0d0;
                padding: 5px;
                min-width: 250px;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
            QMenu::separator {
                height: 1px;
                background-color: #d0d0d0;
                margin: 5px 15px;
            }
        """)
        
        # 메뉴 헤더 위젯 (Select All/Clear All 버튼)
        line_menu_header = QWidget()
        line_menu_header.setStyleSheet("background-color: transparent; border: none;")
        line_menu_header.setMinimumWidth(300)
        line_header_layout = QHBoxLayout(line_menu_header)
        line_header_layout.setContentsMargins(5, 2, 5, 5)
        
        select_all_line_btn = QPushButton("Select All")
        select_all_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 120px;
                border: none;
            }
            QPushButton:hover {
                background-color: #004C99;
            }
        """)
        select_all_line_btn.setCursor(QCursor(Qt.PointingHandCursor))
        select_all_line_btn.clicked.connect(lambda: self.select_all_filters('line'))
        
        clear_all_line_btn = QPushButton("Clear All")
        clear_all_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 120px;
                border: none;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)
        clear_all_line_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_all_line_btn.clicked.connect(lambda: self.clear_all_filters('line'))
        
        line_header_layout.addWidget(select_all_line_btn)
        line_header_layout.addWidget(clear_all_line_btn)
        
        # 헤더 위젯을 액션으로 추가
        line_header_action = QWidgetAction(self.line_filter_menu)
        line_header_action.setDefaultWidget(line_menu_header)
        self.line_filter_menu.addAction(line_header_action)
        
        # 구분선 추가
        self.line_filter_menu.addSeparator()
        
        # 라인 체크박스 컨테이너
        self.line_checkbox_container = QWidget()
        self.line_checkbox_container.setStyleSheet("background-color: white; border: none;")
        self.line_checkbox_layout = QVBoxLayout(self.line_checkbox_container)
        self.line_checkbox_layout.setContentsMargins(5, 5, 5, 5)
        self.line_checkbox_layout.setSpacing(4)
        
        # 체크박스 컨테이너를 스크롤 영역에 넣기
        line_scroll = QScrollArea()
        line_scroll.setWidgetResizable(True)
        line_scroll.setWidget(self.line_checkbox_container)
        line_scroll.setStyleSheet("background-color: white; border: none;")
        line_scroll.setMaximumHeight(200)  # 최대 높이 제한
        line_scroll.setMinimumWidth(300)
        
        # 스크롤 영역을 액션으로 추가
        line_scroll_action = QWidgetAction(self.line_filter_menu)
        line_scroll_action.setDefaultWidget(line_scroll)
        self.line_filter_menu.addAction(line_scroll_action)
        
        self.line_filter_btn.setMenu(self.line_filter_menu)
        
        # 프로젝트 필터 버튼
        self.project_filter_btn = QToolButton(self)
        self.project_filter_btn.setText("Project")
        self.project_filter_btn.setStyleSheet("""
            QToolButton {
                background-color: white;  /* 배경색을 흰색으로 변경 */
                color: black;  /* 텍스트 색을 검은색으로 변경 */
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 4px;
                min-width: 120px;
                border: 1px solid #808080;  /* 테두리 색상을 회색으로 통일 */
            }
            QToolButton:hover {
                background-color: #f0f0f0;
            }
            QToolButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self.project_filter_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.project_filter_btn.setPopupMode(QToolButton.InstantPopup)
        
        # 프로젝트 필터 메뉴
        self.project_filter_menu = QMenu(self.project_filter_btn)
        self.project_filter_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #d0d0d0;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px 5px 10px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
        """)
        
        # 메뉴 헤더 위젯
        project_menu_header = QWidget()
        project_menu_header.setStyleSheet("background-color: transparent; border: none;")
        project_menu_header.setMinimumWidth(300)
        project_header_layout = QHBoxLayout(project_menu_header)
        project_header_layout.setContentsMargins(5, 2, 5, 5)
        
        select_all_project_btn = QPushButton("Select All")
        select_all_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 120px;
                border: none;
            }
            QPushButton:hover {
                background-color: #004C99;
            }
        """)
        select_all_project_btn.setCursor(QCursor(Qt.PointingHandCursor))
        select_all_project_btn.clicked.connect(lambda: self.select_all_filters('project'))
        
        clear_all_project_btn = QPushButton("Clear All")
        clear_all_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 120px;
                border: none;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)
        clear_all_project_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_all_project_btn.clicked.connect(lambda: self.clear_all_filters('project'))
        
        project_header_layout.addWidget(select_all_project_btn)
        project_header_layout.addWidget(clear_all_project_btn)
        
        # 헤더 위젯을 액션으로 추가
        project_header_action = QWidgetAction(self.project_filter_menu)
        project_header_action.setDefaultWidget(project_menu_header)
        self.project_filter_menu.addAction(project_header_action)
        
        # 구분선 추가
        self.project_filter_menu.addSeparator()
        
        # 프로젝트 체크박스 컨테이너
        self.project_checkbox_container = QWidget()
        self.project_checkbox_container.setStyleSheet("background-color: white; border: none;")
        self.project_checkbox_layout = QVBoxLayout(self.project_checkbox_container)
        self.project_checkbox_layout.setContentsMargins(5, 5, 5, 5)
        self.project_checkbox_layout.setSpacing(4)
        
        # 체크박스 컨테이너를 스크롤 영역에 넣기
        project_scroll = QScrollArea()
        project_scroll.setWidgetResizable(True)
        project_scroll.setWidget(self.project_checkbox_container)
        project_scroll.setStyleSheet("background-color: white; border: none;")
        project_scroll.setMaximumHeight(200)  # 최대 높이 제한
        project_scroll.setMinimumWidth(300)
        
        # 스크롤 영역을 액션으로 추가
        project_scroll_action = QWidgetAction(self.project_filter_menu)
        project_scroll_action.setDefaultWidget(project_scroll)
        self.project_filter_menu.addAction(project_scroll_action)
        
        self.project_filter_btn.setMenu(self.project_filter_menu)
        
        # 버튼 추가
        main_layout.addWidget(self.line_filter_btn)
        main_layout.addWidget(self.project_filter_btn)
        
        # 위젯 스타일
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QCheckBox {
                font-size: 9pt;
                background-color: white;
                border: none;
                padding: 2px;
            }
            QCheckBox:hover {
                color: #1428A0;
            }
        """)
            
    """필터 데이터 설정"""
    def set_filter_data(self, lines=None, projects=None):
        max_width = 250

        if lines:
            # 모든 라인을 문자열로 변환하여 저장
            self.filter_data['line'] = sorted([str(line) for line in lines])
            self.update_line_filters()
            
        if projects:
            # 모든 프로젝트를 문자열로 변환하여 저장
            self.filter_data['project'] = sorted([str(project) for project in projects])
            self.update_project_filters()
    
    """라인 필터 체크박스 업데이트"""
    def update_line_filters(self):
        # 기존 체크박스 정리
        self._clear_layout(self.line_checkbox_layout)
        
        # 체크박스 생성
        for line in self.filter_data['line']:
            checkbox = QCheckBox(str(line))
            checkbox.setChecked(True)  # 기본값은 체크된 상태
            checkbox.setStyleSheet("""
                QCheckBox {
                    background-color: white;
                    border: none;
                    padding: 3px;
                }
            """)
            self.filter_states['line'][line] = True
            checkbox.stateChanged.connect(
                lambda state, line=line: self.on_filter_changed('line', line, state == Qt.Checked))
            self.line_checkbox_layout.addWidget(checkbox)
        
        # "Line (x)" 형식으로 버튼 텍스트 업데이트
        self.line_filter_btn.setText(f"Line ({len(self.filter_data['line'])})")

    """프로젝트 필터 체크박스 업데이트"""
    def update_project_filters(self):
        # 기존 체크박스 정리
        self._clear_layout(self.project_checkbox_layout)
        
        # 체크박스 생성
        for project in self.filter_data['project']:
            checkbox = QCheckBox(str(project))
            checkbox.setChecked(True)  # 기본값은 체크된 상태
            checkbox.setStyleSheet("""
                QCheckBox {
                    background-color: white;
                    border: none;
                    padding: 3px;
                }
            """)
            self.filter_states['project'][project] = True
            checkbox.stateChanged.connect(
                lambda state, proj=project: self.on_filter_changed('project', proj, state == Qt.Checked))
            self.project_checkbox_layout.addWidget(checkbox)
        
        # "Project (x)" 형식으로 버튼 텍스트 업데이트
        self.project_filter_btn.setText(f"Project ({len(self.filter_data['project'])})")
    
    """레이아웃 내 위젯 모두 제거"""
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    """필터 상태 변경 처리"""
    def on_filter_changed(self, filter_type, value, is_checked):
        # 값이 숫자인 경우에도 문자열로 처리하여 일관성 유지
        if isinstance(value, (int, float)):
            value = str(value)
            
        self.filter_states[filter_type][value] = is_checked
        self.filter_changed.emit(self.filter_states.copy())
    
    """특정 필터 유형의 모든 필터 선택"""
    def select_all_filters(self, filter_type):
        if filter_type == 'line':
            layout = self.line_checkbox_layout
        else:
            layout = self.project_checkbox_layout
            
        # 모든 체크박스 선택
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                checkbox = item.widget()
                checkbox.setChecked(True)
                
        # 필터 상태 업데이트
        for key in self.filter_states[filter_type]:
            self.filter_states[filter_type][key] = True
                
        # 필터 변경 신호 발생
        self.filter_changed.emit(self.filter_states.copy())
    
    """특정 필터 유형의 모든 필터 해제"""
    def clear_all_filters(self, filter_type):
        if filter_type == 'line':
            layout = self.line_checkbox_layout
        else:
            layout = self.project_checkbox_layout
            
        # 모든 체크박스 해제
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                checkbox = item.widget()
                checkbox.setChecked(False)
                
        # 필터 상태 업데이트
        for key in self.filter_states[filter_type]:
            self.filter_states[filter_type][key] = False
                
        # 필터 변경 신호 발생
        self.filter_changed.emit(self.filter_states.copy())