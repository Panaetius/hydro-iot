from dataclasses import dataclass

from hydro_iot.domain.pressure import Pressure


@dataclass
class SystemState:
    last_fertilizer_ph_adjustment: float
    current_pressure_level: Pressure
    increasing_pressure: bool = False
    spraying_boxes: bool = False
