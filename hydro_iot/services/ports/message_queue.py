from abc import ABC
from typing import Callable

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature
from hydro_iot.domain.timing import SprayTiming


class IMessageQueuePublisher(ABC):
    def send_temperature_status(self, temperature: WaterTemperature):
        raise NotImplementedError()

    def send_ph_value(self, ph: PH):
        raise NotImplementedError()

    def send_fertilizer_level(self, ec: Conductivity):
        raise NotImplementedError()

    def send_pressure_status(self, pressure: Pressure):
        raise NotImplementedError()

    def send_spray_message(self, num_boxes: int):
        raise NotImplementedError()

    def send_ph_raised(self, amount: float):
        raise NotImplementedError()

    def send_ph_lowered(self, amount: float):
        raise NotImplementedError()

    def send_ec_lowered(self, amount: float):
        raise NotImplementedError()

    def send_ec_increased(self, amount_grow: float, amount_micro: float, amount_bloom: float):
        raise NotImplementedError()

    def send_pressure_raised(self, pressure: Pressure):
        raise NotImplementedError()

    def send_unexpected_pressure_drop(self, pressure_drop: float):
        raise NotImplementedError()

    def send_could_not_raise_pressure(self):
        raise NotImplementedError()


class IMessageQueueSubscriber(ABC):
    def set_minimum_ph_level(self, ph: PH):
        raise NotImplementedError()

    def set_maximum_ph_level(self, ph: PH):
        raise NotImplementedError()

    def set_minimum_conductivity_level(self, conductivity: Conductivity):
        raise NotImplementedError()

    def set_maximum_conductivity_level(self, conductivity: Conductivity):
        raise NotImplementedError()

    def set_minimum_pump_pressure(self, pressure: Pressure):
        raise NotImplementedError()

    def set_target_pump_pressure(self, pressure: Pressure):
        raise NotImplementedError()

    def set_spray_timing(self, timing: SprayTiming):
        raise NotImplementedError()
