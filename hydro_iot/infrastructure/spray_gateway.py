from time import sleep

import inject
import RPi.GPIO as GPIO

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.spray_gateway import ISprayGateway


class SprayGateway(ISprayGateway):
    config = inject.attr(IConfig)
    _log = inject.attr(ILogging)
    system_state = inject.attr(SystemState)

    def __init__(self) -> None:
        self._log.info("Init spray gateway")
        GPIO.setmode(GPIO.BCM)

        for box_pin in self.config.pins.box_spray_pins:
            GPIO.setup(box_pin, GPIO.OUT)

    def spray_box(self, index: int, duration: int):
        with self.system_state.power_output_lock:
            try:
                GPIO.output(self.config.pins.box_spray_pins[index], GPIO.HIGH)
                sleep(duration / 1000.0)
            finally:
                GPIO.output(self.config.pins.box_spray_pins[index], GPIO.LOW)
