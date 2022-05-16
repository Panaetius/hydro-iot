import json
from dataclasses import dataclass, field
from threading import Lock
from typing import List, Optional

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature


@dataclass
class SystemState:
    last_ph_adjustment: float
    last_fertilizer_adjustment: float
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
        result = {
            "paused": self.paused,
            "last_pressure": self.last_pressure.bar if self.last_pressure else None,
            "last_ph": self.last_ph.value if self.last_ph else None,
            "last_ec": self.last_ec.microsiemens_per_meter if self.last_ec else None,
            "last_temperature": self.last_temperature.value if self.last_temperature else None,
        }

        return json.dumps(result)
