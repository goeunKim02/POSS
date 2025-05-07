from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import os

from app.views.components.data_upload_components.data_table_component import DataTableComponent
from app.views.components.data_upload_components.enhanced_table_filter_component import EnhancedTableFilterComponent


class FileTabManager:
    """
    파일 탭 관리를 위한 클래스
    DataInputPage의 탭 관련 로직을 모두 담당
    """

    def __init__(self, parent):
        self.parent = parent
        self.tab_bar = parent.tab_bar
        self.stacked_widget = parent.stacked_widget
        self.open_tabs = {}  # {(file_path, sheet_name): tab_index}
        self.updating_from_tab = False

        # 탭 스타일 설정 - 스타일 관리를 여기에서만 담당
        self.apply_tab_styles()

        # 탭 바 시그널 연결
        self.tab_bar.currentChanged.connect(self.on_tab_changed)
        self.tab_bar.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tab_bar.tabMoved.connect(self.on_tab_moved)
        self.tab_bar.setTabsClosable(True)

        # 시작 페이지 생성
        self.create_start_page()

    def apply_tab_styles(self):
        """모든 탭 관련 스타일을 한 곳에서 적용"""
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setElideMode(Qt.ElideNone)
        self.tab_bar.setStyleSheet("""
            QTabBar {
                background-color: transparent;
                border: none;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 6px 10px;
                margin-right: 2px;
                min-width: 530px;
                max-width: 1700px;
                font-family: Arial, sans-serif;
                font-weight: bold;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #1428A0;
                color: white;
            }
            QTabBar::tab:selected {
                border-bottom-color: white;
            }
        """)

        self.stacked_widget.setStyleSheet("border: 2px solid #cccccc; background-color: white;")

    # 파일 탭 제목 설정 부분을 수정
    # file_tab_manager.py 파일의 create_new_tab 메서드에서 수정할 부분

    def create_new_tab(self, file_path, sheet_name):
        """새 탭 생성"""
        try:
            file_info = self.parent.loaded_files[file_path]

            # 수정된 데이터 우선 확인
            df = None
            if file_path in self.parent.data_modifier.modified_data_dict:
                sheet_key = sheet_name or 'data'
                if sheet_key in self.parent.data_modifier.modified_data_dict[file_path]:
                    df = self.parent.data_modifier.modified_data_dict[file_path][sheet_key]
                    print(f"수정된 데이터 로드됨: {file_path}, 시트: {sheet_name}")

            # 수정된 데이터가 없으면 원본 데이터 로드
            if df is None:
                if sheet_name and file_info['sheets'] and sheet_name in file_info['sheets']:
                    # 시트가 명시적으로 선택된 경우
                    df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_name)
                    file_info['df'] = df  # 현재 로드된 데이터프레임 업데이트
                    file_info['current_sheet'] = sheet_name
                else:
                    # CSV 파일이거나 시트가 없는 경우
                    df = file_info['df']

            # 탭 제목 설정 - 여기서 수정
            file_name = os.path.basename(file_path)
            # 확장자 제거
            file_name_without_ext = os.path.splitext(file_name)[0]

            if sheet_name:
                tab_title = f"{file_name_without_ext}/{sheet_name}"
            else:
                tab_title = file_name_without_ext

            # 수정된 파일인 경우 표시
            if (file_path in self.parent.data_modifier.modified_data_dict and
                    (sheet_name in self.parent.data_modifier.modified_data_dict[file_path] or
                     'data' in self.parent.data_modifier.modified_data_dict[file_path])):
                tab_title += " *"

            # 새 탭용 위젯 생성
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)

            # 필터 컴포넌트 생성
            filter_component = EnhancedTableFilterComponent()

            # 데이터 테이블 생성
            data_container = DataTableComponent.create_table_from_dataframe(df, filter_component)
            tab_layout.addWidget(data_container)

            # 새 탭과 스택 위젯 항목 추가
            tab_index = self.tab_bar.addTab(tab_title)
            self.stacked_widget.addWidget(tab_widget)

            # 탭 상태 저장 및 선택
            self.open_tabs[(file_path, sheet_name)] = tab_index
            self.tab_bar.setCurrentIndex(tab_index)  # 새 탭으로 전환

            # DataStore에 데이터 저장
            from app.models.common.fileStore import DataStore
            df_dict = DataStore.get("dataframes", {})
            key = f"{file_path}:{sheet_name}" if sheet_name else file_path
            df_dict[key] = df
            DataStore.set("dataframes", df_dict)

            return tab_index

        except Exception as e:
            print(f"탭 생성 오류: {str(e)}")
            return -1

    def close_tab(self, file_path, sheet_name):
        """특정 파일과 시트에 해당하는 탭 닫기"""
        tab_key = (file_path, sheet_name)

        if tab_key not in self.open_tabs:
            return False

        tab_index = self.open_tabs[tab_key]

        # 탭을 닫기 전에 데이터 저장
        if 0 <= tab_index < self.stacked_widget.count():
            tab_widget = self.stacked_widget.widget(tab_index)
            self.parent.data_modifier.save_tab_data(tab_widget, file_path, sheet_name)

        # 1. 모든 위젯과 키 정보를 저장 (닫을 탭 제외)
        widgets_to_keep = []
        keys_to_keep = []

        for key, idx in sorted(self.open_tabs.items(), key=lambda x: x[1]):
            if key != tab_key:  # 닫을 탭 제외
                if 0 <= idx < self.stacked_widget.count():
                    widget = self.stacked_widget.widget(idx)
                    widgets_to_keep.append(widget)
                    keys_to_keep.append(key)

        # 2. 탭 제거
        self.tab_bar.removeTab(tab_index)

        # 3. 모든 위젯 제거 (삭제하지 않고 제거만 함)
        while self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.widget(0))

        # 4. open_tabs 초기화
        self.open_tabs = {}

        # 5. 위젯 재추가 및 딕셔너리 업데이트
        for i, (widget, key) in enumerate(zip(widgets_to_keep, keys_to_keep)):
            self.stacked_widget.addWidget(widget)
            self.open_tabs[key] = i

        # 6. 현재 선택된 탭에 맞게 스택 위젯 설정
        current_idx = self.tab_bar.currentIndex()
        if 0 <= current_idx < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(current_idx)

        # 7. 모든 탭이 닫혔는지 확인
        if self.tab_bar.count() == 0:
            self.create_start_page()

        return True

    def on_tab_changed(self, index):
        """탭이 변경되면 호출되는 함수"""
        # 이전 탭의 데이터 저장
        prev_idx = self.stacked_widget.currentIndex()
        if prev_idx >= 0 and prev_idx < self.stacked_widget.count():
            old_tab_widget = self.stacked_widget.widget(prev_idx)
            if old_tab_widget:
                # 현재 탭에 해당하는 파일과 시트 찾기
                old_file_path = None
                old_sheet_name = None
                for (file_path, sheet_name), idx in self.open_tabs.items():
                    if idx == prev_idx:
                        old_file_path = file_path
                        old_sheet_name = sheet_name
                        break

                if old_file_path:
                    self.parent.data_modifier.save_tab_data(old_tab_widget, old_file_path, old_sheet_name)

        # 스택 위젯 업데이트
        self.stacked_widget.setCurrentIndex(index)

        # 사이드바에서 업데이트 중이면 무시 (무한 루프 방지)
        if self.parent.sidebar_manager.updating_from_sidebar:
            return

        if index < 0 or index >= self.tab_bar.count():
            return

        # 시작 페이지인 경우 (인덱스 0)
        if index == 0 and self.tab_bar.tabText(0) == "Start Page":
            self.parent.current_file = None
            self.parent.current_sheet = None
            return

        # 현재 선택된 탭에 해당하는 파일과 시트 찾기
        found = False
        for (file_path, sheet_name), idx in self.open_tabs.items():
            if idx == index:
                found = True
                self.parent.current_file = file_path
                self.parent.current_sheet = sheet_name

                # 파일 정보 업데이트
                if file_path in self.parent.loaded_files:
                    file_info = self.parent.loaded_files[file_path]
                    if sheet_name:
                        file_info['current_sheet'] = sheet_name

                # 사이드바에서도 동일 항목 선택 처리
                self.updating_from_tab = True
                self.parent.file_explorer.select_file_or_sheet(file_path, sheet_name)
                self.updating_from_tab = False

                break

        if not found:
            self.parent.current_file = None
            self.parent.current_sheet = None

    def on_tab_close_requested(self, index):
        """탭 닫기 요청 처리"""
        # 시작 페이지는 닫을 수 없음
        if index == 0 and self.tab_bar.tabText(0) == "Start Page":
            return

        # 닫을 탭의 키 찾기
        tab_key_to_close = None
        for tab_key, idx in self.open_tabs.items():
            if idx == index:
                tab_key_to_close = tab_key
                break

        if tab_key_to_close:
            # 탭 닫기 실행
            self.close_tab(tab_key_to_close[0], tab_key_to_close[1])

            # 현재 선택된 탭에 맞게 스택 위젯 설정
            current_idx = self.tab_bar.currentIndex()
            if 0 <= current_idx < self.stacked_widget.count():
                self.stacked_widget.setCurrentIndex(current_idx)

    def on_tab_moved(self, from_index, to_index):
        """탭이 이동되면 실행되는 함수"""
        # 1. 이동할 탭의 키 찾기
        moved_tab_key = None
        for key, idx in self.open_tabs.items():
            if idx == from_index:
                moved_tab_key = key
                break

        if not moved_tab_key:
            return

        # 2. 모든 위젯과 키 백업
        widgets_by_index = {}
        for idx in range(self.stacked_widget.count()):
            widgets_by_index[idx] = self.stacked_widget.widget(idx)

        # 3. 인덱스 업데이트
        new_open_tabs = {}
        for key, old_idx in self.open_tabs.items():
            # 이동한 탭
            if key == moved_tab_key:
                new_idx = to_index
            # 범위 내의 다른 탭
            elif from_index < to_index and old_idx > from_index and old_idx <= to_index:
                new_idx = old_idx - 1  # 한 칸 앞으로
            elif from_index > to_index and old_idx < from_index and old_idx >= to_index:
                new_idx = old_idx + 1  # 한 칸 뒤로
            # 영향 받지 않는 탭
            else:
                new_idx = old_idx

            new_open_tabs[key] = new_idx

        # 4. 스택 위젯 재구성
        for i in range(self.stacked_widget.count()):
            self.stacked_widget.removeWidget(self.stacked_widget.widget(0))

        # 5. 새 인덱스 순서대로 위젯 다시 배치
        for key, new_idx in sorted(new_open_tabs.items(), key=lambda x: x[1]):
            old_idx = self.open_tabs[key]
            if old_idx in widgets_by_index:
                widget = widgets_by_index[old_idx]
                self.stacked_widget.insertWidget(new_idx, widget)

        # 6. 새 매핑 적용
        self.open_tabs = new_open_tabs

        # 7. 현재 선택된 탭에 맞게 스택 위젯 설정
        current_idx = self.tab_bar.currentIndex()
        if 0 <= current_idx < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(current_idx)

    def remove_start_page(self):
        """Start Page 탭 제거"""
        if self.tab_bar.count() > 0 and self.tab_bar.tabText(0) == "Start Page":
            # Start Page 위젯 제거
            start_widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(start_widget)
            start_widget.deleteLater()

            # 탭 제거
            self.tab_bar.removeTab(0)

            # open_tabs의 인덱스 조정 (모든 탭 인덱스를 1씩 감소)
            updated_open_tabs = {}
            for key, idx in self.open_tabs.items():
                updated_open_tabs[key] = idx - 1
            self.open_tabs = updated_open_tabs

    def create_start_page(self):
        """Start Page 생성 및 추가"""
        # Start Page 위젯 생성
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_msg = QLabel("Select a file or sheet from the sidebar to open a new tab")
        empty_msg.setAlignment(Qt.AlignCenter)
        empty_msg.setStyleSheet("color: #888; font-size: 14px; font-family: Arial; font-weight: bold;")
        empty_layout.addWidget(empty_msg)

        # 위젯 추가
        self.stacked_widget.insertWidget(0, empty_widget)
        self.tab_bar.insertTab(0, "Start Page")
        self.tab_bar.setCurrentIndex(0)

    def close_file_tabs(self, file_path):
        """파일 관련 모든 탭 닫기"""
        # 해당 파일과 관련된 모든 탭 찾아서 닫기
        tabs_to_remove = []
        for (path, sheet), idx in self.open_tabs.items():
            if path == file_path:
                tabs_to_remove.append((path, sheet))

        # 탭 삭제 (역순으로)
        for key in tabs_to_remove:
            self.close_tab(key[0], key[1])

    def update_tab_title(self, file_path, sheet_name, is_modified=False):
        """탭 제목 업데이트 (수정 상태에 따라)"""
        # 해당 탭 찾기
        tab_key = (file_path, sheet_name)
        if tab_key not in self.open_tabs:
            return

        tab_index = self.open_tabs[tab_key]

        # 탭 제목 설정 - 여기서 수정
        file_name = os.path.basename(file_path)
        # 확장자 제거
        file_name_without_ext = os.path.splitext(file_name)[0]

        if sheet_name:
            base_title = f"{file_name_without_ext}/{sheet_name}"
        else:
            base_title = file_name_without_ext

        # 수정된 파일인지 확인
        is_modified = is_modified or (
                file_path in self.parent.data_modifier.modified_data_dict and
                (sheet_name or 'data') in self.parent.data_modifier.modified_data_dict[file_path]
        )

        # 탭 제목 업데이트
        tab_title = base_title + " *" if is_modified else base_title
        current_title = self.tab_bar.tabText(tab_index)
        if current_title != tab_title:
            self.tab_bar.setTabText(tab_index, tab_title)

    def save_current_tab_data(self):
        """현재 선택된 탭의 데이터 저장"""
        current_tab_index = self.tab_bar.currentIndex()
        if current_tab_index >= 0 and current_tab_index < self.stacked_widget.count():
            current_tab_widget = self.stacked_widget.widget(current_tab_index)
            if current_tab_widget:
                # 현재 탭에 해당하는 파일과 시트 찾기
                for (file_path, sheet_name), idx in self.open_tabs.items():
                    if idx == current_tab_index:
                        self.parent.data_modifier.save_tab_data(current_tab_widget, file_path, sheet_name)
                        return True
        return False