from PyQt5.QtCore import QObject, QDate


class DataModel(QObject):
    """
    애플리케이션 데이터 모델
    파일 경로, 날짜 범위, 분석 결과 등의 데이터를 관리
    """

    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.start_date = None
        self.end_date = None
        self.analysis_results = None

    def set_file_path(self, file_path):
        """파일 경로 설정"""
        if file_path not in self.file_paths:
            self.file_paths.append(file_path)

    def get_file_paths(self):
        """파일 경로 목록 반환"""
        return self.file_paths

    def set_date_range(self, start_date, end_date):
        """날짜 범위 설정"""
        try:
            self.start_date = start_date
            self.end_date = end_date
            print(f"데이터 모델에 날짜 범위 설정: {start_date.toString('yyyy-MM-dd')} ~ {end_date.toString('yyyy-MM-dd')}")
        except Exception as e:
            print(f"날짜 범위 설정 중 오류 발생: {str(e)}")

    def get_date_range(self):
        """날짜 범위 반환"""
        return self.start_date, self.end_date

    def set_analysis_results(self, results):
        """분석 결과 설정"""
        self.analysis_results = results

    def get_analysis_results(self):
        """분석 결과 반환"""
        return self.analysis_results

    def clear(self):
        """모든 데이터 초기화"""
        self.file_paths = []
        self.start_date = None
        self.end_date = None
        self.analysis_results = None