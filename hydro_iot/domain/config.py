from dataclasses import dataclass
from typing import List


@dataclass
class Timings:
    check_ph_ex_interval_ms: int
    check_temperature_interval_ms: int
    spray_box_timings_ms: List[int]


class IMessageQueueConnectionInfo:
    pass


@dataclass
class Pins:
    tds_sensor_adc_pin: int
    ph_sensor_adc_pin: int
    pressure_adc_sensor_pin: int
    tds_power_gpio_pin: int
    ph_power_gpio_pin: int
    box_spray_pins: List[int]


@dataclass
class IConfig:
    timings: Timings
    message_queue_connection: IMessageQueueConnectionInfo
    pins: Pins
