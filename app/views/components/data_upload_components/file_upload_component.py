from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame
from PyQt5.QtGui import QCursor, QFont


class FileUploadComponent(QWidget):
    """
    파일 업로드 컴포넌트
    파일 선택, 표시, 제거 기능을 제공합니다.
    """
    file_selected = pyqtSignal(str)  # 파일이 선택되었을 때 발생하는 시그널
    file_removed = pyqtSignal(str)  # 파일이 제거되었을 때 발생하는 시그널

    def __init__(self, parent=None, label_text="Upload Data:", button_text="Browse"):
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
        upload_label.setFont(QFont("Arial"))
        upload_label.setStyleSheet("border: none")
        self.layout.addWidget(upload_label)

        # 파일명들을 표시할 영역
        files_container = QWidget()
        self.files_display = QHBoxLayout(files_container)
        self.files_display.setContentsMargins(5, 0, 5, 0)
        self.files_display.setSpacing(5)  # 파일 항목 간격 설정
        self.files_display.setAlignment(Qt.AlignLeft)  # 왼쪽 정렬 설정

        # 처음에는 안내 텍스트 표시
        self.no_files_label = QLabel("No files selected")
        self.no_files_label.setFont(QFont("Arial"))
        self.no_files_label.setStyleSheet("color: #888888; border:none; background-color: transparent; margin-left:5px")
        self.files_display.addWidget(self.no_files_label)
        self.files_display.addStretch(1)  # 파일 라벨들이 왼쪽에 정렬되도록

        # 파일 선택 버튼
        browse_btn = QPushButton(self.button_text)
        browse_btn.setFixedWidth(150)
        browse_btn.clicked.connect(self.on_file_btn_clicked)
        browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        browse_btn_font = QFont("Arial")
        browse_btn_font.setPointSize(9)
        browse_btn_font.setBold(True)
        browse_btn.setFont(browse_btn_font)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #1428A0; 
                color: white; 
                height: 100px; 
                border-radius: 10px;
                border:none;
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

        # 항상 추가하기 전에 모든 stretch 제거
        for i in range(self.files_display.count() - 1, -1, -1):
            if self.files_display.itemAt(i).spacerItem():
                self.files_display.removeItem(self.files_display.itemAt(i))

        file_name = file_path.split('/')[-1]

        # 파일 라벨 생성 - 더 작고 컴팩트하게
        file_frame = QFrame()
        file_frame.setStyleSheet("QFrame { background-color: #e0e0ff; border-radius: 10px; border:none; padding: 2px; }")
        file_frame.setFixedHeight(30)  # 높이 고정

        file_layout = QHBoxLayout(file_frame)
        file_layout.setContentsMargins(3, 0, 3, 0)
        file_layout.setSpacing(2)

        file_label = QLabel(file_name)
        file_label_font = QFont("Arial",9)
        file_label.setFont(file_label_font)

        remove_btn = QPushButton("X")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #555; border: none; font-weight: bold; } "
            "QPushButton:hover { color: red; }")
        remove_btn.clicked.connect(lambda: self.remove_file(file_path, file_frame))
        remove_btn.setCursor(QCursor(Qt.PointingHandCursor))

        file_layout.addWidget(file_label)
        file_layout.addWidget(remove_btn)

        # 파일 위젯 추가
        self.files_display.addWidget(file_frame)

        # 파일 경로 저장
        self.file_paths.append(file_path)

        # 파일이 선택되면 시그널 발생
        self.file_selected.emit(file_path)

        # 마지막에 한 번만 stretch 추가
        self.files_display.addStretch(1)

        return file_frame

    def remove_file(self, file_path, file_frame):
        """파일 제거"""
        # UI에서 라벨 제거
        self.files_display.removeWidget(file_frame)
        file_frame.deleteLater()

        # 남아있는 위젯 중 spacerItem(stretch)을 확인하고 제거
        if self.file_paths.count(file_path) == 1:  # 이 파일이 마지막으로 제거될 예정이라면
            # 모든 stretch 항목 찾아서 제거
            for i in range(self.files_display.count() - 1, -1, -1):
                if self.files_display.itemAt(i).spacerItem():
                    self.files_display.removeItem(self.files_display.itemAt(i))

        # 파일 경로 목록에서 제거
        if file_path in self.file_paths:
            self.file_paths.remove(file_path)
            # 파일 제거 시그널 발생
            self.file_removed.emit(file_path)

        # 파일이 남아 있으면 마지막에 다시 stretch 추가
        if self.file_paths and len(self.file_paths) > 0:
            self.files_display.addStretch(1)

        # 모든 파일이 제거되면 안내 텍스트 다시 표시
        if not self.file_paths and not self.no_files_label:
            # 모든 기존 항목 제거 (stretch 포함)
            while self.files_display.count():
                item = self.files_display.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # 안내 텍스트 추가
            self.no_files_label = QLabel("No files selected")
            self.no_files_label.setFont(QFont("Arial"))
            self.no_files_label.setStyleSheet("color: #888888; border: none; background-color: transparent; margin-left:5px")

            self.files_display.addWidget(self.no_files_label)
            self.files_display.addStretch(1)  # 왼쪽 정렬을 위한 stretch

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

    # def clear_files(self):
    #     """모든 파일 제거"""
    #     # 파일 리스트 복사해서 순회
    #     file_paths_copy = self.file_paths.copy()
    #
    #     # 모든 위젯 제거 - 레이아웃을 완전히 비움
    #     while self.files_display.count():
    #         item = self.files_display.takeAt(0)
    #         if item.widget():
    #             item.widget().deleteLater()
    #
    #     # 파일 경로 리스트 비우기
    #     self.file_paths.clear()
    #
    #     # 안내 텍스트 다시 표시 - 초기 설정과 동일하게
    #     self.no_files_label = QLabel("No files selected")
    #     self.no_files_label.setFont(QFont("Arial"))
    #     self.no_files_label.setStyleSheet("color: #888888; border:none; background-color: transparent;")
    #     self.files_display.addWidget(self.no_files_label)
    #     self.files_display.addStretch(1)  # 왼쪽 정렬을 위한 stretch
    #
    #     # 제거된 모든 파일에 대해 시그널 발생
    #     for file_path in file_paths_copy:
    #         self.file_removed.emit(file_path)