from time import sleep

import inject
import RPi.GPIO as GPIO
from pi1wire import Pi1Wire

import hydro_iot.infrastructure.adc.ADS1263 as ADS1263
from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.config import IConfig
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature
from hydro_iot.services.ports.sensors_gateway import ISensorGateway


class RaspberrySensorGateway(ISensorGateway):
    def __init__(self) -> None:
        self.config = inject.instance(IConfig)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(config.pins.ph_power_gpio_pin, GPIO.OUT)
        GPIO.setup(config.pins.tds_power_gpio_pin, GPIO.OUT)

        self._adc = ADS1263.ADS1263()
        self._ref = 5.08
        self._neutral_ph_voltage = 1500.0
        self._acid_ph_voltage = 2032.44
        self._hpa_zero_pressure_voltage = 488

    def get_temperature(self) -> WaterTemperature:
        sensor = next(iter(Pi1Wire().find_all_sensors()), None)

        if not sensor:
            raise FileNotFoundError("Couldn't find 1-wire enable device.")

        return WaterTemperature(value=sensor.get_temperature())

    def get_conductivity(self) -> Conductivity:
        config = inject.instance(IConfig)

        GPIO.output(config.pins.tds_power_gpio_pin, GPIO.HIGH)
        sleep(0.5)
        values = []
        for _ in range(10):
            result = self._adc.ADS1263_GetChannalValue(config.pins.tds_sensor_adc_pin)

            if result >> 31 == 1:
                result = -1 * (self._ref * 2 - result * self._ref / 0x800000)
            else:
                result = result * self._ref / 0x7FFFFF

            values.append(result)
            sleep(0.05)

        GPIO.output(config.pins.tds_power_gpio_pin, GPIO.LOW)

        value = sum(values) / 10.0

        water_temperature = self.get_temperature()

        ms = (133.42 * value ** 3 - 255.86 * value ** 2 + 857.39 * value) / (
            1.0 + 0.02 * (water_temperature.value - 25.0)
        )

        return Conductivity(microsiemens_per_meter=ms)

    def get_ph(self) -> PH:
        config = inject.instance(IConfig)

        GPIO.output(config.pins.ph_power_gpio_pin, GPIO.HIGH)
        sleep(0.5)
        values = []
        for _ in range(10):
            result = self._adc.ADS1263_GetChannalValue(config.pins.ph_sensor_adc_pin)

            if result >> 31 == 1:
                result = -1 * (self._ref * 2 - result * self._ref / 0x800000)
            else:
                result = result * self._ref / 0x7FFFFF

            values.append(result)
            sleep(0.05)

        GPIO.output(config.pins.ph_power_gpio_pin, GPIO.LOW)

        value = sum(values) / 10.0

        slope = (7.0 - 4.0) / ((self._neutral_ph_voltage - 1500.0) / 3.0 - (self._acid_ph_voltage - 1500.0) / 3.0)
        intercept = 7.0 - slope * (self._neutral_ph_voltage - 1500.0) / 3.0
        ph_value = slope * (value * 1000.0 - 1500.0) / 3.0 + intercept

        return PH(value=ph_value)

    def get_pressure(self) -> Pressure:
        config = inject.instance(IConfig)

        values = []
        for _ in range(5):
            result = self._adc.ADS1263_GetChannalValue(config.pins.pressure_adc_sensor_pin)

            if result >> 31 == 1:
                result = -1 * (self._ref * 2 - result * self._ref / 0x800000)
            else:
                result = result * self._ref / 0x7FFFFF

            values.append(result)

            sleep(0.05)

        value = sum(values) / 5.0

        pressure = (value * 1000.0 - self._hpa_zero_pressure_voltage) * 9.8 / 4000.0

        return Pressure(bar=pressure)
