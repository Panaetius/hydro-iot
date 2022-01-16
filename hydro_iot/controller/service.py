import time
import systemd.daemon
import inject
from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.controller.config import load_config


@inject.autoparams()
def start_service(scheduler: IScheduler):
    print("Starting up ...")
    print("Startup complete")
    # Tell systemd that our service is ready
    systemd.daemon.notify("READY=1")

    config = load_config()

    # scheduler.repeat_job_at_interval(check_ph_ec_usecase, seconds=config.timings.check_ph_ex_interval)

    scheduler.start()
