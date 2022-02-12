import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway
from hydro_iot.services.ports.spray_gateway import ISprayGateway


@inject.autoparams()
def spray_boxes(
    message_gateway: IMessageQueuePublisher,
    logging: ILogging,
    system_state: SystemState,
    config: IConfig,
    spray_gateway: ISprayGateway,
    sensor_gateway: ISensorGateway,
):
    logging.info("Spraying boxes")

    num_boxes = len(config.pins.box_spray_pins)

    for i in range(num_boxes):
        spray_gateway.spray_box(i, config.timings.spray_box_timings_ms[i])
        logging.info(f"Sprayed box {i} for {config.timings.spray_box_timings_ms[i]} ms")

    system_state.current_pressure_level = sensor_gateway.get_pressure()

    message_gateway.send_spray_message(num_boxes)
