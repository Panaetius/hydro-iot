from itertools import tee
from time import sleep

import inject
import RPi.GPIO as GPIO

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.pump_gateway import IPumpGateway
from hydro_iot.services.ports.sensors_gateway import ISensorGateway

MAX_INTERVAL_WITHOUT_PRESSURE_INCREASE = 5
SLEEP_BETWEEN_MEASUREMENTS = 0.2
ML_TO_S = 0.9325


class PumpGateway(IPumpGateway):
    sensor_gateway: ISensorGateway = inject.attr(ISensorGateway)
    config: IConfig = inject.attr(IConfig)

    def __init__(self) -> None:
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.config.pins.pressure_pump, GPIO.OUT)
        GPIO.setup(self.config.pins.flora_grow_pump, GPIO.OUT)
        GPIO.setup(self.config.pins.flora_micro_pump, GPIO.OUT)
        GPIO.setup(self.config.pins.flora_bloom_pump, GPIO.OUT)
        GPIO.setup(self.config.pins.ph_up_pump, GPIO.OUT)
        GPIO.setup(self.config.pins.ph_down_pump, GPIO.OUT)

    def increase_system_pressure(self, target_pressure: Pressure):
        current_pressure = self.sensor_gateway.get_pressure().bar
        max_measured_pressure = current_pressure
        last_max_measured = 0

        GPIO.output(self.config.pins.pressure_pump, GPIO.HIGH)

        try:
            while current_pressure < target_pressure.bar:
                # Moving exponential average to smooth measurement
                current_pressure = (current_pressure + self.sensor_gateway.get_pressure().bar) / 2

                if current_pressure > max_measured_pressure:
                    last_max_measured = 0
                    max_measured_pressure = current_pressure
                else:
                    last_max_measured += 1

                if last_max_measured > MAX_INTERVAL_WITHOUT_PRESSURE_INCREASE:
                    break

                sleep(SLEEP_BETWEEN_MEASUREMENTS)

        finally:
            GPIO.output(self.config.pins.pressure_pump, GPIO.LOW)

    def increase_fertilizer(self, flora_grow_ml: float, flora_micro_ml: float, flora_bloom_ml: float):
        flora_grow_time = flora_grow_ml * ML_TO_S
        flora_micro_time = flora_micro_ml * ML_TO_S
        flora_bloom_time = flora_bloom_ml * ML_TO_S

        # Sort pump times from smallest to largest and turn absolute times to relative times
        pumps = [
            (flora_grow_time, self.config.pins.flora_grow_pump),
            (flora_micro_time, self.config.pins.flora_micro_pump),
            (flora_bloom_time, self.config.pins.flora_bloom_pump),
        ]
        pumps = sorted(pumps, key=lambda x: x[0])
        pumps_before, pumps_after = tee(pumps)
        next(pumps_after, None)
        pumps = [pumps[0]] + [(after[0] - before[0], after[1]) for before, after in zip(pumps_before, pumps_after)]

        try:
            GPIO.output(self.config.pins.flora_grow_pump, GPIO.HIGH)
            GPIO.output(self.config.pins.flora_micro_pump, GPIO.HIGH)
            GPIO.output(self.config.pins.flora_bloom_pump, GPIO.HIGH)

            for duration, pin in pumps:
                sleep(duration)
                GPIO.output(pin, GPIO.LOW)

        finally:
            GPIO.output(self.config.pins.flora_grow_pump, GPIO.LOW)
            GPIO.output(self.config.pins.flora_micro_pump, GPIO.LOW)
            GPIO.output(self.config.pins.flora_bloom_pump, GPIO.LOW)

    def lower_fertilizer(self):
        pass  # Not implemented yet

    def raise_ph(self, amount_ml: float):
        duration = amount_ml * ML_TO_S

        try:
            GPIO.output(self.config.pins.ph_up_pump, GPIO.HIGH)
            sleep(duration)
        finally:
            GPIO.output(self.config.pins.ph_up_pump, GPIO.LOW)

    def lower_ph(self, amount_ml: float):
        duration = amount_ml * ML_TO_S

        try:
            GPIO.output(self.config.pins.ph_down_pump, GPIO.HIGH)
            sleep(duration)
        finally:
            GPIO.output(self.config.pins.ph_down_pump, GPIO.LOW)
