import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


@inject.autoparams()
def read_pressure(
    sensor_gateway: ISensorGateway,
    logging: ILogging,
    system_state: SystemState,
    message_gateway: IMessageQueuePublisher,
    event_hub: IEventHub,
    config: IConfig,
):
    pressure = sensor_gateway.get_pressure()

    logging.info(f"Pressure: {pressure.bar} Bar")
    message_gateway.send_pressure_status(pressure)
    logging.info("Sent pressure status message")

    difference = system_state.current_pressure_level.bar - pressure.bar

    if (
        not system_state.increasing_pressure
        and not system_state.spraying_boxes
        and difference > config.levels.pressure_drop_error_threshold
    ):
        message_gateway.send_unexpected_pressure_drop(difference)

    if pressure.bar < config.levels.minimum_pressure_bar:
        event_hub.publish(key="pressure.increase", message="increase_pressure")
        logging.info("Triggered pressure increase")
