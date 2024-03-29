import json

import inject

from hydro_iot.controller.interface.scheduler import IScheduler
from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.config import IConfig
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.system_state import SystemState
from hydro_iot.domain.timing import SprayTiming
from hydro_iot.services.empty_tank import empty_tank as empty_tank_usecase
from hydro_iot.services.get_ndvi import calculate_ndvi
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.message_queue import IMessageQueueSubscriber
from hydro_iot.services.spray_boxes import spray_boxes


class CommandEventSubscriber(IMessageQueueSubscriber):
    config = inject.attr(IConfig)
    scheduler = inject.attr(IScheduler)
    system_state = inject.attr(SystemState)
    event_hub = inject.attr(IEventHub)

    def set_minimum_ph_level(self, ph: PH):
        self.config.levels.min_ph = ph.value
        self.config.save_config(inject.instance("config_path"))

    def set_maximum_ph_level(self, ph: PH):
        self.config.levels.max_ph = ph.value
        self.config.save_config(inject.instance("config_path"))

    def set_minimum_conductivity_level(self, conductivity: Conductivity):
        self.config.levels.min_ec = conductivity.microsiemens_per_meter
        self.config.save_config(inject.instance("config_path"))

    def set_maximum_conductivity_level(self, conductivity: Conductivity):
        self.config.levels.max_ec = conductivity.microsiemens_per_meter
        self.config.save_config(inject.instance("config_path"))

    def set_minimum_pump_pressure(self, pressure: Pressure):
        self.config.levels.minimum_pressure_bar = pressure.bar
        self.config.save_config(inject.instance("config_path"))

    def set_target_pump_pressure(self, pressure: Pressure):
        self.config.levels.maximum_pressure_bar = pressure.bar
        self.config.save_config(inject.instance("config_path"))

    def set_spray_timing(self, timing: SprayTiming):
        self.config.timings.spray_box_interval_ms = int(timing.interval_ms)
        self.scheduler.change_job_schedule("spray_boxes", timing.interval_ms / 1000.0)

        self.config.timings.spray_box_timings_ms = [int(timing.duration_ms)] * 3  # TODO: Change to timing per Box
        self.config.save_config(inject.instance("config_path"))

    def set_box_status(self, box1_status: bool, box2_status: bool, box3_status: bool):
        self.config.levels.boxes_enabled = [box1_status, box2_status, box3_status]
        self.config.save_config(inject.instance("config_path"))

    def spray_boxes(self):
        spray_boxes()

    def increase_ph(self):
        self.event_hub.publish(key="ph.up", message="increase_ph")

    def decrease_ph(self):
        self.event_hub.publish(key="ph.down", message="decrease_ph")

    def increase_ec(self):
        self.event_hub.publish(key="ec.up", message="increase_ec")

    def decrease_ec(self):
        self.event_hub.publish(key="ec.down", message="decrease_ec")

    def empty_tank(self):
        self.event_hub.publish(key="pressure.empty", message="empty_tank")

    def increase_pressure(self):
        self.event_hub.publish(key="pressure.increase", message="increase_pressure")

    def pause_system(self):
        self.system_state.paused = True

    def unpause_system(self):
        self.system_state.paused = False

    def get_system_state(self):
        return self.system_state.to_json()

    def get_config(self):
        return self.config.to_json()

    def take_ndvi_image(self):
        calculate_ndvi()
