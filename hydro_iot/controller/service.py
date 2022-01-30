import time

import cysystemd.daemon as daemon
import inject

from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.domain.config import IConfig
from hydro_iot.infrastructure.dummy_message_queue import DummyMQGateway
from hydro_iot.services.ports.message_queue import IMessageQueueSubscriber
from hydro_iot.services.read_ph_ec import read_ph_conductivity
from hydro_iot.services.read_temperature import read_temperature


@inject.autoparams()
def start_service(
    scheduler: IScheduler,
    config: IConfig,
    message_queue_subscriber: IMessageQueueSubscriber,
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

    scheduler.repeat_job_at_interval(
        func=read_ph_conductivity,
        seconds=config.timings.check_ph_ex_interval,
        id="check_ph_ec",
    )

    scheduler.start()

    message_queue = DummyMQGateway()
    message_queue.declare_listener(
        "commands",
        "user123.set_minimum_ph",
        message_queue_subscriber.set_minimum_ph_level,
    )
    message_queue.declare_listener(
        "commands",
        "user123.set_maximum_ph_level",
        message_queue_subscriber.set_maximum_ph_level,
    )
    message_queue.declare_listener(
        "commands",
        "user123.set_minimum_conductivity_level",
        message_queue_subscriber.set_minimum_conductivity_level,
    )
    message_queue.declare_listener(
        "commands",
        "user123.set_maximum_conductivity_level",
        message_queue_subscriber.set_maximum_conductivity_level,
    )
    message_queue.declare_listener(
        "commands",
        "user123.set_minimum_pump_pressure",
        message_queue_subscriber.set_minimum_pump_pressure,
    )
    message_queue.declare_listener(
        "commands",
        "user123.set_target_pump_pressure",
        message_queue_subscriber.set_target_pump_pressure,
    )
    message_queue.declare_listener(
        "commands",
        "user123.set_spray_timing",
        message_queue_subscriber.set_spray_timing,
    )
    message_queue.start_listening()
