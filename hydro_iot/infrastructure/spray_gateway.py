from time import sleep

import inject
import RPi.GPIO as GPIO

from hydro_iot.domain.config import IConfig
from hydro_iot.services.ports.spray_gateway import ISprayGateway


class SprayGateway(ISprayGateway):
    config = inject.attr(IConfig)

    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)

        for box_pin in self.config.pins.box_spray_pins:
            GPIO.setup(box_pin, GPIO.OUT)

    def spray_box(self, index: int, duration: int):
        GPIO.output(self.config.pins.box_spray_pins[index], GPIO.HIGH)
        sleep(duration / 1000.0)
        GPIO.output(self.config.pins.box_spray_pins[index], GPIO.LOW)
