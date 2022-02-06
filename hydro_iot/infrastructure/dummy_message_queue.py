from time import sleep
from typing import Callable

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature
from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)


class DummyMQGateway(IMessageQueuePublisher):
    def send_temperature_status(self, temperature: WaterTemperature):
        pass

    def send_ph_value(self, ph: PH):
        pass

    def send_fertilizer_level(self, ec: Conductivity):
        pass

    def send_pressure_status(self, pressure: Pressure):
        pass

    def send_spray_message(self, num_boxes: int):
        pass

    def send_ph_raised(self, amount: float):
        pass

    def send_ph_lowered(self, amount: float):
        pass

    def send_ec_lowered(self, amount: float):
        pass

    def send_ec_increased(self, amount_grow: float, amount_micro: float, amount_bloom: float):
        pass
