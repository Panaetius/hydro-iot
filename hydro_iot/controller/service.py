import asyncio
import time

import cysystemd.daemon as daemon
import inject

from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.domain.config import IConfig
from hydro_iot.infrastructure.dummy_message_queue import DummyMQGateway
from hydro_iot.services.adjust_nutrient_solution import (
    decrease_ec_listener,
    decrease_ph_listener,
    increase_ec_listener,
    increase_ph_listener,
)
from hydro_iot.services.ports.message_queue import IMessageQueueSubscriber
from hydro_iot.services.read_ph_ec import read_ph_conductivity
from hydro_iot.services.read_pressure import read_pressure
from hydro_iot.services.read_temperature import read_temperature
from hydro_iot.services.spray_boxes import spray_boxes


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
        seconds=config.timings.check_temperature_interval_ms / 1000.0,
        id="check_temperature",
    )

    scheduler.repeat_job_at_interval(
        func=read_ph_conductivity,
        seconds=config.timings.check_ph_ec_interval_ms / 1000.0,
        id="check_ph_ec",
    )

    scheduler.repeat_job_at_interval(
        func=spray_boxes,
        seconds=config.timings.spray_box_interval_ms / 1000.0,
        id="check_ph_ec",
    )

    scheduler.repeat_job_at_interval(
        func=read_pressure,
        seconds=config.timings.check_pressure_interval_ms / 1000.0,
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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(increase_ph_listener(), decrease_ph_listener(), increase_ec_listener(), decrease_ec_listener())
    )
