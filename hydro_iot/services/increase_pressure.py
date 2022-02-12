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


@inject.autoparams()
def increase_pressure(
    system_state: SystemState,
    logging: ILogging,
    pump_gateway: IPumpGateway,
    message_queue: IMessageQueuePublisher,
    config: IConfig,
):
    try:
        logging.info(f"Increasing pressure to {config.levels.maximum_pressure_bar}")
        pressure = pump_gateway.increase_system_pressure(
            target_pressure=Pressure(bar=config.levels.maximum_pressure_bar)
        )
        logging.info(f"Increased pressure to {pressure.bar} bar.")
        system_state.current_pressure_level = pressure
        message_queue.send_pressure_raised(pressure=pressure)
    except PressureNotIncreasingError:
        message_queue.send_could_not_raise_pressure()
        logging.error("Pressure couldn't be increased successfully.")


@inject.autoparams()
async def increase_pressure_listener(eventhub: IEventHub):
    with eventhub.subscribe("pressure.increase") as queue:
        _ = await queue.get()
        increase_pressure()
