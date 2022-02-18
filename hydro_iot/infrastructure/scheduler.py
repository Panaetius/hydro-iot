from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler

from hydro_iot.controller.interface.scheduler import IScheduler


class APScheduler(IScheduler):
    _scheduler = BackgroundScheduler({"apscheduler.job_defaults.max_instances": 10})

    def start(self) -> None:
        self._scheduler.start()

    def stop(self) -> None:
        self._scheduler.shutdown()

    def repeat_job_at_interval(self, func: Callable, seconds: float, id: str) -> str:
        self._scheduler.add_job(func, "interval", seconds=seconds, id=id)

    def change_job_schedule(self, id: str, seconds: float) -> None:
        self._scheduler.reschedule_job(id, trigger="interval", seconds=seconds)
