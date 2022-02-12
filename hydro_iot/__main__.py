from time import monotonic

import inject
import RPi.GPIO as GPIO

from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.controller.service import start_service
from hydro_iot.domain.config import IConfig
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.system_state import SystemState
from hydro_iot.infrastructure.config import Config

# from hydro_iot.external_interface.rabbitmq_gateway import RabbitMQGateway
from hydro_iot.infrastructure.dummy_message_queue import DummyMQGateway
from hydro_iot.infrastructure.event_queue import AsyncioEventHub
from hydro_iot.infrastructure.logging import Logging
from hydro_iot.infrastructure.pump_gateway import PumpGateway
from hydro_iot.infrastructure.scheduler import APScheduler
from hydro_iot.infrastructure.sensor_gateway import RaspberrySensorGateway
from hydro_iot.infrastructure.spray_gateway import SprayGateway
from hydro_iot.services.command_event_subscriber import CommandEventSubscriber
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)
from hydro_iot.services.ports.pump_gateway import IPumpGateway
from hydro_iot.services.ports.sensors_gateway import ISensorGateway
from hydro_iot.services.ports.spray_gateway import ISprayGateway


def config(binder):
    binder.bind_to_constructor(ISensorGateway, lambda: RaspberrySensorGateway())
    binder.bind_to_constructor(IMessageQueueSubscriber, lambda: CommandEventSubscriber())
    binder.bind_to_constructor(IMessageQueuePublisher, lambda: DummyMQGateway())
    binder.bind_to_constructor(IScheduler, lambda: APScheduler())
    binder.bind_to_constructor(
        SystemState,
        lambda: SystemState(last_fertilizer_ph_adjustment=monotonic()),
    )
    binder.bind_to_constructor(IEventHub, lambda: AsyncioEventHub())
    binder.bind_to_constructor(ISprayGateway, lambda: SprayGateway())
    binder.bind_to_constructor(IPumpGateway, lambda: PumpGateway())
    binder.bind_to_constructor(ILogging, lambda: Logging())

    config_path = "config.example.hocon"
    binder.bind("config_path", config_path)
    binder.bind_to_constructor(IConfig, lambda: Config.load_config(config_path))


inject.configure(config)

try:
    start_service()
finally:
    GPIO.cleanup()
