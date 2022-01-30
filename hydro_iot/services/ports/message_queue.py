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
