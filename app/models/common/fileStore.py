# 파일 경로를 저장하는 중앙 저장소
class FilePaths:
    _paths = {
        "dynamic_excel_file": None,
        "master_excel_file": None,
        "demand_excel_file": None,
        "etc_excel_file": None,
        "output_file": None,
        "result_file": None,
    }

    # 파일 경로 조회
    @classmethod
    def get(cls, key):
        return cls._paths.get(key)
    
    # 파일 경로 등록
    @classmethod
    def set(cls, key, path):
        cls._paths[key] = path

    # 파일 경로 갱신
    @classmethod
    def update(cls, paths_dict):
        cls._paths.update(paths_dict)