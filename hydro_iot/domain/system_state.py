import json
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Optional

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature


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
    last_pressure: Optional[Pressure] = None
    last_ph: Optional[PH] = None
    last_ec: Optional[Conductivity] = None
    last_temperature: Optional[WaterTemperature] = None
    paused: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self))
