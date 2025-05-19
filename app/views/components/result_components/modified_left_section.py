from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog,
                             QLineEdit, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QCursor
import pandas as pd
from .item_grid_widget import ItemGridWidget
from .item_position_manager import ItemPositionManager
from app.views.components.common.enhanced_message_box import EnhancedMessageBox
from app.models.common.file_store import FilePaths
from .legend_widget import LegendWidget
from .filter_widget import FilterWidget
from app.utils.fileHandler import load_file
from app.utils.item_key_manager import ItemKeyManager
from app.resources.fonts.font_manager import font_manager
from app.models.common.screen_manager import *

class ModifiedLeftSection(QWidget):
    # 데이터 변경을 통합해서 한 번만 내보내는 시그널
    viewDataChanged = pyqtSignal(pd.DataFrame)  # 수정 후 변경된 DataFrame을 전달
    item_selected = pyqtSignal(object, object)
    itemModified = pyqtSignal(object, dict, dict)
    cellMoved = pyqtSignal(object, dict, dict)
    validation_error_occured = pyqtSignal(dict, str)
    validation_error_resolved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = None
        self.data = None
        self.original_data = None
        self.grouped_data = None
        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.time_periods = ['Day', 'Night']
        self.pre_assigned_items = set()  # 사전할당된 아이템 저장
        self.shipment_failure_items = {}  # 출하 실패 아이템 저장
        self.init_ui()

        # MVC 컴포넌트 초기화
        self.controller = None
        self.validator = None

        # 아이템 이동을 위한 정보 저장
        self.row_headers = []

        # 검색 관련 변수
        self.search_active = False
        self.last_search_text = ''
        self.all_items = []
        self.search_results = []
        self.current_result_index = -1

        if not hasattr(self, 'current_selected_item'):
            self.current_selected_item = None
        if not hasattr(self, 'current_selected_container'):
            self.current_selected_container = None

        # 필터 상태 저장 
        self.current_filter_states = {
            'shortage': False,
            'shipment': False,  
            'pre_assigned': False
        }

        # 엑셀 스타일 필터 상태 저장 (새로 추가된 부분)
        self.current_excel_filter_states = {
            'line': {},
            'project': {}
        }

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 범례 위젯 추가
        self.legend_widget = LegendWidget()
        self.legend_widget.filter_changed.connect(self.on_filter_changed)
        self.legend_widget.filter_activation_requested.connect(self.on_filter_activation_requested)
        main_layout.addWidget(self.legend_widget)

        # 통합 컨트롤 레이아웃 (버튼, 필터, 검색 섹션을 한 줄에 배치)
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(w(5))

        # 왼쪽 버튼 섹션 (Import/Reset)
        button_section = QHBoxLayout()
        button_section.setSpacing(10)

        bold_font = font_manager.get_just_font("SamsungSharpSans-Bold").family()
        normal_font = font_manager.get_just_font("SamsungOne-700").family()

        # 엑셀 파일 불러오기 버튼 - 길이 증가
        self.load_button = QPushButton("Import Excel")
        self.load_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #1428A0;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: {w(80)}px;
                border:none;
                font-family:{normal_font};
                font-size: {f(16)}px;
                min-height: {h(28)}px;
            }}
            QPushButton:hover {{
                background-color: #004C99;
            }}
            QPushButton:pressed {{
                background-color: #003366;
            }}
        """)
        self.load_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.load_button.clicked.connect(self.load_excel_file)
        button_section.addWidget(self.load_button)

        # 원본 복원 버튼 
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #808080;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: {w(80)}px;
                border:none;
                font-family:{normal_font};
                font-size: {f(16)}px;
                min-height: {h(28)}px;
            }}
            QPushButton:hover {{
                background-color: #606060;
            }}
            QPushButton:pressed {{
                background-color: #404040;
            }}
        """)
        self.reset_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_button.clicked.connect(self.reset_to_original)
        self.reset_button.setEnabled(False)
        button_section.addWidget(self.reset_button)

        # 버튼 섹션을 통합 레이아웃에 추가 (왼쪽에 붙이기)
        control_layout.addLayout(button_section)
        
        # 가운데 여백 추가
        control_layout.addStretch(1)  # 가운데 여백 추가

        # 필터 위젯 추가 - Line과 Project 버튼 간격 조정 및 스타일 변경
        self.filter_widget = FilterWidget()
        self.filter_widget.filter_changed.connect(self.on_excel_filter_changed)
        # self.filter_widget.setFixedWidth(400)
        control_layout.addWidget(self.filter_widget)
        control_layout.addStretch(1)

        # 검색 섹션 - 오른쪽에 붙이기
        search_section = QHBoxLayout()
        search_section.setSpacing(5)

        # 검색 필드 수정 - 크기 증가
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('searching...')
        self.search_field.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #808080;  /* 테두리 색상 통일 */
                border-radius: 4px;
                background-color: white;
                selection-background-color: #1428A0;
                font-size: {f(16)}px;
                padding: 6px 8px;
                font-family:{normal_font};
                min-height: {h(30)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid #1428A0;
            }}
        """)
        self.search_field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.search_field.setFixedWidth(w(250))  # 검색 박스 폭 더 증가
        # self.search_field.setFixedHeight(36)
        self.search_field.returnPressed.connect(self.search_items)
        search_section.addWidget(self.search_field)

        # 검색 버튼
        self.search_button = QPushButton('Search')
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #1428A0;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: {w(80)}px;
                border:none;
                font-family:{normal_font};
                font-size: {f(16)}px;
                min-height: {h(28)}px;
            }}
            QPushButton:hover {{
                background-color: #004C99;
            }}
            QPushButton:pressed {{
                background-color: #003366;
            }}
        """)

        self.search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_button.clicked.connect(self.search_items)
        search_section.addWidget(self.search_button)

        # 검색 초기화 버튼
        self.clear_search_button = QPushButton('Reset')
        self.clear_search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #808080;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: {w(80)}px;
                border:none;
                font-family:{normal_font};
                font-size: {f(16)}px;
                min-height: {h(28)}px;
            }}
            QPushButton:hover {{
                background-color: #606060;
            }}
            QPushButton:pressed {{
                background-color: #404040;
            }}
        """)
        self.clear_search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setEnabled(False)
        search_section.addWidget(self.clear_search_button)

        # 검색 섹션을 통합 레이아웃에 추가 (오른쪽에 붙이기)
        control_layout.addLayout(search_section)

        # 통합 컨트롤 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(control_layout)

        # 검색 상태 표시 레이아웃
        self.search_status_layout = QHBoxLayout()
        self.search_status_layout.setContentsMargins(10, 0, 10, 5)

        # 결과 이동을 위한 버튼
        self.prev_result_button = QPushButton('◀')
        self.prev_result_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #1428A0;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
                min-width: 30px;
                max-width: 30px;
                border: 1px solid #d0d0d0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                color: #a0a0a0;
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
            }
        """)
        self.prev_result_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_result_button.clicked.connect(self.go_to_prev_result)
        self.prev_result_button.setEnabled(False)

        # 검색 결과 수 표시
        self.search_result_label = QLabel('')
        self.search_result_label.setStyleSheet("""
            QLabel {
                color: #1428A0;
                font-weight: bold;
                font-size: 13px;
                border: None;
                padding: 0 5px;
            }
        """)

        # 다음 버튼
        self.next_result_button = QPushButton('▶')
        self.next_result_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #1428A0;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
                min-width: 30px;
                max-width: 30px;
                border: 1px solid #d0d0d0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                color: #a0a0a0;
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
            }
        """)

        self.next_result_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_result_button.clicked.connect(self.go_to_next_result)
        self.next_result_button.setEnabled(False)

        self.search_status_layout.addStretch(1)
        self.search_status_layout.addWidget(self.search_result_label)
        self.search_status_layout.addWidget(self.prev_result_button)
        self.search_status_layout.addWidget(self.next_result_button)

        self.search_result_label.hide()
        self.prev_result_button.hide()
        self.next_result_button.hide()

        main_layout.addLayout(self.search_status_layout)

        # 새로운 그리드 위젯 추가
        self.grid_widget = ItemGridWidget()
        self.grid_widget.itemSelected.connect(self.on_grid_item_selected)  # 아이템 선택 이벤트 연결
        self.grid_widget.itemDataChanged.connect(self.on_item_data_changed)  # 아이템 데이터 변경 이벤트 연결
        self.grid_widget.itemCreated.connect(self.register_item)
        self.grid_widget.itemRemoved.connect(self.on_item_removed)
        self.grid_widget.itemCopied.connect(self.on_item_copied)  # 아이템 복사 이벤트 연결 
        main_layout.addWidget(self.grid_widget, 1)

    
    """
    데이터프레임 타입 정규화
    """
    def _normalize_data_types(self, df):
        if df is not None and not df.empty:
            # Line은 항상 문자열
            if 'Line' in df.columns:
                df['Line'] = df['Line'].astype(str)
            
            # Time은 항상 정수
            if 'Time' in df.columns:
                df['Time'] = pd.to_numeric(df['Time'], errors='coerce').fillna(0).astype(int)
            
            # Item은 항상 문자열
            if 'Item' in df.columns:
                df['Item'] = df['Item'].astype(str)
            
            # Qty는 항상 정수
            if 'Qty' in df.columns:
                df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
        
        return df
    

    """
    새로 생성된 아이템 등록
    """
    def register_item(self, item) :
        if item not in self.all_items :
            self.all_items.append(item)

            if self.search_active and self.last_search_text :
                self.apply_search_to_item(item, self.last_search_text)

    """
    엑셀 스타일 필터 상태 변경 처리
    """
    def on_excel_filter_changed(self, filter_states):
        self.current_excel_filter_states = filter_states
        self.apply_all_filters()

    """
    모든 필터 (범례 & 엑셀 스타일) 적용
    """
    def apply_all_filters(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return

        excel_filter_active = (any(not all(states.values()) for states in self.current_excel_filter_states.values())
                            if hasattr(self, 'current_excel_filter_states') else False)
        
        # 현재 검색 상태 저장
        search_active = self.search_active
        search_text = self.last_search_text
                
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    # 아이템 표시 상태 기본값: 표시
                    should_show_item = True
                    
                    # 1. 상태선(범례) 표시 업데이트 - 라벨만 업데이트, 아이템 가시성은 변경 안함
                    self.update_item_status_line_visibility(item)
                    
                    # 2. 엑셀 스타일 필터 적용
                    if excel_filter_active:
                        should_show_item = self.should_show_item_excel_filter(item)
                    
                    # 3. 검색 필터 적용 (검색 활성화 상태일 때)
                    if should_show_item and search_active and search_text:
                        # 검색 조건에 맞는지 확인
                        if hasattr(item, 'item_data') and item.item_data:
                            item_code = str(item.item_data.get('Item', '')).lower()
                            should_show_item = search_text in item_code
                    
                    # 최종 표시 상태 적용
                    item.setVisible(should_show_item)
                    
                # 컨테이너 높이 재조정
                container.adjustSize()
        
        # 검색 결과가 있고 활성화된 상태라면 검색 결과 UI 업데이트
        if search_active and self.search_results:
            self.update_result_navigation()

    """
    엑셀 필터를 고려한 아이템 표시 여부
    """
    def should_show_item_excel_filter(self, item):
        if not hasattr(self, 'current_excel_filter_states') or not hasattr(item, 'item_data'):
            return True
        
        item_data = item.item_data
        
        # 라인 필터 체크 - Line 컬럼 사용
        if 'Line' in item_data:
            line = item_data['Line']

            if isinstance(line, (int, float)):
                line = str(int(line))  # 숫자인 경우 문자열로 변환
            else:
                line = str(line)
                
            if line in self.current_excel_filter_states['line'] and not self.current_excel_filter_states['line'][line]:
                return False
        
        # 프로젝트 필터 체크 - Project 컬럼 사용
        if 'Project' in item_data:
            project = item_data['Project']

            if pd.isna(project):  # nan 값 처리
                project = "N/A"
            else:
                project = str(project)
                
            if project in self.current_excel_filter_states['project'] and not self.current_excel_filter_states['project'][project]:
                return False
        
        return True
    
    """필터 활성화 요청 처리"""
    def on_filter_activation_requested(self, status_type):
        # 출하 상태 필터가 활성화된 경우
        if status_type == 'shipment':
            # 현재 데이터가 있는지 확인
            if self.data is not None and not self.data.empty:
                # 결과 페이지 참조 찾기
                result_page = self.parent_page
                if result_page and hasattr(result_page, 'analyze_shipment_with_current_data'):
                    # 현재 데이터로 출하 분석 실행 요청
                    result_page.analyze_shipment_with_current_data(self.data)
    
    """
    데이터 로드 후 필터 데이터 업데이트
    """
    def update_filter_data(self):
        if self.data is None:
            return
        
        # 라인 목록 추출 - Line 컬럼에서 추출
        lines = []
        if 'Line' in self.data.columns:
            # 숫자 형태의 라인도 문자열로 통일
            lines = [str(line) if not pd.isna(line) else "N/A" for line in self.data['Line']]
            lines = sorted(set(lines))  # 중복 제거하고 정렬
        
        # 프로젝트 목록 추출 - Project 컬럼에서 추출
        projects = []
        if 'Project' in self.data.columns:
            # nan 값 처리 및 문자열 변환
            projects = [str(project) if not pd.isna(project) else "N/A" for project in self.data['Project']]
            projects = sorted(set(projects))  # 중복 제거하고 정렬
        
        # 필터 위젯에 데이터 설정
        self.filter_widget.set_filter_data(lines, projects)

    """
    검색 기능 실행
    """
    def search_items(self) :
        search_text = self.search_field.text().strip().lower()

        if not search_text :
            self.clear_search()
            return
        
        self.search_active = True
        self.last_search_text = search_text
        self.clear_search_button.setEnabled(True)

        try:
            if hasattr(self.grid_widget, 'clear_all_selections'):
                self.grid_widget.clear_all_selections()
            self.current_selected_item = None
            self.current_selected_container = None
        except Exception as e:
            print(f"선택 초기화 오류: {e}")

        self.search_results = []
        self.current_result_index = -1

        invalid_items = []

        # 검색 조건에 맞는 아이템 찾기
        for item in self.all_items[:] :
            try:
                is_match = self.apply_search_to_item(item, search_text)
                if is_match:
                    self.search_results.append(item)
            except RuntimeError:
                invalid_items.append(item)
            except Exception as e:
                print(f"검색 중 오류 발생: {e}")
        
        # 잘못된 아이템 제거
        for item in invalid_items:
            if item in self.all_items:
                self.all_items.remove(item)

        # 모든 필터 재적용 (검색 포함)
        self.apply_all_filters()

        # 검색 결과 UI 업데이트
        self.search_result_label.show()
        self.prev_result_button.show()
        self.next_result_button.show()

        if self.search_results:
            self.current_result_index = 0
            self.select_current_result()
            self.update_result_navigation()
        else:
            self.search_result_label.setText('result: No matching items')
            self.prev_result_button.setEnabled(False)
            self.next_result_button.setEnabled(False)

    """
    아이템에 검색 조건 적용
    """
    def apply_search_to_item(self, item, search_text):
        try :
            if not item or not hasattr(item, 'item_data') or not item.item_data:
                return False
            
            try:
                _ = item.isVisible()
            except RuntimeError:
                if item in self.all_items:
                    self.all_items.remove(item)
                return False
            
            item_code = str(item.item_data.get('Item', '')).lower()
            is_match = search_text in item_code
            
            # 현재 필터 상태를 유지하며 검색 결과 적용
            # 아이템의 가시성을 직접 변경하지 않고 검색 결과만 반환
            return is_match
        except RuntimeError:
            return False
        except Exception as e:
            print(f"아이템 검색 중 오류: {e}")
            return False
    
    """
    검색 초기화
    """
    def clear_search(self):
        if not self.search_active:
            return
        
        self.search_active = False
        self.last_search_text = ''
        self.search_field.clear()
        self.clear_search_button.setEnabled(False)
        
        try:
            for item in self.all_items:
                if hasattr(item, 'set_search_focus'):
                    item.set_search_focus(False)
                    item.update()

            if hasattr(self.grid_widget, 'clear_all_selections'):
                self.grid_widget.clear_all_selections()
            self.current_selected_item = None
            self.current_selected_container = None
        except Exception as e:
            print(f"선택 초기화 오류: {e}")
        
        self.search_results = []
        self.current_result_index = -1
        
        self.search_result_label.hide()
        self.prev_result_button.hide()
        self.next_result_button.hide()
        
        # 검색을 제외한 다른 필터 상태를 유지하며 모든 필터 적용
        self.apply_all_filters()
        
        for item in self.all_items:
            try:
                item.setVisible(True)
            except RuntimeError:
                pass
            except Exception as e:
                print(f"아이템 표시 오류: {e}")
        
        try:
            if hasattr(self.grid_widget, 'update_container_visibility'):
                self.grid_widget.update_container_visibility()
        except Exception as e:
            print(f"컨테이너 가시성 업데이트 오류: {e}")

    """
    이전 검색 결과로 이동
    """
    def go_to_prev_result(self):
        if not self.search_results or self.current_result_index <= 0:
            return
        
        try:
            if self.current_result_index < len(self.search_results):
                current_item = self.search_results[self.current_result_index]
                
                if hasattr(current_item, 'set_search_focus'):
                    current_item.set_search_focus(False)
                    current_item.update()
            
            self.current_result_index -= 1
            self.select_current_result()
            self.update_result_navigation()
        except Exception as e:
            print(f"이전 결과 이동 오류: {str(e)}")

    """
    다음 검색 결과로 이동
    """
    def go_to_next_result(self):
        if not self.search_results or self.current_result_index >= len(self.search_results) - 1:
            return
        
        try:
            if self.current_result_index >= 0 and self.current_result_index < len(self.search_results):
                current_item = self.search_results[self.current_result_index]
                
                if hasattr(current_item, 'set_search_focus'):
                    current_item.set_search_focus(False)
                    current_item.update()
            
            self.current_result_index += 1
            self.select_current_result()
            self.update_result_navigation()
        except Exception as e:
            print(f"다음 결과 이동 오류: {str(e)}")

    """
    선택된 검색 결과를 포커스 
    """
    def select_current_result(self):
        if not self.search_results or not (0 <= self.current_result_index < len(self.search_results)):
            return
        
        try:
            for item in self.all_items:
                if hasattr(item, 'set_search_focus'):
                    item.set_search_focus(False)
                    item.update()

            current_item = self.search_results[self.current_result_index]
            container = current_item.parent()

            if hasattr(current_item, 'set_search_focus'):
                current_item.set_search_focus(True)
                current_item.update()

            if container:
                if hasattr(container, 'select_item'):
                    container.select_item(current_item)

                self.current_selected_container = container
                self.current_selected_item = current_item

                # self.item_selected.emit(current_item, container)
                df = self.extract_dataframe()
                self.viewDataChanged.emit(df)

                if hasattr(self.grid_widget, 'ensure_item_visible'):
                    self.grid_widget.ensure_item_visible(container, current_item)
        except Exception as e:
            print(f'항목 선택 오류 : {str(e)}')

    """
    검색 결과 상태 업데이트
    """
    def update_result_navigation(self):
        if not self.search_results:
            self.search_result_label.setText('result: No matching items')
            self.prev_result_button.setEnabled(False)
            self.next_result_button.setEnabled(False)
            return
        
        try:
            total_results = len(self.search_results)
            current_index = self.current_result_index + 1

            self.search_result_label.setText(f'<span style="font-size:26px;">result: {current_index}/{total_results}</span>')

            self.prev_result_button.setEnabled(self.current_result_index > 0)
            self.next_result_button.setEnabled(self.current_result_index < total_results - 1)
        except Exception as e :
            print(f'네이게이션 업데이트 오류 : {str(e)}')
            self.search_result_label.setText(f'result: {len(self.search_results)}')

    """
    그리드에서 아이템이 선택되면 호출되는 함수
    """
    def on_grid_item_selected(self, selected_item, container):
        # 현재 선택 상태 저장
        self.current_selected_item = selected_item
        self.current_selected_container = container

        # 선택 시그널 방출
        self.item_selected.emit(selected_item, container)

    """
    아이템 데이터가 변경되면 호출되는 함수
    """
    def on_item_data_changed(self, item, new_data, changed_fields=None):

        if not item or not new_data or not hasattr(item, 'item_data'):
            print("아이템 또는 데이터가 없음")
            return
        
        # 현재 아이템의 원래 위치 정보 확인
        original_data = item.item_data.copy() if hasattr(item, 'item_data') else {}
        
        # 위치 정보가 변경되지 않았다면 원래 위치 정보 사용
        if changed_fields and 'Line' not in changed_fields and 'Time' not in changed_fields:
            new_data['Line'] = original_data.get('Line', new_data.get('Line'))
            new_data['Time'] = original_data.get('Time', new_data.get('Time'))
        
        # MVC 컨트롤러가 있으면 시그널 발생 (
        if hasattr(self, 'controller') and self.controller:
            print("MVC 컨트롤러로 처리 - 시그널 발생")
            self.itemModified.emit(item, new_data, changed_fields)
            return

    """
    위치 변경 처리 로직 분리
    """
    def _handle_position_change(self, item, new_data, changed_fields, old_data):
        position_change_needed = False

        if changed_fields:
            if 'Time' in changed_fields:
                position_change_needed = True
                time_change = changed_fields['Time']
                old_time = time_change['from']
                new_time = time_change['to']

            if 'Line' in changed_fields:
                position_change_needed = True
                line_change = changed_fields['Line']
                old_line = line_change['from']
                new_line = line_change['to']

        if position_change_needed:
            # 위치 변경 로직 (기존 코드 유지)
            self._process_position_change(item, new_data, changed_fields, old_data)
        else:
            # 데이터만 업데이트
            if hasattr(item, 'update_item_data'):
                success, error_message = item.update_item_data(new_data)
                if not success:
                    print(f"아이템 데이터 업데이트 실패: {error_message}")
                    return

            self.mark_as_modified()
            self.itemModified.emit(item, new_data)

    """
    위치 변경 처리 (기존 로직 유지)
    """
    def _process_position_change(self, item, new_data, changed_fields, old_data):
        old_container = item.parent() if hasattr(item, 'parent') else None
        
        if not isinstance(old_container, QWidget):
            return

        # 변경된 Line과 Time에 따른 새 위치 계산
        line = new_data.get('Line')
        new_time = new_data.get('Time')

        if not line or not new_time:
            return

        # 위치 계산 로직 (기존 코드 유지)
        old_time = changed_fields.get('Time', {}).get('from', new_time) if changed_fields else new_time
        old_line = changed_fields.get('Line', {}).get('from', line) if changed_fields else line

        old_day_idx, old_shift = ItemPositionManager.get_day_and_shift(old_time)
        new_day_idx, new_shift = ItemPositionManager.get_day_and_shift(new_time)

        old_row_key = ItemPositionManager.get_row_key(old_line, old_shift)
        new_row_key = ItemPositionManager.get_row_key(line, new_shift)

        old_row_idx = ItemPositionManager.find_row_index(old_row_key, self.row_headers)
        new_row_idx = ItemPositionManager.find_row_index(new_row_key, self.row_headers)

        old_col_idx = ItemPositionManager.get_col_from_day_idx(old_day_idx, self.days)
        new_col_idx = ItemPositionManager.get_col_from_day_idx(new_day_idx, self.days)

        # 유효한 인덱스인 경우 아이템 이동
        if old_row_idx >= 0 and old_col_idx >= 0 and new_row_idx >= 0 and new_col_idx >= 0:
            # 이전 위치에서 아이템 제거
            if old_container:
                old_container.remove_item(item)

            # 새 위치에 아이템 추가
            item_text = str(new_data.get('Item', ''))
            if 'Qty' in new_data and pd.notna(new_data['Qty']):
                item_text += f"    {new_data['Qty']}"

            # 드롭 위치 정보 처리
            drop_index = 0
            if changed_fields and '_drop_pos' in changed_fields:
                try:
                    drop_pos_info = changed_fields['_drop_pos']
                    x = int(drop_pos_info['x'])
                    y = int(drop_pos_info['y'])
                    target_container = self.grid_widget.containers[new_row_idx][new_col_idx]
                    drop_index = target_container.findDropIndex(QPoint(x, y))
                except Exception as e:
                    drop_index = 0

            # 새 위치에 아이템 추가
            new_item = self.grid_widget.addItemAt(new_row_idx, new_col_idx, item_text, new_data, drop_index)

            if new_item:
                self.mark_as_modified()
                
                # 아이템 상태 복원
                self._restore_item_states(new_item, new_data)
                
                # 셀 이동 이벤트 발생
                self.cellMoved.emit(new_item, old_data, new_data)
            else:
                print("새 아이템 생성 실패")

    """
    아이템 상태 복원
    """
    def _restore_item_states(self, new_item, new_data):
        item_code = new_data.get('Item', '')
        
        # 사전할당 상태
        if item_code in self.pre_assigned_items:
            new_item.set_pre_assigned_status(True)
            
        # 출하 실패 상태
        if item_code in self.shipment_failure_items:
            failure_info = self.shipment_failure_items[item_code]
            new_item.set_shipment_failure(True, failure_info.get('reason', 'Unknown reason'))

        # 자재부족 상태
        if hasattr(self, 'current_shortage_items') and item_code in self.current_shortage_items:
            shortage_info = self.current_shortage_items[item_code]
            new_item.set_shortage_status(True, shortage_info)

    """
    MVC 컨트롤러 설정
    """
    def set_controller(self, controller):
        self.controller = controller
        print("MVC 컨트롤러가 설정되었습니다")

    """
    검증기 설정
    """
    def set_validator(self, validator):
        self.validator = validator
        if hasattr(self.grid_widget, 'set_validator'):
            self.grid_widget.set_validator(validator)
        print("검증기가 설정되었습니다")
        

    """
    엑셀 파일 로드
    """
    def load_excel_file(self):
        print("엑셀 파일 로드 시작")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            try:
                self.clear_all_items()
                print("clear_all_items()")

                loaded_result = load_file(file_path)
                print(f"로드 파일 결과 타입: {type(loaded_result)}")

                # 'result' 키에서 DataFrame 추출
                if isinstance(loaded_result, dict) and 'result' in loaded_result:
                    loaded_data = loaded_result['result']
                    print("'result' 키에서 데이터프레임 추출 성공")
                else:
                    # 이미 DataFrame이거나 다른 형태면 그대로 사용
                    loaded_data = loaded_result
                    print(f"로드된 데이터 타입: {type(loaded_data)}")
                
                # DataFrame 확인
                if not isinstance(loaded_data, pd.DataFrame):
                    print(f"오류: 데이터프레임이 아닌 타입: {type(loaded_data)}")
                    loaded_data = pd.DataFrame()  # 빈 데이터프레임 생성
                
                FilePaths.set("result_file", file_path)
                
                # 로드된 데이터가 비어있는지 확인
                if loaded_data.empty:
                    print("경고: 로드된 데이터가 비어있습니다.")
                    EnhancedMessageBox.show_validation_error(self, "파일 로드 문제", "로드된 데이터가 비어있습니다.")
                    return
                
                # # 데이터 컬럼 출력 (디버깅용)
                # print(f"로드된 데이터 컬럼: {loaded_data.columns.tolist()}")
                # print(f"로드된 데이터 첫 5행:\n{loaded_data.head()}")
                
                # 데이터 타입 안전하게 정규화
                try:
                    loaded_data = self._normalize_data_types(loaded_data)
                except Exception as type_error:
                    print(f"데이터 타입 정규화 중 오류: {type_error}")
                    # 기본 타입 변환만 시도
                    if 'Line' in loaded_data.columns:
                        loaded_data['Line'] = loaded_data['Line'].astype(str)
                    if 'Time' in loaded_data.columns:
                        loaded_data['Time'] = pd.to_numeric(loaded_data['Time'], errors='coerce').fillna(0).astype(int)
                
                # 현재 데이터와 원본 데이터 모두 저장
                self.data = loaded_data.copy()
                self.original_data = loaded_data.copy()
                print("데이터 복사: 현재/원본")

                # 컨터롤러 확인
                if hasattr(self, 'controller') and self.controller is not None:
                    print("컨트롤러 확인")
                    # 컨트롤러가 있는 경우, 모델을 새 데이터로 업데이트
                    if hasattr(self.controller, 'update_model_data'):
                        # 컨트롤러를 통해 모델 업데이트
                        success = self.controller.update_model_data(loaded_data)  # 변수 이름 변경
                        if success:
                            print("컨트롤러를 통해 모델 데이터 업데이트 완료")
                        else:
                            print("컨트롤러를 통한 모델 업데이트 실패")
                    else:
                        # update_model_data 메서드가 없는 경우, 직접 업데이트 시도
                        try:
                            self.controller.model._df = loaded_data.copy()  # 변수 이름 변경
                            self.controller.model._original_df = loaded_data.copy()  # 변수 이름 변경
                            self.controller.model.modelDataChanged.emit()
                            print("컨트롤러 모델 직접 업데이트 완료")
                        except Exception as e:
                            print(f"컨트롤러 모델 직접 업데이트 중 오류 발생: {e}")
                else:
                    print("컨트롤러 없음.")
                    # 컨트롤러가 없는 경우 직접 업데이트 
                    self.update_table_from_data()

                # 새로운 원본 상태가 있으므로 리셋 버튼 활성화
                self.reset_button.setEnabled(True)

                EnhancedMessageBox.show_validation_success(self, "File Loaded Successfully",
                                        f"File has been successfully loaded.\nRows: {self.data.shape[0]}, Columns: {self.data.shape[1]}")
            except Exception as e:
                EnhancedMessageBox.show_validation_error(self, "File Loding Error", f"An error occurred while loading the file.\n{str(e)}")

    """
    아이템 목록과 그리드 초기화하는 메서드
    """
    def clear_all_items(self) :
        self.all_items = []
        self.search_active = False
        self.last_search_text = ''
        self.search_field.clear()
        self.clear_search_button.setEnabled(False)
        self.search_result_label.hide()

        if hasattr(self, 'grid_widget'):
            self.grid_widget.clearAllItems()

    """
    엑셀 파일에서 데이터를 읽어와 테이블 업데이트
    """
    def update_table_from_data(self):
        if self.data is None:
            return

        self.update_ui_with_signals()

        # 데이터 변경 신호 발생
        # self.data_changed.emit(self.data)
        df = self.extract_dataframe()
        self.viewDataChanged.emit(df)

        self.preload_analyses()

    """데이터 로드 후 사전 분석 실행"""
    def preload_analyses(self):
        # 데이터가 없으면 건너뜀
        if self.data is None or self.data.empty:
            return
            
        # 결과 페이지 참조 확인
        result_page = self.parent_page
        if not result_page:
            return
            
        try:
            # 탭 위젯들 초기화 요청
            if hasattr(result_page, 'preload_tab_analyses'):
                result_page.preload_tab_analyses(self.data)
                
            # 범례에도 필터 상태 업데이트 알림
            if hasattr(self, 'legend_widget'):
                # 현재 필터 상태 가져오기
                current_states = self.legend_widget.filter_states
                
                # 강제로 필터 변경 이벤트 재발생
                self.on_filter_changed(current_states)
        except Exception as e:
            print(f"사전 분석 초기화 중 오류: {e}")

    """
    Line과 Time으로 데이터 그룹화하고 개별 아이템으로 표시
    """
    def update_ui_with_signals(self): 
        if self.data is None or 'Line' not in self.data.columns or 'Time' not in self.data.columns:
            EnhancedMessageBox.show_validation_error(self, "Grouping Failed",
                                "Data is missing or does not contain 'Line' or 'Time' columns.\nPlease load data with the required columns.")
            return

        try:
            # Line과 Time 값 추출
            lines = sorted(self.data['Line'].unique())
            times = sorted(self.data['Time'].unique())

            # 여기서는 원래 Line 값을 유지하고, 표시만 바뀌도록 처리
            # 내부적으로는 원래 라인명(예: "1", "A" 등)을 사용하되,
            # 화면에는 "ㅣ-01" 형식으로 표시

            # 교대 시간 구분
            shifts = {}
            for time in times:
                if int(time) % 2 == 1:
                    shifts[time] = "Day"
                else:
                    shifts[time] = "Night"

            # 라인별 교대 정보
            line_shifts = {}
            for line in lines:
                line_shifts[line] = ["Day", "Night"]

            # 행 헤더
            self.row_headers = []
            for line in lines:
                for shift in ["Day", "Night"]:
                    self.row_headers.append(f"{line}_({shift})")

            self.grid_widget.setupGrid(
                rows=len(self.row_headers),
                columns=len(self.days),
                row_headers=self.row_headers,
                column_headers=self.days,
                line_shifts=line_shifts  # 새로운 라인별 교대 정보 전달
            )

            # 각 요일과 라인/교대 별로 데이터 수집 및 그룹화
            for _, row_data in self.data.iterrows():
                if 'Line' not in row_data or 'Time' not in row_data:
                    continue

                line = row_data['Line']
                time = row_data['Time']
                shift = shifts[time]
                day_idx = (int(time) - 1) // 2

                if day_idx >= len(self.days):
                    continue

                day = self.days[day_idx]
                row_key = f"{line}_({shift})"

                # Item 정보가 있으면 추출하여 저장
                if 'Item' in row_data and pd.notna(row_data['Item']):
                    item_info = str(row_data['Item'])

                    # MFG 정보가 있으면 수량 정보로 추가
                    if 'Qty' in row_data and pd.notna(row_data['Qty']):
                        item_info += f"    {row_data['Qty']}"

                    try:
                        # 그리드에 아이템 추가
                        row_idx = self.row_headers.index(row_key)
                        col_idx = self.days.index(day)

                        # 전체 행 데이터를 아이템 데이터(dict 형태)로 전달
                        item_full_data = row_data.to_dict()
                        new_item = self.grid_widget.addItemAt(row_idx, col_idx, item_info, item_full_data)

                        if new_item:
                            item_code = item_full_data.get('Item', '')

                            # 사전할당 아이템인 경우
                            if item_code in self.pre_assigned_items:
                                new_item.set_pre_assigned_status(True)
                                
                            # 출하 실패 아이템인 경우
                            if item_code in self.shipment_failure_items:
                                item_code = item_full_data.get('Item')
                                failure_info = self.shipment_failure_items[item_code]
                                new_item.set_shipment_failure(True, failure_info.get('reason', 'Unknown reason'))

                            # 자재부족 아이템인 경우
                            if hasattr(self, 'current_shortage_items') and item_code in self.current_shortage_items:
                                shortage_info = self.current_shortage_items[item_code]
                                new_item.set_shortage_status(True, shortage_info)

                    except ValueError as e:
                        print(f"인덱스 찾기 오류: {e}")

            # 새로운 그룹화된 데이터 저장
            if 'Day' in self.data.columns:
                self.grouped_data = self.data.groupby(['Line', 'Day', 'Time']).first().reset_index()
            else:
                self.grouped_data = self.data.groupby(['Line', 'Time']).first().reset_index()

            # 데이터 변경 신호 발생
            # self.data_changed.emit(self.grouped_data)
            df = self.extract_dataframe()
            self.viewDataChanged.emit(df)
            
            # 필터 데이터 업데이트 (새로 추가된 부분)
            self.update_filter_data()

        except Exception as e:
            # 에러 메시지 표시
            print(f"그룹핑 에러: {e}")
            EnhancedMessageBox.show_validation_error(self, "Grouping Error", f"An error occurred during data grouping.\n{str(e)}")

    """
    외부에서 데이터 설정
    """
    def set_data_from_external(self, new_data):
        self.data = self._normalize_data_types(new_data.copy())
        self.original_data = self.data.copy()
        self.update_table_from_data()

    """
    원본 데이터로 되돌리기
    """
    def reset_to_original(self):
        if self.original_data is None:
            EnhancedMessageBox.show_validation_error(self, "Reset Failed", 
                                "No original data to reset to.")
            return
        
        # 사용자 확인 Dialog
        reply = EnhancedMessageBox.show_confirmation(
            self, "Reset to Original", "Are you sure you want to reset all changes and return to the original data?\nAll modifications will be lost."
        )

        if reply:
            # 원본 데이터로 복원
            self.data = self.original_data.copy()
            self.update_table_from_data()

            # Reset 버튼 비활성화
            self.reset_button.setEnabled(False)

            # 성공 메세지
            EnhancedMessageBox.show_validation_success(
                self, "Reset Complete", "Data has been successfully reset to the original values."
            )
    
    """
    데이터가 수정되었음을 표시하는 메서드
    """
    def mark_as_modified(self):
        self.reset_button.setEnabled(True)

    """
    현재 자재부족 아이템 정보 저장
    """
    def set_current_shortage_items(self, shortage_items):
        # 자재 부족 정보 저장
        self.current_shortage_items = shortage_items
        
        # 시프트 기반으로 자재 부족 상태 적용
        self.update_left_widget_shortage_status(shortage_items)

    """
    왼쪽 위젯의 아이템들에 자재 부족 상태 적용

    Args:
        shortage_dict: {item_code: [{shift: shift_num, material: material_code, shortage: shortage_amt}]}
    """
    def update_left_widget_shortage_status(self, shortage_dict):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
        
        print(f"자재 부족 상태 적용 시작: {len(shortage_dict)}개 아이템")
        status_applied_count = 0
        
        # 그리드의 모든 컨테이너 순회
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                # 각 컨테이너의 아이템들 순회
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']
                        item_time = item.item_data.get('Time')  # 시프트(Time) 정보 가져오기
                        
                        # 해당 아이템이 자재 부족 목록에 있는지 확인
                        if item_code in shortage_dict:
                            # 시프트별 부족 정보 검사
                            shortages_for_item = shortage_dict[item_code]
                            matching_shortages = []
                            
                            for shortage in shortages_for_item:
                                shortage_shift = shortage.get('shift')
                                
                                # 시프트가 일치하면 부족 정보 저장
                                if shortage_shift and item_time and int(shortage_shift) == int(item_time):
                                    matching_shortages.append(shortage)
                            
                            # 일치하는 시프트의 부족 정보가 있으면 부족 상태로 설정
                            if matching_shortages:
                                item.set_shortage_status(True, matching_shortages)
                                status_applied_count += 1
                            else:
                                item.set_shortage_status(False)
                        else:
                            # 부족 목록에 없는 경우 부족 상태 해제
                            item.set_shortage_status(False)
        
        print(f"자재 부족 상태 적용 완료: {status_applied_count}개 아이템에 적용됨")

    """
    모든 상태 정보를 현재 아이템들에 적용
    """
    def apply_all_states(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
        
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if hasattr(item, 'item_data') and item.item_data and 'Item' in item.item_data:
                        item_code = item.item_data['Item']
                        item_time = item.item_data.get('Time')

                        # 사전할당 상태
                        if item_code in self.pre_assigned_items:
                            item.set_pre_assigned_status(True)

                        # 출하 실패 상태
                        if item_code in self.shipment_failure_items:
                            failure_info = self.shipment_failure_items[item_code]
                            item.set_shipment_failure(True, failure_info.get('reason', 'Unknown'))

                        # 자재 부족 상태 - 시프트별 체크 적용
                        if hasattr(self, 'current_shortage_items') and item_code in self.current_shortage_items:
                            shortages = self.current_shortage_items[item_code]
                            matching_shortages = []
                            
                            # 시프트별 부족 정보 검사
                            for shortage in shortages:
                                shortage_shift = shortage.get('shift')
                                
                                # 시프트가 일치하는 경우만 처리
                                if shortage_shift and item_time and int(shortage_shift) == int(item_time):
                                    matching_shortages.append(shortage)
                            
                            # 일치하는 시프트의 부족 정보가 있으면 부족 상태로 설정
                            if matching_shortages:
                                item.set_shortage_status(True, matching_shortages)
                            else:
                                item.set_shortage_status(False)

    """범례 위젯에서 필터가 변경될 때 호출"""
    def on_filter_changed(self, filter_states):
        self.current_filter_states = filter_states
        
        # 필터 적용 전 기본 상태 확인
        if filter_states.get('shipment', False):
            # 출하 필터가 켜져 있고, 아직 출하 상태가 설정되지 않았으면
            # 결과 페이지 참조 찾기
            result_page = self.parent_page
            if result_page and hasattr(result_page, 'shipment_widget') and result_page.shipment_widget:
                # 출하 분석 상태 확인
                if not hasattr(result_page.shipment_widget, 'failure_items') or not result_page.shipment_widget.failure_items:
                    # 출하 분석 데이터가 없으면 분석 요청
                    if hasattr(result_page, 'analyze_shipment_with_current_data') and self.data is not None:
                        result_page.analyze_shipment_with_current_data(self.data)
        
        # 상태선 표시만 업데이트
        self.apply_visibility_filter()
        
    """
    현재 필터 상태에 따라 아이템 가시성 조정
    """
    def apply_visibility_filter(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
        
        self.apply_all_filters()
        
    
    """
    아이템이 표시
    - shortage만 체크: 자재부족 아이템만 표시
    - shipment만 체크: 출하실패 아이템만 표시
    - pre_assigned만 체크: 사전할당 아이템만 표시
    - shortage + shipment 체크: 자재부족 AND 출하실패인 아이템만 표시
    - 모든 체크박스 체크: 자재부족 AND 출하실패 AND 사전할당인 아이템만 표시
    - 모든 체크박스 해제: 모든 아이템 표시
    """
    def should_show_item(self, item):
        # 항상 모든 아이템을 표시하도록 변경
        return True
    
    """
    아이템의 상태선 업데이트
    """
    def update_item_status_line_visibility(self, item):
        if not hasattr(self, 'current_filter_states'):
            # 필터 상태가 없으면 아무것도 표시 안함.
            if hasattr(item, 'show_shortage_line'):
                item.show_shortage_line = False
            if hasattr(item, 'show_shipment_line'):
                item.show_shipment_line = False
            if hasattr(item, 'show_pre_assigned_line'):
                item.show_pre_assigned_line = False
            return
        
        # 각 상태별 필터 확인
        shortage_filter = self.current_filter_states.get('shortage', False)
        shipment_filter = self.current_filter_states.get('shipment', False)
        pre_assigned_filter = self.current_filter_states.get('pre_assigned', False)

        # 각 상태선의 가시성 설정
        if hasattr(item, 'is_shortage') and hasattr(item, 'show_shortage_line'):
            item.show_shortage_line = shortage_filter and item.is_shortage
        
        if hasattr(item, 'is_shipment_failure') and hasattr(item, 'show_shipment_line'):
            item.show_shipment_line = shipment_filter and item.is_shipment_failure
        
        if hasattr(item, 'is_pre_assigned') and hasattr(item, 'show_pre_assigned_line'):
            item.show_pre_assigned_line = pre_assigned_filter and item.is_pre_assigned
        
        # 아이템에 repaint 요청하여 선을 다시 그리도록 함
        if hasattr(item, 'update'):
            item.update()

    """
    아이템 삭제 처리 메서드 (ItemContainer에서 발생한 삭제를 처리)
    """
    def on_item_removed(self, item_or_id):
        # print("DEBUG: ModifiedLeftSection.on_item_removed 호출됨")

        # MVC 컨트롤러 확인
        has_controller = hasattr(self, 'controller') and self.controller is not None
        # print(f"DEBUG: MVC 컨트롤러 존재 여부: {has_controller}")
        
        # MVC 컨트롤러가 있으면 컨트롤러에서 처리
        if has_controller:
            print("DEBUG: 컨트롤러를 통해 삭제 처리 시도")
            # 컨트롤러에 연결이 제대로 되어 있는지 확인
            if hasattr(self.controller, 'on_item_deleted'):
                # print("DEBUG: 컨트롤러의 on_item_deleted 메서드 호출")
                self.controller.on_item_deleted(item_or_id)
                return
            else:
                print("DEBUG: 컨트롤러에 on_item_deleted 메서드가 없음")
        
        # 컨트롤러가 없거나 처리하지 않은 경우 기존 로직 사용
        print("DEBUG: 기존 로직으로 삭제 처리")
        if self.data is None:
            print("DEBUG: 데이터가 없음")
            return
        
        # item_or_id가 문자열(ID)인 경우
        if isinstance(item_or_id, str):
            item_id = item_or_id
            print(f"DEBUG: ID로 삭제: {item_id}")
            mask = ItemKeyManager.create_mask_by_id(self.data, item_id)
            if mask.any():
                self.data = self.data[~mask].reset_index(drop=True)
                df = self.extract_dataframe()
                self.viewDataChanged.emit(df)
                self.mark_as_modified()
                # print("DEBUG: ID 기반 삭제 완료")
            else:
                print(f"DEBUG: ID {item_id}로 아이템을 찾을 수 없음")
            return
        
        # item_or_id가 아이템 객체인 경우
        if hasattr(item_or_id, 'item_data') and item_or_id.item_data:
            # ID가 있으면 ID로 찾기
            item_id = ItemKeyManager.extract_item_id(item_or_id)
            if item_id:
                print(f"DEBUG: 아이템 객체의 ID로 삭제: {item_id}")
                mask = ItemKeyManager.create_mask_by_id(self.data, item_id)
                if mask.any():
                    self.data = self.data[~mask].reset_index(drop=True)
                    df = self.extract_dataframe()
                    self.viewDataChanged.emit(df)
                    self.mark_as_modified()
                    # print("DEBUG: ID 기반 삭제 완료")
                    return
            
            # ID가 없으면 Line/Time/Item으로 찾기
            line, time, item_code = ItemKeyManager.get_item_from_data(item_or_id.item_data)
            if line is not None and time is not None and item_code is not None:
                print(f"DEBUG: Line/Time/Item으로 삭제: {item_code} @ {line}-{time}")
                mask = ItemKeyManager.create_mask_for_item(self.data, line, time, item_code)
                if mask.any():
                    self.data = self.data[~mask].reset_index(drop=True)
                    df = self.extract_dataframe()
                    self.viewDataChanged.emit(df)
                    self.mark_as_modified()
                    # print("DEBUG: Line/Time/Item 기반 삭제 완료")
                else:
                    print(f"DEBUG: Line/Time/Item으로 아이템을 찾을 수 없음")
        else:
            print("DEBUG: 유효하지 않은 아이템 객체")


    """
    현재 뷰에 로드된 DataFrame(self.data)의 사본 반환
    viewDataChanged 신호를 뿌릴 때 사용 
    """
    def extract_dataframe(self) -> pd.DataFrame:
        if hasattr(self, 'data') and isinstance(self.data, pd.DataFrame):
            return self._normalize_data_types(self.data.copy())
        else:
            return pd.DataFrame()
        
    """
    모델로부터 UI 업데이트 - 이벤트 발생시키지 않음
    """
    def update_from_model(self, model_df):

        if model_df is None:
            return
            
        # 타입 변환을 한 번에 처리
        self.data = self._normalize_data_types(model_df.copy())
        
        # UI 업데이트 시작
        if self.data is None or 'Line' not in self.data.columns or 'Time' not in self.data.columns:
            print("데이터가 없거나 필수 컬럼이 없음")
            return
            
        try:
            # 기존 아이템 모두 지우기
            self.clear_all_items()
            
            # Line과 Time 값 추출
            lines = sorted(self.data['Line'].unique())
            times = sorted(self.data['Time'].unique())

            # 교대 시간 구분
            shifts = {}
            for time in times:
                if int(time) % 2 == 1:
                    shifts[time] = "Day"
                else:
                    shifts[time] = "Night"

            # 라인별 교대 정보
            line_shifts = {}
            for line in lines:
                line_shifts[line] = ["Day", "Night"]

            # 행 헤더
            self.row_headers = []
            for line in lines:
                for shift in ["Day", "Night"]:
                    self.row_headers.append(f"{line}_({shift})")

            # 그리드 설정
            self.grid_widget.setupGrid(
                rows=len(self.row_headers),
                columns=len(self.days),
                row_headers=self.row_headers,
                column_headers=self.days,
                line_shifts=line_shifts
            )

            # 데이터에서 아이템 생성하여 그리드에 배치
            for _, row_data in self.data.iterrows():
                if 'Line' not in row_data or 'Time' not in row_data:
                    continue

                line = row_data['Line']
                time = row_data['Time']
                shift = shifts[time]
                day_idx = (int(time) - 1) // 2

                if day_idx >= len(self.days):
                    continue

                day = self.days[day_idx]
                row_key = f"{line}_({shift})"

                # Item 정보가 있으면 추출하여 저장
                if 'Item' in row_data and pd.notna(row_data['Item']):
                    item_info = str(row_data['Item'])

                    # MFG 정보가 있으면 수량 정보로 추가
                    if 'Qty' in row_data and pd.notna(row_data['Qty']):
                        item_info += f"    {row_data['Qty']}"

                    try:
                        # 그리드에 아이템 추가
                        row_idx = self.row_headers.index(row_key)
                        col_idx = self.days.index(day)

                        # 전체 행 데이터를 아이템 데이터(dict 형태)로 전달
                        item_full_data = row_data.to_dict()
                        new_item = self.grid_widget.addItemAt(row_idx, col_idx, item_info, item_full_data)

                        if new_item:
                            item_code = item_full_data.get('Item', '')

                            # 사전할당 아이템인 경우
                            if item_code in self.pre_assigned_items:
                                new_item.set_pre_assigned_status(True)
                                
                            # 출하 실패 아이템인 경우
                            if item_code in self.shipment_failure_items:
                                failure_info = self.shipment_failure_items[item_code]
                                new_item.set_shipment_failure(True, failure_info.get('reason', 'Unknown reason'))

                            # 자재부족 아이템인 경우
                            if hasattr(self, 'current_shortage_items') and item_code in self.current_shortage_items:
                                shortage_info = self.current_shortage_items[item_code]
                                new_item.set_shortage_status(True, shortage_info)

                    except ValueError as e:
                        print(f"인덱스 찾기 오류: {e}")
            
        except Exception as e:
            print(f"UI 업데이트 오류: {e}")


    """
    복사된 아이템 처리
    """
    def on_item_copied(self, item, data):
        # 아이템 등록
        self.register_item(item)

        # 데이터 처리는 제거 - 이미 컨트롤러에서 처리함
        # MVC 패턴에서는 뷰는 UI 렌더링만 담당, 데이터 처리는 컨트롤러에서
        
        # 컨트롤러가 없는 경우에만 직접 처리
        if not hasattr(self, 'controller') or not self.controller:
            # 컨트롤러가 없는 경우 기본 처리 - 레거시 지원
            print("컨트롤러 없음: 레거시 처리 방식으로 복사 처리")
            df = self.extract_dataframe()
            self.viewDataChanged.emit(df)

    """
    출하 실패 아이템 정보 설정
    """
    def set_shipment_failure_items(self, failure_items):
                
        # 이전 출하 실패 정보 초기화
        old_failure_items = getattr(self, 'shipment_failure_items', {})
        
        # 새 출하 실패 정보 저장
        self.shipment_failure_items = failure_items
        
        # 상태 변화가 있을 때만 UI 업데이트
        if old_failure_items != failure_items:
            self.apply_shipment_failure_status()

    """출하 실패 상태를 모든 아이템에 적용"""
    def apply_shipment_failure_status(self):
        if not hasattr(self, 'grid_widget') or not hasattr(self.grid_widget, 'containers'):
            return
        
        # 출하 실패 아이템 목록이 없는 경우 초기화
        if not hasattr(self, 'shipment_failure_items'):
            self.shipment_failure_items = {}
        
        status_applied_count = 0
        
        # 모든 컨테이너와 아이템 순회
        for row_containers in self.grid_widget.containers:
            for container in row_containers:
                for item in container.items:
                    if not hasattr(item, 'item_data') or not item.item_data:
                        continue
                        
                    item_data = item.item_data
                    
                    # 필수 필드 확인
                    if 'Item' not in item_data:
                        continue
                        
                    item_code = item_data['Item']
                    
                    # 간단하게 아이템 코드로만 검색 (복합 키는 제외)
                    if item_code in self.shipment_failure_items:
                        # 출하 실패 정보 가져오기
                        failure_info = self.shipment_failure_items[item_code]
                        reason = failure_info.get('reason', '출하 실패')
                        
                        # 출하 실패 상태로 설정
                        item.set_shipment_failure(True, reason)
                        status_applied_count += 1
                    else:
                        # 출하 성공 상태로 설정 (기존 실패였던 경우)
                        if hasattr(item, 'is_shipment_failure') and item.is_shipment_failure:
                            item.set_shipment_failure(False, None)