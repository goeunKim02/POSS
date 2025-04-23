from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame
from PyQt5.QtGui import QCursor

class FileUploadComponent(QWidget):
    """
    파일 업로드 컴포넌트
    파일 선택, 표시, 제거 기능을 제공합니다.
    """
    file_selected = pyqtSignal(str)  # 파일이 선택되었을 때 발생하는 시그널
    file_removed = pyqtSignal(str)  # 파일이 제거되었을 때 발생하는 시그널

    def __init__(self, parent=None, label_text="Upload Data:", button_text="Browse..."):
        super().__init__(parent)
        self.file_paths = []  # 선택된 파일 경로들을 저장할 리스트
        self.no_files_label = None
        self.label_text = label_text
        self.button_text = button_text
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # 라벨 추가
        upload_label = QLabel(self.label_text)
        self.layout.addWidget(upload_label)

        # 파일명들을 표시할 영역
        files_container = QWidget()
        self.files_display = QHBoxLayout(files_container)
        self.files_display.setContentsMargins(5, 0, 5, 0)
        self.files_display.setSpacing(5)

        # 처음에는 안내 텍스트 표시
        self.no_files_label = QLabel("No files selected")
        self.no_files_label.setStyleSheet("color: #888888;")
        self.files_display.addWidget(self.no_files_label)
        self.files_display.addStretch()  # 파일 라벨들이 왼쪽에 정렬되도록

        # 파일 선택 버튼
        browse_btn = QPushButton(self.button_text)
        browse_btn.setFixedWidth(150)
        browse_btn.clicked.connect(self.on_file_btn_clicked)
        browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                height: 100px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #004C99; /* 원래 색상보다 약간 어두운 색 */
            }
            QPushButton:pressed {
                background-color: #003366; /* 클릭 시에는 더 어두운 색 */
            }
        """)

        # 레이아웃에 위젯 추가
        self.layout.addWidget(files_container, 1)
        self.layout.addWidget(browse_btn)

    def add_file_label(self, file_path):
        """파일 라벨 추가"""
        # 첫 파일이 추가되면 안내 텍스트 제거
        if self.no_files_label:
            self.files_display.removeWidget(self.no_files_label)
            self.no_files_label.deleteLater()
            self.no_files_label = None
            # stretch도 제거하고 다시 추가
            # stretch 항목 찾기
            for i in range(self.files_display.count()):
                if self.files_display.itemAt(i).spacerItem():
                    self.files_display.removeItem(self.files_display.itemAt(i))
                    break

        file_name = file_path.split('/')[-1]

        # 파일 라벨 생성 - 더 작고 컴팩트하게
        file_frame = QFrame()
        file_frame.setStyleSheet("QFrame { background-color: #e0e0ff; border-radius: 3px; }")
        file_frame.setFixedHeight(24)  # 높이 고정

        file_layout = QHBoxLayout(file_frame)
        file_layout.setContentsMargins(5, 0, 3, 0)
        file_layout.setSpacing(2)

        file_label = QLabel(file_name)
        file_label.setStyleSheet("font-size: 9pt;")

        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #555; border: none; font-weight: bold; } "
            "QPushButton:hover { color: red; }")
        remove_btn.clicked.connect(lambda: self.remove_file(file_path, file_frame))

        file_layout.addWidget(file_label)
        file_layout.addWidget(remove_btn)

        # 파일 위젯 추가
        self.files_display.addWidget(file_frame)
        self.files_display.addStretch()  # 항상 맨 뒤에 stretch 유지

        # 파일 경로 저장
        self.file_paths.append(file_path)

        # 파일이 선택되면 시그널 발생
        self.file_selected.emit(file_path)

        return file_frame

    def remove_file(self, file_path, file_frame):
        """파일 제거"""
        # UI에서 라벨 제거
        self.files_display.removeWidget(file_frame)
        file_frame.deleteLater()

        # 파일 경로 목록에서 제거
        if file_path in self.file_paths:
            self.file_paths.remove(file_path)
            # 파일 제거 시그널 발생
            self.file_removed.emit(file_path)

        # 모든 파일이 제거되면 안내 텍스트 다시 표시
        if not self.file_paths and not self.no_files_label:
            self.no_files_label = QLabel("No files selected")
            self.no_files_label.setStyleSheet("color: #888888;")

            # stretch 항목 찾기 및 제거
            for i in range(self.files_display.count()):
                if self.files_display.itemAt(i).spacerItem():
                    self.files_display.removeItem(self.files_display.itemAt(i))
                    break

            self.files_display.addWidget(self.no_files_label)
            self.files_display.addStretch()

    def on_file_btn_clicked(self):
        """파일 선택 다이얼로그 표시 - 여러 파일 선택 가능"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Excel 파일 선택 (여러 파일 선택 가능)",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        # 선택된 파일들 처리
        for file_path in file_paths:
            # 중복 파일 체크
            if file_path not in self.file_paths:
                self.add_file_label(file_path)

    def get_file_paths(self):
        """선택된 파일 경로 리스트 반환"""
        return self.file_paths

    def clear_files(self):
        """모든 파일 제거"""
        # 파일 리스트 복사해서 순회 (순회 중 제거 때문)
        file_paths_copy = self.file_paths.copy()

        # 모든 위젯 제거
        for i in range(self.files_display.count()):
            item = self.files_display.itemAt(0)
            if item.widget():
                item.widget().deleteLater()
            self.files_display.removeItem(item)

        # 파일 경로 리스트 비우기
        self.file_paths.clear()

        # 안내 텍스트 다시 표시
        self.no_files_label = QLabel("No files selected")
        self.no_files_label.setStyleSheet("color: #888888;")
        self.files_display.addWidget(self.no_files_label)
        self.files_display.addStretch()

        # 제거된 모든 파일에 대해 시그널 발생
        for file_path in file_paths_copy:
            self.file_removed.emit(file_path)