import inject

from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


@inject.autoparams()
def read_temperature(
    sensor_gateway: ISensorGateway,
    system_state: SystemState,
    logging: ILogging,
    message_gateway: IMessageQueuePublisher,
):
    temperature = sensor_gateway.get_temperature()
    system_state.last_temperature = temperature
    logging.info(f"Temperature: {temperature.value} °C")

    message_gateway.send_temperature_status(temperature)
    logging.info("Sent temperature status message")
