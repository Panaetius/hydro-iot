from time import monotonic, sleep

import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


@inject.autoparams()
def read_ph_conductivity(
    sensor_gateway: ISensorGateway,
    message_gateway: IMessageQueuePublisher,
    event_hub: IEventHub,
    config: IConfig,
    system_state: SystemState,
    logging: ILogging,
):
    ph = sensor_gateway.get_ph()
    logging.info(f"PH: {ph.value}")

    sleep(0.5)

    ec = sensor_gateway.get_conductivity()
    logging.info(f"EC: {ec.microsiemens_per_meter}")

    message_gateway.send_ph_value(ph)
    message_gateway.send_fertilizer_level(ec)

    logging.info("Sent ph ec messages")

    if monotonic() - system_state.last_fertilizer_ph_adjustment < config.timings.ph_ec_adjustment_downtime_ms:
        return

    if ec.microsiemens_per_meter < config.levels.min_ec:
        event_hub.publish(key="ec.up", message="increase_ec")
        logging.info("Increasing EC")
    elif config.pins.fresh_water_pump and ec.microsiemens_per_meter > config.levels.max_ec:
        event_hub.publish(key="ec.down", message="decrease_ec")
        logging.info("Decreasing EC")
    elif ph.value < config.levels.min_ph:
        event_hub.publish(key="ph.up", message="increase_ph")
        logging.info("Increasing PH")
    elif ph.value > config.levels.max_ph:
        event_hub.publish(key="ph.down", message="decrease_ph")
        logging.info("Decreasing PH")
