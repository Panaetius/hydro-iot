import asyncio
from datetime import datetime, timedelta

import cysystemd.daemon as daemon
import inject
from tzlocal import get_localzone

from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.domain.config import IConfig
from hydro_iot.infrastructure.dummy_message_queue import DummyMQGateway
from hydro_iot.services.adjust_nutrient_solution import (
    decrease_ec_listener,
    decrease_ph_listener,
    increase_ec_listener,
    increase_ph_listener,
)
from hydro_iot.services.empty_tank import empty_tank_listener
from hydro_iot.services.get_ndvi import calculate_ndvi
from hydro_iot.services.increase_pressure import increase_pressure_listener
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueueSubscriber
from hydro_iot.services.read_ph_ec import read_ph_conductivity
from hydro_iot.services.read_pressure import read_pressure
from hydro_iot.services.read_temperature import read_temperature
from hydro_iot.services.spray_boxes import spray_boxes


async def start_tasks():
    tasks = [
        asyncio.create_task(increase_ph_listener()),
        asyncio.create_task(decrease_ph_listener()),
        asyncio.create_task(increase_ec_listener()),
        asyncio.create_task(decrease_ec_listener()),
        asyncio.create_task(increase_pressure_listener()),
        asyncio.create_task(empty_tank_listener()),
    ]

    await asyncio.gather(*tasks)


@inject.autoparams()
def start_service(
    scheduler: IScheduler,
    config: IConfig,
    logging: ILogging,
    message_queue_subscriber: IMessageQueueSubscriber,
):
    logging.info("Starting up ...")

    logging.info("Setting up scheduler")
    timezone = get_localzone()

    scheduler.repeat_job_at_interval(
        func=read_temperature,
        seconds=config.timings.check_temperature_interval_ms / 1000.0,
        id="check_temperature",
        start_date=datetime.now(timezone) + timedelta(seconds=10),
    )

    scheduler.repeat_job_at_interval(
        func=read_ph_conductivity,
        seconds=config.timings.check_ph_ec_interval_ms / 1000.0,
        id="check_ph_ec",
        start_date=datetime.now(timezone) + timedelta(seconds=30),
    )

    scheduler.repeat_job_at_interval(
        func=spray_boxes,
        seconds=config.timings.spray_box_interval_ms / 1000.0,
        id="spray_boxes",
        start_date=datetime.now(timezone) + timedelta(seconds=45),
    )

    scheduler.repeat_job_at_interval(
        func=read_pressure,
        seconds=config.timings.check_pressure_interval_ms / 1000.0,
        id="read_pressure",
        start_date=datetime.now(timezone) + timedelta(seconds=5),
    )

    scheduler.repeat_job_at_interval(
        func=calculate_ndvi, seconds=config.timings.take_ndvi_image_interval_s, id="calculate_ndvi"
    )

    scheduler.start()

    # message_queue = DummyMQGateway()
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_minimum_ph",
    #     message_queue_subscriber.set_minimum_ph_level,
    # )
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_maximum_ph_level",
    #     message_queue_subscriber.set_maximum_ph_level,
    # )
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_minimum_conductivity_level",
    #     message_queue_subscriber.set_minimum_conductivity_level,
    # )
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_maximum_conductivity_level",
    #     message_queue_subscriber.set_maximum_conductivity_level,
    # )
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_minimum_pump_pressure",
    #     message_queue_subscriber.set_minimum_pump_pressure,
    # )
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_target_pump_pressure",
    #     message_queue_subscriber.set_target_pump_pressure,
    # )
    # message_queue.declare_listener(
    #     "commands",
    #     "user123.set_spray_timing",
    #     message_queue_subscriber.set_spray_timing,
    # )
    # message_queue.start_listening()

    logging.info("Starting async event loop")

    logging.info("Startup complete")
    # Tell systemd that our service is ready
    daemon.notify(daemon.Notification.READY)

    asyncio.run(start_tasks())
