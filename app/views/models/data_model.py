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
        self.settings = {}  # 설정 데이터를 저장할 딕셔너리 추가

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

    def update_settings(self, settings):
        """
        설정 업데이트 메서드

        Args:
            settings (dict): 업데이트할 설정 딕셔너리
        """
        # 설정 값 저장
        self.settings.update(settings)

        # 설정 변경 로그 출력
        print("DataModel: 설정이 업데이트되었습니다")

        # 설정에 따라 모델 상태 업데이트가 필요한 경우 여기에 구현
        # 예: 시간 제한 설정 업데이트
        if 'time_limit' in settings:
            print(f"  - 작업 시간 제한이 {settings['time_limit']}초로 설정되었습니다")

        # 필요한 경우 다른 설정에 따른 처리 추가
        if 'op_InputRoute' in settings and settings['op_InputRoute']:
            print(f"  - 입력 경로가 '{settings['op_InputRoute']}'(으)로 설정되었습니다")

        if 'op_SavingRoute' in settings and settings['op_SavingRoute']:
            print(f"  - 결과 저장 경로가 '{settings['op_SavingRoute']}'(으)로 설정되었습니다")

    def get_settings(self):
        """현재 설정 반환"""
        return self.settings

    def clear(self):
        """모든 데이터 초기화"""
        self.file_paths = []
        self.start_date = None
        self.end_date = None
        self.analysis_results = None
        # 설정은 초기화하지 않음 - 필요한 경우 아래 주석 해제
        self.settings = {}