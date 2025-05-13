import threading
import time
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

from app.core.optimizer import Optimizer
from app.models.common.settings_store import SettingsStore

class ProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame)

    def __init__(self, df: pd.DataFrame, projects: list, time_limit: int = None):
        super().__init__()
        self.df = df
        self.projects = projects
        # 설정된 time_limit 없으면 기본값 사용
        self.time_limit = time_limit or SettingsStore._settings.get("time_limit", 300)
        self._opt_result = None

    def run(self):
        # 최적화 작업
        def do_opt():
            results = Optimizer().run_optimization({
                'pre_assigned_df': self.df,
                'selected_projects': self.projects
            })
            self._opt_result = results['assignment_result']

        opt_thread = threading.Thread(target=do_opt, daemon=True)
        opt_thread.start()

        # 진행률 업데이트
        for i in range(self.time_limit):
            time.sleep(1)
            pct = int((i+1) / self.time_limit * 100)
            self.progress.emit(pct)

            if self._opt_result is not None:
                self.progress.emit(100)
                self.finished.emit(self._opt_result)
                return

        # 시간 제한 후 처리
        if self._opt_result is not None:
            self.finished.emit(self._opt_result)
        else:
            self.finished.emit(self.df)