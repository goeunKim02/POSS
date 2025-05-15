import json
import os
import copy

"""
설정값을 저장하고 관리하기 위한 중앙 저장소 클래스
"""
class SettingsStore:
    # 기본 설정 값 정의
    _default_settings = {
        # Basic 설정
        "time_limit": 300,  # 수행시간(초)
        "weight_sop_ox": 1.0,  # SOP 가중치
        "weight_mat_qty": 1.0,  # 자재 가중치
        "weight_linecnt_bypjt": 1.0,  # PJT분산 가중치
        "weight_linecnt_byitem": 1.0,  # Item분산 가중치
        "weight_operation": 1.0,  # 가동률 가중치

        # Pre_option 설정
        "op_timeset_1": [],  # 계획유지율_1 (1~14일 중 선택)
        "op_SKU_1": 100,  # SKU_계획유지율_1
        "op_RMC_1": 100,  # RMC_계획유지율_1
        "op_timeset_2": [],  # 계획유지율_2 (1~14일 중 선택)
        "op_SKU_2": 100,  # SKU_계획유지율_2
        "op_RMC_2": 100,  # RMC_계획유지율_2
        "max_min_ratio_ox": 0,  # 사전할당 비율 반영여부
        "max_min_margin": 0,  # 1차 수행 사전할당 비율

        # Detail 설정
        "op_InputRoute": "",  # 인풋경로
        "op_SavingRoute": "",  # 아웃풋경로
        "itemcnt_limit_ox": 0,  # 기종변경 시간 반영여부
        "itemcnt_limit": 1,  # 기종변경 최소 종수
        "itemcnt_limit_max_i_ox": 0,  # 최대 할당 종수_i 반영여부
        "itemcnt_limit_max_i": 1,  # 최대 할당 종수_i 제조동
        "itemcnt_limit_max_o_ox": 0,  # 최대 할당 종수_그 외 반영여부
        "itemcnt_limit_max_o": 1,  # 최대 할당 종수_그 외 제조동
        "mat_use": 0,  # 자재제약 반영여부
        "P999_line_ox": 0,  # P999 제약 반영여부
        "P999_line": "",  # P999 할당라인
        "weight_day_ox": 0,  # shift별 가중치 반영여부
        "weight_day": [1.0, 1.0, 1.0]  # shift별 가중치 (기본값: 3개 shift)
    }

    _settings = {}
    _settings = copy.deepcopy(_default_settings)

    _config_file = "settings.json"

    """
    설정값 조회
    """
    @classmethod
    def get(cls, key, default=None):
        return cls._settings.get(key, default)

    """
    설정값 저장
    """
    @classmethod
    def set(cls, key, value):
        cls._settings[key] = value

    """
    여러 설정값 일괄 업데이트
    """
    @classmethod
    def update(cls, settings_dict):
        cls._settings.update(settings_dict)

    """
    모든 설정값 조회
    """
    @classmethod
    def get_all(cls):
        return copy.deepcopy(cls._settings)

    """
    설정값을 파일에 저장
    """
    @classmethod
    def save_settings(cls, file_path=None):
        if file_path is None:
            os.makedirs('config', exist_ok=True)
            file_path = os.path.join('config', cls._config_file)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cls._settings, f, indent=4, ensure_ascii=False)

    """
    파일에서 설정값 로드
    """
    @classmethod
    def load_settings(cls, file_path=None):
        if file_path is None:
            file_path = os.path.join('config', cls._config_file)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    cls._settings.update(loaded_settings)
                return True
            return False
        except Exception as e:
            print(f"설정 파일 로드 중 오류 발생: {e}")
            return False

    """
    설정값을 기본값으로 초기화
    """
    @classmethod
    def reset_to_default(cls):
        cls._settings = copy.deepcopy(cls._default_settings)
        cls.save_settings()
        
        return copy.deepcopy(cls._settings)