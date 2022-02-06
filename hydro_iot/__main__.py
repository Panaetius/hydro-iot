from time import monotonic

import inject

from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.controller.service import start_service
from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.infrastructure.config import Config

# from hydro_iot.external_interface.rabbitmq_gateway import RabbitMQGateway
from hydro_iot.infrastructure.dummy_message_queue import DummyMQGateway
from hydro_iot.infrastructure.event_queue import AsyncioEventHub
from hydro_iot.infrastructure.scheduler import APScheduler
from hydro_iot.infrastructure.sensor_gateway import RaspberrySensorGateway
from hydro_iot.services.command_event_subscriber import CommandEventSubscriber
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


def config(binder):
    binder.bind_to_constructor(ISensorGateway, lambda: RaspberrySensorGateway())
    binder.bind_to_constructor(IMessageQueueSubscriber, lambda: CommandEventSubscriber())
    binder.bind_to_constructor(IMessageQueuePublisher, lambda: DummyMQGateway())
    binder.bind_to_constructor(IScheduler, lambda: APScheduler())
    binder.bind_to_constructor(
        SystemState, lambda: SystemState(last_fertilizer_ph_adjustment=monotonic(), last_ph_adjustment=monotonic())
    )
    binder.bind_to_constructor(IEventHub, lambda: AsyncioEventHub())

    config_path = "config.example.conf"
    binder.bind("config_path", config_path)
    binder.bind_to_constructor(IConfig, lambda: Config.load_config(config_path))


inject.configure(config)

start_service()
