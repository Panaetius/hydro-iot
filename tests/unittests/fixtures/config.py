import dataconf
import pytest

from hydro_iot.infrastructure.config import Config


@pytest.fixture
def test_config():
    config = """timings {
    check_ph_ec_interval_ms = 600000
    check_temperature_interval_ms = 900000
    check_pressure_interval_ms = 10000
    spray_box_interval_ms = 360000
    spray_box_timings_ms = [
        750,
        750,
        750
    ]
    ph_ec_adjustment_downtime_ms = 1200000
}

levels {
    max_ph = 6.5
    min_ph = 5.7
    max_ec = 1800
    min_ec = 1200
    minimum_pressure_bar = 6.0
}

amounts {
    ph_increase_ml = 5.0
    ph_decrease_ml = 5.0
    flora_grow_ml = 3.0
    flora_micro_ml = 1.5
    flora_bloom_ml = 0.75
    fresh_water_ml = 1000
}

message_queue_connection {
    host = localhost
    port = 1234
}

pins {
    tds_sensor_adc = 0
    ph_sensor_adc = 1
    pressure_adc_sensor = 2
    tds_power_gpio = 5  # Pin 29
    ph_power_gpio = 6   # Pin 31
    pressure_pump= 19
    flora_grow_pump = 20
    flora_micro_pump = 21
    flora_bloom_pump = 26
    ph_up_pump = 24
    ph_down_pump = 25
    fresh_water_pump = 33
    box_spray_pins = [
        12,
        13,
        16
    ]
}
"""
    return dataconf.string(config, Config)
