from time import monotonic

import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.pump_gateway import (
    IPumpGateway,
    PressureNotIncreasingError,
)
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


def _check_pressure_error(
    system_state: SystemState, config: IConfig, sensor_gateway: ISensorGateway, logging: ILogging
):
    if monotonic() - system_state.pressure_error_time < config.timings.minimum_pressure_error_wait_time_ms / 1000.0:
        return False

    current_pressure = sensor_gateway.get_pressure()

    # check if system recovered
    diff_to_last_change_state = abs(system_state.current_pressure_level.bar - current_pressure.bar)
    diff_to_error_state = abs(system_state.pressure_error_pressure.bar - current_pressure.bar)

    if diff_to_last_change_state < config.levels.pressure_drop_error_threshold:
        logging.info("Recovering from pressure error, probably bad measurement")
        system_state.pressure_error = False
        system_state.pressure_error_pressure = None
        system_state.pressure_error_time = None
        return True

    if (
        system_state.pressure_error_pressure.bar > 4.0
        and diff_to_error_state < config.levels.pressure_drop_error_threshold
    ):
        # We're off from where we should be but pressure didn't drop anymore since the error occurred, so probably fine?
        logging.info("Recovering from pressure error, pressure dropped but didn't drop any further")
        system_state.pressure_error = False
        system_state.pressure_error_pressure = None
        system_state.pressure_error_time = None
        return True


@inject.autoparams()
def increase_pressure(
    system_state: SystemState,
    logging: ILogging,
    pump_gateway: IPumpGateway,
    sensor_gateway: ISensorGateway,
    message_queue: IMessageQueuePublisher,
    config: IConfig,
):
    if system_state.increasing_pressure:
        return

    if system_state.pressure_error and not _check_pressure_error(system_state, config, sensor_gateway, logging):
        logging.warn("Didn't pump due to pressure error")
        return

    try:
        logging.info(f"Increasing pressure to {config.levels.maximum_pressure_bar}")
        pressure = pump_gateway.increase_system_pressure(
            target_pressure=Pressure(bar=config.levels.maximum_pressure_bar)
        )
        logging.info(f"Increased pressure to {pressure.bar} bar.")
        system_state.current_pressure_level = pressure
        message_queue.send_pressure_raised(pressure=pressure)
    except PressureNotIncreasingError as e:
        system_state.pressure_error = True
        system_state.pressure_error_time = monotonic()
        system_state.pressure_error_pressure = e.pressure

        logging.error("Pressure couldn't be increased successfully.")
        message_queue.send_could_not_raise_pressure()


@inject.autoparams()
async def increase_pressure_listener(eventhub: IEventHub, logging: ILogging):
    with eventhub.subscribe("pressure.increase") as queue:
        logging.info("started listening to pressure up events")
        while True:
            _ = await queue.get()
            logging.info("Got increase pressure event")
            increase_pressure()
