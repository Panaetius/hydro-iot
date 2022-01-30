import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.spray_gateway import ISprayGateway


@inject.autoparams()
def spray_boxes(message_gateway: IMessageQueuePublisher, config: IConfig, spray_gateway: ISprayGateway):
    num_boxes = len(config.pins.box_spray_pins)

    for i in range(num_boxes):
        spray_gateway.spray_box(i, config.timings.spray_box_timings_ms[i])

    message_gateway.send_spray_message(num_boxes)
