import pandas as pd


class DataModel:
    """페이지 간 데이터를 공유하기 위한 모델 클래스"""

    def __init__(self):
        self.file_path = None
        self.data = None
        self.results = None

    def set_file_path(self, path):
        self.file_path = path
        # 파일이 존재하면 로드
        try:
            self.load_data()
        except Exception as e:
            print(f"데이터 로드 중 오류 발생: {e}")

    def load_data(self):
        if self.file_path:
            self.data = pd.read_excel(self.file_path)
            return True
        return False

    def process_data(self, parameters):
        """데이터 처리 로직 구현"""
        if self.data is None:
            return False

        # 데이터 처리 로직
        # ...

        # 결과 저장
        self.results = {}  # 처리 결과
        return True

    def get_results(self):
        return self.results