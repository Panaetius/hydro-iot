import json
from threading import Lock, Thread
from typing import Callable

import inject
import pika

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.config import IConfig
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)


class RabbitMQGateway(IMessageQueuePublisher):
    config: IConfig = inject.attr(IConfig)
    logging: ILogging = inject.attr(ILogging)
    publish_lock: Lock = Lock()

    def __init__(self) -> None:
        self.logging.info("Setting up message queues")

        self.sensor_data_channel = None
        self.event_data_channel = None

        self.consume_connection = pika.SelectConnection(
            pika.ConnectionParameters(
                host=self.config.message_queue_connection.host,
                port=self.config.message_queue_connection.port,
                credentials=pika.PlainCredentials(
                    self.config.message_queue_connection.user, self.config.message_queue_connection.password
                ),
            ),
            on_open_callback=self._open_callback,
        )

        self.publish_connection = pika.SelectConnection(
            pika.ConnectionParameters(
                host=self.config.message_queue_connection.host,
                port=self.config.message_queue_connection.port,
                credentials=pika.PlainCredentials(
                    self.config.message_queue_connection.user, self.config.message_queue_connection.password
                ),
            ),
            on_open_callback=self.publish_connection_open_callback,
        )
        self.channels = dict()
        self.logging.info("Starting messagequeue io loop")
        Thread(target=self.publish_connection.ioloop.start).start()
        Thread(target=self.consume_connection.ioloop.start).start()

    def publish_connection_open_callback(self, connection):
        self.logging.info("Opening publish channels")
        self.sensor_data_channel = connection.channel()
        self.sensor_data_channel.queue_declare(queue="sensor_data")

        self.event_data_channel = connection.channel()
        self.event_data_channel.queue_declare(queue="event_data")

    def _open_callback(self, connection):
        for (queue, key), callback in self.channels.items():
            channel = connection.channel()
            channel.queue_declare(queue)
            channel.queue_bind(queue=queue, routing_key=key)
            # channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    def __del__(self):
        self.consume_connection.close()
        self.publish_connection.close()

    def send_temperature_status(self, temperature: WaterTemperature):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                routing_key="measurement.temperature", body=json.dumps({"temperature": temperature.value})
            )

    def send_ph_value(self, ph: PH):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(routing_key="measurement.ph", body=json.dumps({"ph": ph.value}))

    def send_fertilizer_level(self, ec: Conductivity):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                routing_key="measurement.ec", body=json.dumps({"ec": ec.microsiemens_per_meter})
            )

    def send_pressure_status(self, pressure: Pressure):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                routing_key="measurement.pressure", body=json.dumps({"pressure": pressure.bar})
            )

    def send_spray_message(self, index: int, duration: int):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.boxes.spray.{index}", body=json.dumps({"index": index, "duration": duration})
            )

    def send_ph_raised(self, amount: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.adjustment.ph.up", body=json.dumps({"amount": amount})
            )

    def send_ph_lowered(self, amount: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.adjustment.ph.down", body=json.dumps({"amount": amount})
            )

    def send_ec_lowered(self, amount: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.adjustment.ec.down", body=json.dumps({"amount": amount})
            )

    def send_ec_increased(self, amount_grow: float, amount_micro: float, amount_bloom: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.adjustment.ec.up",
                body=json.dumps(
                    {"amount_grow": amount_grow, "amount_micro": amount_micro, "amount_bloom": amount_bloom}
                ),
            )

    def send_pressure_raised(self, pressure: Pressure):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.adjustment.pressure.up", body=json.dumps({"bar": pressure.bar})
            )

    def send_unexpected_pressure_drop(self, pressure_drop: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                routing_key=f"event.exception.pressure.drop", body=json.dumps({"drop": pressure_drop})
            )

    def send_could_not_raise_pressure(self):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(routing_key=f"event.exception.pressure.not_increasing", body="")
