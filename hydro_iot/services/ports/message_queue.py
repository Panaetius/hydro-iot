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

    def send_spray_message(self, index: int, duration: int):
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

    def take_ndvi_image(self):
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

    def set_box_status(self, box1_status: bool, box2_status: bool, box3_status: bool):
        raise NotImplementedError()

    def get_config(self):
        raise NotImplementedError()

    def pause_system(self):
        raise NotImplementedError()

    def unpause_system(self):
        raise NotImplementedError()

    def get_system_state(self):
        raise NotImplementedError()

    def spray_boxes(self):
        raise NotImplementedError()

    def increase_ph(self):
        raise NotImplementedError()

    def decrease_ph(self):
        raise NotImplementedError()

    def increase_ec(self):
        raise NotImplementedError()

    def decrease_ec(self):
        raise NotImplementedError()

    def empty_tank(self):
        raise NotImplementedError()

    def increase_pressure(self):
        raise NotImplementedError()
