from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.timing import SprayTiming
from hydro_iot.services.ports.message_queue import IMessageQueueSubscriber


class CommandEventSubscriber(IMessageQueueSubscriber):
    def set_minimum_ph_level(self, ph: PH):
        pass

    def set_maximum_ph_level(self, ph: PH):
        pass

    def set_minimum_conductivity_level(self, conductivity: Conductivity):
        pass

    def set_maximum_conductivity_level(self, conductivity: Conductivity):
        pass

    def set_minimum_pump_pressure(self, pressure: Pressure):
        pass

    def set_target_pump_pressure(self, pressure: Pressure):
        pass

    def set_spray_timing(self, timing: SprayTiming):
        pass
