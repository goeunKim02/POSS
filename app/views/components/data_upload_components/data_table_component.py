from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QVBoxLayout
import pandas as pd


class DataTableComponent:
    """
    데이터 테이블 컴포넌트
    데이터프레임을 QTableWidget으로 변환하여 표시하는 기능을 제공합니다.
    """

    @staticmethod
    def create_table_from_dataframe(df):
        """데이터프레임으로 테이블 위젯 생성"""
        # 컨테이너 위젯 생성 (테이블 및 필터를 포함할 수 있음)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 데이터 테이블 생성
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

        # 컨테이너에 테이블 참조 저장 (필터 컴포넌트가 접근할 수 있도록)
        container._data_table = data_table

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