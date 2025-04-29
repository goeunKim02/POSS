from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QVBoxLayout, QTableView
from PyQt5.QtCore import Qt
import pandas as pd


class DataTableComponent:
    @staticmethod
    def create_table_from_dataframe(df, filter_component=None):
        # 데이터프레임으로 테이블 위젯 생성
        # 컨테이너 위젯 생성
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 필터 컴포넌트가 제공된 경우, 데이터 설정
        if filter_component:
            filter_component.set_data(df)
            # 필터 위젯 추가
            layout.addWidget(filter_component)
            # 테이블 뷰는 이미 필터 컴포넌트 내부에 있으므로 별도로 추가할 필요가 없음
            # 컨테이너에 필터 컴포넌트 참조 저장
            container._filter_component = filter_component
            # 필터링된 데이터에 접근하기 위한 메서드
            container.get_filtered_data = lambda: filter_component.get_filtered_data()
            return container

        # 필터 컴포넌트가 없는 경우 기존 방식으로 테이블 위젯 생성 (이전 코드와 호환성 유지)
        data_table = QTableWidget()
        data_table.setStyleSheet("QTableWidget { border: none; }")
        data_table.setAlternatingRowColors(True)

        # 모든 열이 동일한 너비를 가지도록 Stretch 모드 설정
        data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 마지막 열을 늘리는 설정 비활성화
        data_table.horizontalHeader().setStretchLastSection(False)

        # 테이블 설정
        data_table.setRowCount(len(df))
        data_table.setColumnCount(len(df.columns))

        # 모든 컬럼명을 문자열로 변환 (datetime 객체 처리)
        column_labels = [str(col) for col in df.columns]
        data_table.setHorizontalHeaderLabels(column_labels)

        # 데이터 채우기 - NaN, None, datetime 등의 데이터 타입 안전하게 처리
        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = df.iloc[row, col]
                # None, NaN 등의 값 처리
                if pd.isna(value):
                    display_value = ""
                else:
                    display_value = str(value)
                item = QTableWidgetItem(display_value)
                data_table.setItem(row, col, item)

        # 레이아웃에 테이블 추가
        layout.addWidget(data_table)

        # 컨테이너에 테이블 참조 저장
        container._data_table = data_table

        # 필터링된 데이터에 접근하기 위한 메서드 (필터가 없는 경우 원본 반환)
        container.get_filtered_data = lambda: df.copy()

        return container

    @staticmethod
    def load_data_from_file(file_path, sheet_name=None):
        """파일로부터 데이터 로드"""
        import os

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.csv':
            # CSV 파일 로드
            return pd.read_csv(file_path, encoding='utf-8')
        elif file_ext in ['.xls', '.xlsx']:
            # 엑셀 파일 로드 (시트명 지정 가능)
            return pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다")