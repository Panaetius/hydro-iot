from abc import ABC

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature


class ISensorGateway(ABC):
    def get_temperature(self) -> WaterTemperature:
        raise NotImplementedError()

    def get_ph(self) -> PH:
        raise NotImplementedError()

    def get_conductivity(self) -> Conductivity:
        raise NotImplementedError()

    def get_pressure(self) -> Pressure:
        raise NotImplementedError()
