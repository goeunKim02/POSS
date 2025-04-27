from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
import pandas as pd
import os

from app.views.components.data_upload_components.data_table_component import DataTableComponent


class FileTabComponent(QWidget):
    """
    파일 탭 컴포넌트
    여러 파일을 탭 형태로 관리하고 표시하는 기능 제공
    """
    tab_changed = pyqtSignal(str)  # 탭이 변경되었을 때 발생하는 시그널 (선택된 파일 경로 전달)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_tabs = {}  # 파일 경로를 키로, 해당 탭 인덱스를 값으로 저장
        self.excel_sheets = {}  # 파일 경로를 키로, 해당 파일의 모든 시트 이름을 값으로 저장
        self.current_file_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()

        # 탭의 크기를 내용에 맞게 조정
        self.tab_widget.tabBar().setExpanding(False)  # 탭 크기가 내용에 맞게 조정됨
        self.tab_widget.tabBar().setElideMode(Qt.ElideNone)  # 텍스트가 잘리지 않도록 설정
        self.tab_widget.tabBar().setUsesScrollButtons(True)  # 탭이 많아지면 스크롤 버튼 표시

        # 탭 간격 조정 (탭 사이의 간격을 줄임)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #cccccc; 
                background: white; 
                border-radius: 20px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-radius: 10px;
                padding: 5px 12px;
                margin-right: 2px;  /* 탭 간 간격 줄임 */
                min-width:300px;    /* 최소 너비 증가 */

            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #1428A0;
                color: white;
            }
            QTabBar::tab:selected {
                border-bottom-color: white;
            }
        """)

        # 탭 변경 이벤트 연결
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # 레이아웃에 위젯 추가
        layout.addWidget(self.tab_widget)

    def add_file_tab(self, file_path):
        """새 파일 탭 추가"""
        try:
            if not file_path or not os.path.exists(file_path):
                return False, "파일을 찾을 수 없습니다"

            # 이미 탭이 있는지 확인
            if file_path in self.file_tabs:
                # 이미 있는 탭으로 이동
                self.tab_widget.setCurrentIndex(self.file_tabs[file_path])
                return False, "이미 로드된 파일입니다"

            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)

            # 새 탭 생성
            new_tab = QWidget()
            new_tab_layout = QVBoxLayout(new_tab)
            new_tab_layout.setContentsMargins(0, 0, 0, 0)

            # 파일 확장자에 따라 다른 방식으로 데이터 로드
            if file_ext == '.csv':
                # CSV 파일 로드
                try:
                    df = DataTableComponent.load_data_from_file(file_path)
                    # 데이터 테이블 생성 및 추가
                    data_table = DataTableComponent.create_table_from_dataframe(df)
                    new_tab_layout.addWidget(data_table)
                except Exception as e:
                    return False, f"CSV 파일 로딩 오류: {str(e)}"

            elif file_ext in ['.xls', '.xlsx']:
                # 엑셀 파일의 모든 시트 이름 가져오기
                try:
                    excel = pd.ExcelFile(file_path)
                    sheet_names = excel.sheet_names

                    # 시트 정보 저장
                    self.excel_sheets[file_path] = sheet_names

                    # 첫 번째 시트 데이터 로드
                    if sheet_names:
                        df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_names[0])
                        # 데이터 테이블 생성 및 추가
                        data_table = DataTableComponent.create_table_from_dataframe(df)
                        new_tab_layout.addWidget(data_table)
                    else:
                        # 시트가 없는 경우
                        error_label = QLabel("엑셀 파일에 시트가 없습니다")
                        error_label.setAlignment(Qt.AlignCenter)
                        new_tab_layout.addWidget(error_label)
                except Exception as e:
                    return False, f"엑셀 파일 로딩 오류: {str(e)}"
            else:
                return False, "지원하지 않는 파일 형식입니다"

            # 탭 추가
            tab_index = self.tab_widget.addTab(new_tab, file_name)
            self.tab_widget.setCurrentIndex(tab_index)  # 새 탭으로 전환

            # 탭 정보 저장
            self.file_tabs[file_path] = tab_index
            self.current_file_path = file_path

            return True, f"'{file_name}' 파일이 성공적으로 로드되었습니다"

        except Exception as e:
            # 오류 발생 시
            return False, f"데이터 로딩 오류: {str(e)}"

    def remove_file_tab(self, file_path):
        """파일 탭 제거"""
        if file_path not in self.file_tabs:
            return False, "해당 파일 탭이 존재하지 않습니다"

        tab_index = self.file_tabs[file_path]

        # 탭 제거 전에 현재 선택된 탭인지 확인
        is_current = self.tab_widget.currentIndex() == tab_index

        # 탭 제거
        self.tab_widget.removeTab(tab_index)

        # 탭 정보에서 제거
        del self.file_tabs[file_path]

        # 엑셀 시트 정보에서 제거
        if file_path in self.excel_sheets:
            del self.excel_sheets[file_path]

        # 현재 파일 경로 업데이트
        if is_current or file_path == self.current_file_path:
            self.current_file_path = None

            # 새로운 현재 탭 인덱스 가져오기
            new_current_index = self.tab_widget.currentIndex()

            # 현재 선택된 탭이 있고 유효하면 해당 파일 업데이트
            if new_current_index >= 0:
                # 현재 탭에 해당하는 파일 경로 찾기
                for path, idx in self.file_tabs.items():
                    if idx == new_current_index:
                        self.current_file_path = path
                        break

        # 탭 인덱스 재조정 (삭제한 탭 이후의 모든 탭 인덱스 갱신)
        for path, idx in list(self.file_tabs.items()):
            if idx > tab_index:
                self.file_tabs[path] = idx - 1

        # 메시지 반환
        file_name = os.path.basename(file_path)
        return True, f"'{file_name}' 파일이 제거되었습니다"

    def on_tab_changed(self, index):
        """탭이 변경되면 호출되는 함수"""
        # 현재 탭에 해당하는 파일 경로 찾기
        file_path = None
        for path, tab_idx in self.file_tabs.items():
            if tab_idx == index:
                file_path = path
                break

        self.current_file_path = file_path

        # 시그널 발생 (파일 경로 전달)
        if file_path:
            self.tab_changed.emit(file_path)

    def load_sheet(self, file_path, sheet_name):
        """특정 파일의 특정 시트 로드"""
        if file_path not in self.file_tabs:
            return False, "해당 파일 탭이 존재하지 않습니다"

        try:
            # 엑셀 파일에서 특정 시트 로드
            df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_name)

            # 현재 탭의 위젯 가져오기
            tab_index = self.file_tabs[file_path]
            current_tab = self.tab_widget.widget(tab_index)

            # 기존 위젯 제거
            for i in reversed(range(current_tab.layout().count())):
                current_tab.layout().itemAt(i).widget().setParent(None)

            # 데이터 테이블 생성 및 추가
            data_table = DataTableComponent.create_table_from_dataframe(df)
            current_tab.layout().addWidget(data_table)

            return True, f"시트 '{sheet_name}'이(가) 로드되었습니다"

        except Exception as e:
            return False, f"시트 로딩 오류: {str(e)}"

    def get_current_file_path(self):
        """현재 선택된 파일 경로 반환"""
        return self.current_file_path

    def get_excel_sheets(self, file_path):
        """특정 파일의 엑셀 시트 목록 반환"""
        if file_path in self.excel_sheets:
            return self.excel_sheets[file_path]
        return []

    def is_excel_file(self, file_path):
        """해당 파일이 엑셀 파일인지 확인"""
        return file_path in self.excel_sheets

    def has_tabs(self):
        """탭이 있는지 확인"""
        return self.tab_widget.count() > 0