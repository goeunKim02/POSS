import os
import pandas as pd
from PyQt5.QtCore import Qt

from app.views.components.data_upload_components.data_table_component import DataTableComponent


class SidebarManager:
    """사이드바 관리를 위한 클래스"""

    def __init__(self, parent):
        self.parent = parent
        self.file_explorer = parent.file_explorer
        self.updating_from_sidebar = False

    def add_file_to_sidebar(self, file_path):
        """파일을 사이드바에 추가하고 DataStore에 등록"""
        # 파일 확장자 확인
        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            # 엑셀 파일인 경우 시트 목록 가져오기
            sheet_names = None
            if file_ext in ['.xls', '.xlsx']:
                import pandas as pd
                excel = pd.ExcelFile(file_path)
                sheet_names = excel.sheet_names

                # 첫 번째 시트 로드
                if sheet_names:
                    df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet_names[0])
                    self.parent.loaded_files[file_path] = {'df': df, 'sheets': sheet_names,
                                                           'current_sheet': sheet_names[0]}

                    # DataStore에 등록
                    from app.models.common.fileStore import DataStore
                    df_dict = DataStore.get("dataframes", {})
                    df_dict[f"{file_path}:{sheet_names[0]}"] = df

                    # 다른 모든 시트도 로드하여 저장
                    for sheet in sheet_names[1:]:
                        sheet_df = DataTableComponent.load_data_from_file(file_path, sheet_name=sheet)
                        df_dict[f"{file_path}:{sheet}"] = sheet_df

                    DataStore.set("dataframes", df_dict)

            # CSV 파일인 경우
            elif file_ext == '.csv':
                df = DataTableComponent.load_data_from_file(file_path)
                self.parent.loaded_files[file_path] = {'df': df, 'sheets': None, 'current_sheet': None}

                # DataStore에 등록
                from app.models.common.fileStore import DataStore
                df_dict = DataStore.get("dataframes", {})
                df_dict[file_path] = df
                DataStore.set("dataframes", df_dict)

            # 파일 탐색기에 파일 추가
            self.file_explorer.add_file(file_path, sheet_names)

            # 첫 번째 파일인 경우 자동 선택
            if len(self.parent.loaded_files) == 1:
                self.file_explorer.select_first_item()

            return True, f"파일 '{os.path.basename(file_path)}'이(가) 로드되었습니다"

        except Exception as e:
            return False, f"파일 로드 오류: {str(e)}"

    def remove_file_from_sidebar(self, file_path):
        """사이드바에서 파일 제거"""
        # 사이드바에서 파일 제거
        result = self.file_explorer.remove_file(file_path)

        # 로드된 파일 목록에서 제거
        if file_path in self.parent.loaded_files:
            del self.parent.loaded_files[file_path]

        # 수정된 데이터 목록에서도 제거
        if file_path in self.parent.data_modifier.modified_data_dict:
            del self.parent.data_modifier.modified_data_dict[file_path]

        # DataStore에서도 관련 데이터프레임 제거
        from app.models.common.fileStore import DataStore
        df_dict = DataStore.get("dataframes", {})
        keys_to_remove = []
        for key in df_dict.keys():
            if key == file_path or key.startswith(f"{file_path}:"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del df_dict[key]

        DataStore.set("dataframes", df_dict)

        # 현재 표시 중인 파일이 제거된 경우, 화면 초기화
        if self.parent.current_file == file_path:
            self.parent.current_file = None
            self.parent.current_sheet = None

        return result

    def on_file_or_sheet_selected(self, file_path, sheet_name):
        """파일 탐색기에서 파일이나 시트가 선택되면 호출 - 수정된 데이터 로드"""
        print(f"사이드바에서 선택됨: {file_path}, 시트: {sheet_name}")

        # 탭으로부터의 업데이트 중이면 무시 (무한 루프 방지)
        if self.parent.tab_manager.updating_from_tab:
            return

        self.updating_from_sidebar = True

        # 파일이 로드되지 않은 경우
        if file_path not in self.parent.loaded_files:
            print("선택한 파일이 로드되지 않았습니다")
            self.updating_from_sidebar = False
            return

        self.parent.current_file = file_path
        file_info = self.parent.loaded_files[file_path]

        # 시트 이름 결정
        if sheet_name and file_info['sheets'] and sheet_name in file_info['sheets']:
            self.parent.current_sheet = sheet_name
        else:
            # 시트를 명시적으로 선택하지 않은 경우 (파일만 선택)
            if file_info.get('sheets'):
                # 엑셀 파일이고 시트가 있는 경우 기본값 설정
                self.parent.current_sheet = file_info.get('current_sheet') or file_info['sheets'][0]
            else:
                # CSV 파일인 경우
                self.parent.current_sheet = None

        # 해당 탭이 이미 열려 있는지 확인
        tab_key = (file_path, self.parent.current_sheet)
        if tab_key in self.parent.tab_manager.open_tabs:
            # 이미 열려 있는 탭으로 전환
            self.parent.tab_bar.setCurrentIndex(self.parent.tab_manager.open_tabs[tab_key])
        else:
            # Start Page 탭이 있고 이것이 첫 번째 컨텐츠 탭인지 확인
            if self.parent.tab_bar.count() == 1 and self.parent.tab_bar.tabText(0) == "Start Page":
                # Start Page 제거
                self.parent.tab_manager.remove_start_page()

            # 새 탭 생성 - 수정된 데이터 사용
            self.parent.tab_manager.create_new_tab(file_path, self.parent.current_sheet)

        self.updating_from_sidebar = False