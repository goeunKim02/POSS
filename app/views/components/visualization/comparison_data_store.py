"""
비교 차트를 위한 원본/조정 데이터 저장소
"""
class ComparisonDataStore:
    
    _instance = None
    
    """
    싱글턴 인스턴스 반환
    """
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ComparisonDataStore()
        return cls._instance
    
    def __init__(self):
        self.original_data = {}
        self.current_data = {}
    
    """
    원본 데이터 저장
    """
    def save_original(self, data_type, data):
        self.original_data[data_type] = data.copy() if hasattr(data, 'copy') else data
    
    """
    현재 데이터 업데이트
    """
    def update_current(self, data_type, data):
        self.current_data[data_type] = data
    
    """비교 데이터 형식으로 반환
    
    Args:
        data_type (str): 데이터 유형 (예: 'capa', 'utilization')
        current_data: 현재 데이터 (없으면 이전에 저장된 현재 데이터 사용)
        
    Returns:
        dict: {'original': 원본 데이터, 'adjusted': 현재 데이터} 형식
    """
    def get_comparison_data(self, data_type, current_data=None):
        # 원본 데이터 가져오기
        original = self.original_data.get(data_type)
        
        # 현재 데이터 설정
        if current_data is not None:
            # 파라미터로 받은 현재 데이터 사용
            adjusted = current_data
            # 현재 데이터 업데이트
            self.update_current(data_type, current_data)
        else:
            # 저장된 현재 데이터 사용
            adjusted = self.current_data.get(data_type)
        
        # 원본 데이터가 없거나 현재 데이터가 없는 경우
        if original is None:
            # 현재 데이터를 원본으로 저장
            if adjusted is not None:
                self.save_original(data_type, adjusted)
                original = adjusted
        
        # 현재 데이터가 없는 경우
        if adjusted is None:
            adjusted = original
        
        # 비교 데이터 형식으로 반환
        return {
            'original': original,
            'adjusted': adjusted
        }
    
    """
    원본 데이터 존재 여부 확인
    """
    def has_original(self, data_type):
        return data_type in self.original_data
    
    """데이터 초기화
    
    Args:
        data_type (str, optional): 초기화할 데이터 유형. None이면 모든 데이터 초기화
    """
    def reset(self, data_type=None):
        if data_type:
            self.original_data.pop(data_type, None)
            self.current_data.pop(data_type, None)
        else:
            self.original_data.clear()
            self.current_data.clear()