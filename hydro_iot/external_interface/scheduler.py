from hydro_iot.controller.interface.scheduler import IScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Callable


class APScheduler(IScheduler):
    _scheduler = BackgroundScheduler()

    def start(self) -> None:
        self._scheduler.start()

    def stop(self) -> None:
        self._scheduler.shutdown()

    def repeat_job_at_interval(self, func: Callable, seconds: float, id: str) -> str:
        self._scheduler.add_job(func, "interval", seconds=seconds)

    def change_job_schedule(self, id: str, seconds: float) -> None:
        self._scheduler.reschedule_job(id, trigger="interval", seconds=seconds)
