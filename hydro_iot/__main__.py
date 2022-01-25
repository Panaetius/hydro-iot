from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.controller.service import start_service
from hydro_iot.external_interface.scheduler import APScheduler
from hydro_iot.usecase.interface.sensors_gateway import ISensorGateway
from hydro_iot.usecase.interface.message_queue import IMessageQueueGateway

from hydro_iot.gateway.sensor_gateway import RaspberrySensorGateway

# from hydro_iot.external_interface.rabbitmq_gateway import RabbitMQGateway
from hydro_iot.external_interface.dummy_message_queue import DummyMQGateway
from hydro_iot.external_interface.config import Config
import inject
from hydro_iot.controller.config import IConfig


def config(binder):
    binder.bind_to_constructor(ISensorGateway, lambda: RaspberrySensorGateway())
    binder.bind_to_constructor(IMessageQueueGateway, lambda: DummyMQGateway())
    binder.bind_to_constructor(IScheduler, lambda: APScheduler())

    config_path = "config.example.conf"
    binder.bind("config_path", config_path)
    binder.bind_to_constructor(IConfig, lambda: Config.load_config(config_path))


inject.configure(config)

start_service()
