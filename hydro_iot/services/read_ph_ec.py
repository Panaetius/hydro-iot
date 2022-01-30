from time import sleep

import inject

from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


@inject.autoparams()
def read_ph_conductivity(sensor_gateway: ISensorGateway, message_gateway: IMessageQueuePublisher):
    ph = sensor_gateway.get_ph()

    sleep(0.5)

    ec = sensor_gateway.get_conductivity()

    message_gateway.send_ph_value(ph)
    message_gateway.send_fertilizer_level(ec)
