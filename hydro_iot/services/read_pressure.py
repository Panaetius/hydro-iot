import inject

from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


@inject.autoparams()
def read_pressure(sensor_gateway: ISensorGateway, message_gateway: IMessageQueuePublisher):
    pressure = sensor_gateway.get_pressure()

    message_gateway.send_pressure_status(pressure)
