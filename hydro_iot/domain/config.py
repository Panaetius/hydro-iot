from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Timings:
    check_ph_ec_interval_ms: int
    check_temperature_interval_ms: int
    check_pressure_interval_ms: int
    spray_box_interval_ms: int
    spray_box_timings_ms: List[int]
    ec_adjustment_downtime_ms: int
    ph_adjustment_downtime_ms: int
    minimum_pressure_error_wait_time_ms: int
    take_ndvi_image_interval_s: int
    ec_pump_prime_threshold_s: int


@dataclass
class Levels:
    max_ph: float
    min_ph: float
    max_ec: float
    min_ec: float
    minimum_pressure_bar: float
    maximum_pressure_bar: float
    pressure_drop_error_threshold: float
    boxes_enabled: List[bool]


@dataclass
class Amounts:
    ph_increase_ml: float
    ph_decrease_ml: float
    flora_grow_ml: float
    flora_micro_ml: float
    flora_bloom_ml: float
    fresh_water_ml: float


class IMessageQueueConnectionInfo:
    pass


@dataclass
class Pins:
    tds_sensor_adc: int
    ph_sensor_adc: int
    pressure_sensor_adc: int
    tds_power_gpio: int
    ph_power_gpio: int
    pressure_pump: int
    flora_grow_pump: int
    flora_micro_pump: int
    flora_bloom_pump: int
    ph_up_pump: int
    ph_down_pump: int
    box_spray_pins: List[int]
    camera_ir_filter_pin: int
    fresh_water_pump: Optional[int] = None


@dataclass
class IConfig:
    timings: Timings
    message_queue_connection: IMessageQueueConnectionInfo
    pins: Pins
    levels: Levels
    amounts: Amounts

    def save_config(self, path: str):
        raise NotImplementedError()

    def to_json(self) -> str:
        raise NotImplementedError()
