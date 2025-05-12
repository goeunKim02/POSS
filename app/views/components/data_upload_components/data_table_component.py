from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QVBoxLayout, QTableView
from PyQt5.QtCore import Qt, QTimer
import pandas as pd


class DataTableComponent:
    @staticmethod
    def create_table_from_dataframe(df, filter_component=None):
        # 데이터프레임으로 테이블 위젯 생성
        # 컨테이너 위젯 생성
        container = QWidget()
        container.setStyleSheet("border-radius: 10px; background-color: white;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 필터 컴포넌트가 제공된 경우, 데이터 설정
        if filter_component:
            filter_component.set_data(df)

            # 테이블 뷰 스타일 설정 (필터 컴포넌트에 있는 테이블 뷰)
            filter_component.table_view.setStyleSheet("""
                QTableView {
                    border: none;
                    background-color: white;
                    border-radius: 10px;
                }
                QScrollBar:vertical {
                    border: none;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #cccccc;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                QScrollBar:horizontal {
                    border: none;
                    height: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background: #cccccc;
                    min-width: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)

            # 열 너비 균일하게 설정 (필터 컴포넌트용)
            header = filter_component.table_view.horizontalHeader()

            # 사용자가 열 너비를 조정할 수 있도록 Interactive 모드 설정
            header.setSectionResizeMode(QHeaderView.Interactive)

            # 마지막 열이 남은 공간을 채우지 않도록 설정
            header.setStretchLastSection(False)

            # 위젯이 화면에 표시된 후에 열 너비 균등하게 조정 (100ms 지연)
            column_count = len(df.columns)
            QTimer.singleShot(100, lambda: DataTableComponent._adjust_column_widths(filter_component.table_view,
                                                                                    column_count))

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
        data_table.setStyleSheet("""
            QTableWidget { 
                border: none; 
                background-color: white; 
                border-radius: 10px; 
            }
            QScrollBar:vertical {
                border: none;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #cccccc;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        data_table.setAlternatingRowColors(True)

        # 모든 열을 고정 크기로 설정하고 사용자가 직접 크기 조정할 수 있게 함
        data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

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

        # 마지막 열이 남은 공간을 채우지 않도록 설정
        data_table.horizontalHeader().setStretchLastSection(False)

        # 위젯이 화면에 표시된 후에 열 너비 균등하게 조정 (100ms 지연)
        column_count = len(df.columns)
        QTimer.singleShot(100, lambda: DataTableComponent._adjust_column_widths(data_table, column_count))

        # 레이아웃에 테이블 추가
        layout.addWidget(data_table)

        # 컨테이너에 테이블 참조 저장
        container._data_table = data_table

        # 필터링된 데이터에 접근하기 위한 메서드 (필터가 없는 경우 원본 반환)
        container.get_filtered_data = lambda: df.copy()

        return container

    @staticmethod
    def _adjust_column_widths(table, column_count):
        """모든 열의 너비를 균등하게 조정하여 테이블을 꽉 채움"""
        if column_count <= 0:
            return

        total_width = table.viewport().width()
        column_width = total_width // column_count

        for i in range(column_count):
            table.setColumnWidth(i, column_width)

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