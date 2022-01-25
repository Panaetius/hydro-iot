import time
import cysystemd.daemon as daemon
import inject
from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.controller.config import IConfig
from hydro_iot.usecase.interface.message_queue import IMessageQueueGateway
from hydro_iot.usecase.read_temperature import read_temperature


@inject.autoparams()
def start_service(
    scheduler: IScheduler, config: IConfig, message_queue: IMessageQueueGateway
):
    print("Starting up ...")
    print("Startup complete")
    # Tell systemd that our service is ready
    daemon.notify(daemon.Notification.READY)

    scheduler.repeat_job_at_interval(
        func=read_temperature,
        seconds=config.timings.check_temperature_interval,
        id="check_temperature",
    )

    scheduler.start()

    message_queue.declare_listener("commands", "user123.*", lambda a, b, c, d: print(a))
    message_queue.start_listening()
