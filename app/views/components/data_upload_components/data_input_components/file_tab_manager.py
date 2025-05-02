from PyQt5.QtWidgets import QTabBar, QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QFont
import os

from app.views.components.data_upload_components.data_table_component import DataTableComponent
from app.views.components.data_upload_components.enhanced_table_filter_component import EnhancedTableFilterComponent


class FileTabManager:
    """파일 탭 관리를 위한 클래스"""

    def __init__(self, parent):
        self.parent = parent
        self.tab_bar = parent.tab_bar
        self.stacked_widget = parent.stacked_widget
        self.open_tabs = {}  # {(file_path, sheet_name): tab_index}
        self.updating_from_tab = False

    def create_new_tab(self, file_path, sheet_name):
        """새 탭 생성 - 수정된 데이터 사용"""
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

            # 탭 제목 설정
            if sheet_name:
                tab_title = f"{os.path.basename(file_path)} - {sheet_name}"
            else:
                tab_title = os.path.basename(file_path)

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
            self.tab_bar.setCurrentIndex(tab_index)

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

        return True

    def on_tab_changed(self, index):
        """탭이 변경되면 스택 위젯 및 관련 정보 업데이트하고 수정 내용 저장"""
        # 이전 탭의 데이터 저장 (현재 선택된 탭이 변경되기 전)
        current_tab_index = self.tab_bar.currentIndex()
        if current_tab_index >= 0 and current_tab_index < self.stacked_widget.count():
            old_tab_widget = self.stacked_widget.widget(current_tab_index)
            if old_tab_widget:
                # 현재 탭에 해당하는 파일과 시트 찾기
                old_file_path = None
                old_sheet_name = None
                for (file_path, sheet_name), idx in self.open_tabs.items():
                    if idx == current_tab_index:
                        old_file_path = file_path
                        old_sheet_name = sheet_name
                        break

                if old_file_path:
                    self.parent.data_modifier.save_tab_data(old_tab_widget, old_file_path, old_sheet_name)

        # 기존 로직 유지
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
        """탭 닫기 요청 처리 - 수정 내용 정확하게 확인 후 저장"""
        print(f"[DEBUG] 탭 닫기 요청됨: 인덱스 {index}")
        print(f"[DEBUG] 현재 선택된 탭: {self.tab_bar.currentIndex()}")

        # 시작 페이지는 닫을 수 없음
        if index == 0 and self.tab_bar.tabText(0) == "Start Page":
            print("[DEBUG] 시작 페이지는 닫을 수 없음")
            return

        # 닫을 탭의 위젯에서 데이터 가져오기
        if 0 <= index < self.stacked_widget.count():
            tab_widget = self.stacked_widget.widget(index)
            print(f"[DEBUG] 닫을 탭 위젯: {tab_widget}")
        else:
            print(f"[DEBUG] 닫을 탭 위젯 인덱스가 범위를 벗어남: {index}")
            tab_widget = None

        # 닫을 탭에 해당하는 키 찾기
        tab_key_to_close = None
        for tab_key, idx in self.open_tabs.items():
            if idx == index:
                tab_key_to_close = tab_key
                break

        print(f"[DEBUG] 닫을 탭 키: {tab_key_to_close}")

        if tab_key_to_close:
            # 수정된 데이터 확인 및 저장
            file_path, sheet_name = tab_key_to_close
            print(f"[DEBUG] 닫기 전 데이터 저장: {file_path}, {sheet_name}")

            if tab_widget:
                try:
                    # 데이터 저장
                    self.parent.data_modifier.save_tab_data(tab_widget, file_path, sheet_name)
                    print(f"[DEBUG] 데이터 저장 완료")

                    # DataStore에도 현재 데이터 업데이트
                    from app.models.common.fileStore import DataStore
                    final_data = self.parent.data_modifier.get_modified_data_from_tab(tab_widget)

                    # 데이터프레임 딕셔너리에 저장 또는 업데이트
                    df_dict = DataStore.get("dataframes", {})
                    key = f"{file_path}:{sheet_name}" if sheet_name else file_path
                    df_dict[key] = final_data
                    DataStore.set("dataframes", df_dict)
                    print(f"[DEBUG] DataStore에 데이터프레임 저장 완료: {key}")

                except Exception as e:
                    print(f"[DEBUG] 데이터 저장 오류: {str(e)}")

            # 모든 위젯 참조 백업 (실제 위젯 참조를 저장)
            widgets_backup = {}
            for i in range(self.stacked_widget.count()):
                if i != index:  # 닫을 탭 제외
                    widgets_backup[i] = self.stacked_widget.widget(i)

            print(f"[DEBUG] 위젯 백업 완료: {len(widgets_backup)}개")

            # 기존 탭 닫기 로직 실행
            try:
                result = self.close_tab(tab_key_to_close[0], tab_key_to_close[1])
                print(f"[DEBUG] 탭 닫기 결과: {result}")
            except Exception as e:
                print(f"[DEBUG] 탭 닫기 오류: {str(e)}")
                import traceback
                traceback.print_exc()

            # 확인: 탭 닫은 후 위젯과 인덱스 일치 여부
            print(f"[DEBUG] 탭 닫은 후 점검:")
            for key, idx in self.open_tabs.items():
                widget = self.stacked_widget.widget(idx) if 0 <= idx < self.stacked_widget.count() else None
                backup_widget = widgets_backup.get(self.open_tabs.get(key, -1))
                is_same = (widget == backup_widget) if widget and backup_widget else False
                print(f"[DEBUG]   키: {key}, 인덱스: {idx}, 위젯 일치 여부: {is_same}")

            # 탭 닫은 후 인덱스 일관성 확인
            current_idx = self.tab_bar.currentIndex()
            if 0 <= current_idx < self.stacked_widget.count():
                self.stacked_widget.setCurrentIndex(current_idx)
                print(f"[DEBUG] 현재 탭 인덱스로 스택 위젯 설정: {current_idx}")
            else:
                print(f"[DEBUG] 현재 탭 인덱스가 범위를 벗어남: {current_idx}")

            # 모든 탭이 닫혔는지 확인
            if self.tab_bar.count() == 0:
                print(f"[DEBUG] 모든 탭이 닫혔음, 시작 페이지 추가")
                # Start Page 다시 추가
                self.create_start_page()

    def on_tab_moved(self, from_index, to_index):
        """탭이 이동되면 open_tabs 딕셔너리와 스택 위젯 업데이트"""
        print(f"탭 이동: {from_index} -> {to_index}")

        try:
            # 1. 이동할 탭의 키(file_path, sheet_name) 찾기
            moved_tab_key = None
            for key, idx in self.open_tabs.items():
                if idx == from_index:
                    moved_tab_key = key
                    break

            if not moved_tab_key:
                print("이동할 탭을 찾을 수 없습니다.")
                return

            # 2. 이동할 탭의 위젯 가져오기
            moved_widget = self.stacked_widget.widget(from_index)

            # 3. 중요: QTabBar의 이동을 먼저 처리 후 스택 위젯 조정하지 않기
            # QTabBar는 이미 이동 완료된 상태

            # 4. 모든 위젯과 키 백업 (인덱스 순서대로)
            widgets_by_index = {}
            keys_by_index = {}

            for key, idx in self.open_tabs.items():
                if 0 <= idx < self.stacked_widget.count():
                    widgets_by_index[idx] = self.stacked_widget.widget(idx)
                    keys_by_index[idx] = key

            # 5. 인덱스 업데이트 로직을 간소화
            new_open_tabs = {}

            # 모든 키에 대해 새 인덱스 계산
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

            # 6. 스택 위젯 완전히 재구성
            # 먼저 모든 위젯을 제거 (위젯 자체는 삭제하지 않음)
            for i in range(self.stacked_widget.count()):
                self.stacked_widget.removeWidget(self.stacked_widget.widget(0))

            # 7. 새 인덱스 순서대로 위젯 다시 배치
            # 인덱스 순으로 정렬하여 추가
            sorted_items = sorted(new_open_tabs.items(), key=lambda x: x[1])

            for key, new_idx in sorted_items:
                old_idx = self.open_tabs[key]
                if old_idx in widgets_by_index:
                    widget = widgets_by_index[old_idx]
                    self.stacked_widget.insertWidget(new_idx, widget)

            # 8. 새 매핑 적용
            self.open_tabs = new_open_tabs

            # 9. 현재 선택된 탭에 맞게 스택 위젯 설정
            current_idx = self.tab_bar.currentIndex()
            if 0 <= current_idx < self.stacked_widget.count():
                self.stacked_widget.setCurrentIndex(current_idx)

            print(f"탭 이동 완료: 현재 탭 인덱스 {self.tab_bar.currentIndex()}, 스택 위젯 인덱스 {self.stacked_widget.currentIndex()}")
            print(f"업데이트된 탭 정보: {self.open_tabs}")

        except Exception as e:
            # 오류 발생 시 로그 기록
            print(f"탭 이동 중 오류 발생: {str(e)}")

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

        # 탭 삭제 (인덱스는 닫을 때마다 변하므로 역순으로)
        for key in tabs_to_remove:
            self.close_tab(key[0], key[1])

        # 모든 탭이 닫혔는지 확인하고 Start Page 추가
        if self.tab_bar.count() == 0:
            self.create_start_page()

    def update_tab_title(self, file_path, sheet_name, is_modified=False):
        """탭 제목 업데이트 (수정 상태에 따라)"""
        # 해당 탭 찾기
        tab_key = (file_path, sheet_name)
        if tab_key not in self.open_tabs:
            return

        tab_index = self.open_tabs[tab_key]

        # 수정 여부에 따라 탭 제목 설정
        if sheet_name:
            base_title = f"{os.path.basename(file_path)} - {sheet_name}"
        else:
            base_title = os.path.basename(file_path)

        # 수정된 파일인지 확인
        is_modified = is_modified or (
                file_path in self.parent.data_modifier.modified_data_dict and
                (sheet_name or 'data') in self.parent.data_modifier.modified_data_dict[file_path]
        )

        # 탭 제목 설정
        tab_title = base_title + " *" if is_modified else base_title

        # 탭 제목 업데이트
        current_title = self.tab_bar.tabText(tab_index)
        if current_title != tab_title:
            self.tab_bar.setTabText(tab_index, tab_title)