from time import sleep

import inject
import RPi.GPIO as GPIO

from hydro_iot.domain.config import IConfig
from hydro_iot.services.ports.spray_gateway import ISprayGateway


class SprayGateway(ISprayGateway):
    def __init__(self) -> None:
        self._config = inject.instance(IConfig)
        GPIO.setmode(GPIO.BOARD)

        for box_pin in self._config.pins.box_spray_pins:
            GPIO.setup(box_pin, GPIO.OUT)

    def spray_box(self, index: int, duration: int):
        GPIO.output(self._config.pins.box_spray_pins[index], GPIO.HIGH)
        sleep(duration / 1000.0)
        GPIO.output(self._config.pins.box_spray_pins[index], GPIO.LOW)
