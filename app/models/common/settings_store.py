# app/models/common/settings_store.py
import json
import os


class SettingsStore:
    """
    설정값을 저장하고 관리하기 위한 중앙 저장소 클래스
    """
    _settings = {
        # Basic 설정
        "time_limit": 1,  # 수행시간(초)
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
        "max_min_margin": 10,  # 1차 수행 사전할당 비율

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

    _config_file = "settings.json"

    @classmethod
    def get(cls, key, default=None):
        """설정값 조회"""
        return cls._settings.get(key, default)

    @classmethod
    def set(cls, key, value):
        """설정값 저장"""
        cls._settings[key] = value
        cls.save_settings()  # 설정 변경시 자동 저장

    @classmethod
    def update(cls, settings_dict):
        """여러 설정값 일괄 업데이트"""
        cls._settings.update(settings_dict)
        cls.save_settings()  # 설정 변경시 자동 저장

    @classmethod
    def get_all(cls):
        """모든 설정값 조회"""
        return cls._settings.copy()

    @classmethod
    def save_settings(cls, file_path=None):
        """설정값을 파일에 저장"""
        if file_path is None:
            # config 디렉토리가 없으면 생성
            os.makedirs('config', exist_ok=True)
            file_path = os.path.join('config', cls._config_file)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cls._settings, f, indent=4, ensure_ascii=False)

    @classmethod
    def load_settings(cls, file_path=None):
        """파일에서 설정값 로드"""
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