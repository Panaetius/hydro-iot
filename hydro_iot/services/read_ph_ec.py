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
    system_state.last_ph = ph
    logging.info(f"PH: {ph.value}")

    sleep(3)

    ec = sensor_gateway.get_conductivity()
    system_state.last_ec = ec
    logging.info(f"EC: {ec.microsiemens_per_meter} µS/m")

    message_gateway.send_ph_value(ph)
    message_gateway.send_fertilizer_level(ec)

    logging.info("Sent ph ec status messages")

    if monotonic() - system_state.last_fertilizer_ph_adjustment < config.timings.ph_ec_adjustment_downtime_ms / 1000:
        return

    if ec.microsiemens_per_meter < config.levels.min_ec:
        logging.info("Increasing EC")
        event_hub.publish(key="ec.up", message="increase_ec")
    elif config.pins.fresh_water_pump and ec.microsiemens_per_meter > config.levels.max_ec:
        logging.info("Decreasing EC")
        event_hub.publish(key="ec.down", message="decrease_ec")
    elif ph.value < config.levels.min_ph:
        logging.info("Increasing PH")
        event_hub.publish(key="ph.up", message="increase_ph")
    elif ph.value > config.levels.max_ph:
        logging.info("Decreasing PH")
        event_hub.publish(key="ph.down", message="decrease_ph")
