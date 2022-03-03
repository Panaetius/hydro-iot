from time import sleep

import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway
from hydro_iot.services.ports.spray_gateway import ISprayGateway


@inject.autoparams()
def empty_tank(
    logging: ILogging,
    system_state: SystemState,
    config: IConfig,
    spray_gateway: ISprayGateway,
    sensor_gateway: ISensorGateway,
) -> float:
    paused = system_state.paused
    system_state.paused = True
    system_state.spraying_boxes = True

    try:
        logging.info("Emptying Tank")

        num_boxes = len(config.pins.box_spray_pins)
        duration = 2000

        last_pressure = sensor_gateway.get_pressure()
        current_pressure = last_pressure - 0.1

        while current_pressure.bar < last_pressure.bar:
            last_pressure = current_pressure

            for i in range(num_boxes):
                spray_gateway.spray_box(i, duration)
                logging.info(f"Sprayed box {i} for {duration} ms")
                sleep(0.1)
            sleep(3)
            current_pressure = sensor_gateway.get_pressure()

        system_state.current_pressure_level = current_pressure
        return current_pressure.bar
    finally:
        system_state.spraying_boxes = False
        system_state.paused = paused


@inject.autoparams()
async def empty_tank_listener(eventhub: IEventHub, logging: ILogging):
    with eventhub.subscribe("pressure.empty") as queue:
        logging.info("Started listening for pressure.empty events")
        while True:
            _ = await queue.get()
            logging.info("Got empty pressure event")
            empty_tank()
