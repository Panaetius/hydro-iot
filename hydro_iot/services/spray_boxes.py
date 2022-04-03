from time import sleep

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
    if system_state.spraying_boxes or system_state.paused:
        return
    system_state.spraying_boxes = True

    try:
        logging.info("Spraying boxes")

        num_boxes = len(config.pins.box_spray_pins)

        with system_state.power_output_lock:
            for i in range(num_boxes):
                if not config.levels.boxes_enabled[i]:
                    continue

                duration = config.timings.spray_box_timings_ms[i]
                spray_gateway.spray_box(i, duration)
                logging.info(f"Sprayed box {i} for {duration} ms")

                message_gateway.send_spray_message(i, duration)
                sleep(0.1)

        system_state.current_pressure_level = sensor_gateway.get_pressure()
    finally:
        system_state.spraying_boxes = False
