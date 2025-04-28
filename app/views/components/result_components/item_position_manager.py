class ItemPositionManager:
    """아이템 위치 관리 유틸리티 클래스"""

    @staticmethod
    def get_day_and_shift(time_value):
        """Time 값에 따른 요일과 교대 정보 반환"""
        try:
            time_int = int(time_value)
            # 1,2(월), 3,4(화), 5,6(수), 7,8(목), 9,10(금), 11,12(토), 13,14(일)
            day_idx = (time_int - 1) // 2

            # 요일 인덱스(0-6)와 교대(주간/야간) 반환
            shift = "주간" if time_int % 2 == 1 else "야간"
            return day_idx, shift
        except (ValueError, TypeError):
            return -1, None

    @staticmethod
    def get_row_key(line, shift):
        """라인과 교대 정보로 행 키 생성"""
        return f"{line}_({shift})"

    @staticmethod
    def get_col_from_day_idx(day_idx, days):
        """요일 인덱스로 열 인덱스 반환"""
        if 0 <= day_idx < len(days):
            return day_idx
        return -1

    @staticmethod
    def find_row_index(row_key, row_headers):
        """행 키로 행 인덱스 찾기"""
        try:
            return row_headers.index(row_key)
        except ValueError:
            return -1