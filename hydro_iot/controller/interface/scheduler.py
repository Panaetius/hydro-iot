from abc import ABC

from typing import Callable


class IScheduler(ABC):
    def start(self):
        pass

    def stop(self):
        pass

    def repeat_job_at_interval(self, func: Callable, seconds: float, id: str):
        pass

    def change_job_schedule(self, id: str, seconds: float):
        pass
