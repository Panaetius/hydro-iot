from abc import ABC

from hydro_iot.domain.pressure import Pressure


class PressureNotIncreasingError(Exception):
    def __init__(self, pressure: Pressure, message: str = "Pressure hasn't increased while pumping") -> None:
        self.message = message
        self.pressure = pressure
        super().__init__(self.message)


class IPumpGateway(ABC):
    def increase_system_pressure(self, target_pressure: Pressure) -> Pressure:
        raise NotImplementedError()

    def increase_fertilizer(self, flora_grow_ml: float, flora_micro_ml: float, flora_bloom_ml: float):
        raise NotImplementedError()

    def lower_fertilizer(self, amount_ml: float):
        raise NotImplementedError()

    def raise_ph(self, amount_ml: float):
        raise NotImplementedError()

    def lower_ph(self, amount_ml: float):
        raise NotImplementedError()
