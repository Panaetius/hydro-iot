import inject

from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


@inject.autoparams()
def read_temperature(
    sensor_gateway: ISensorGateway, message_gateway: IMessageQueuePublisher
):
    temperature = sensor_gateway.get_temperature()

    message_gateway.send_temperature_status(temperature)
