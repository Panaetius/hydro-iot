from dataclasses import dataclass
from threading import Lock
from typing import Optional

from hydro_iot.domain.pressure import Pressure


@dataclass
class SystemState:
    last_fertilizer_ph_adjustment: float
    current_pressure_level: Optional[Pressure] = None
    increasing_pressure: bool = False
    spraying_boxes: bool = False
    pressure_error: bool = False
    pressure_error_time: Optional[float] = None
    pressure_error_pressure: Optional[Pressure] = None
    power_output_lock: Lock = Lock()
