import json
from datetime import datetime
from threading import Lock, Thread
from typing import Callable

import inject
import pika
import pika.channel

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.config import IConfig
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature
from hydro_iot.domain.timing import SprayTiming
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)


class RabbitMQGateway(IMessageQueuePublisher):
    config: IConfig = inject.attr(IConfig)
    logging: ILogging = inject.attr(ILogging)
    subscriber: IMessageQueueSubscriber = inject.attr(IMessageQueueSubscriber)
    publish_lock: Lock = Lock()

    def __init__(self) -> None:
        self.logging.info("Setting up message queues")

        self.sensor_data_channel = None
        self.event_data_channel = None

        self.consume_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config.message_queue_connection.host,
                port=self.config.message_queue_connection.port,
                credentials=pika.PlainCredentials(
                    self.config.message_queue_connection.user, self.config.message_queue_connection.password
                ),
            )
        )

        self.publish_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config.message_queue_connection.host,
                port=self.config.message_queue_connection.port,
                credentials=pika.PlainCredentials(
                    self.config.message_queue_connection.user, self.config.message_queue_connection.password
                ),
            )
        )
        self.channels = dict()
        self.logging.info("Starting messagequeue io loop")
        self.sensor_data_channel = self.publish_connection.channel()
        self.event_data_channel = self.publish_connection.channel()
        self.rpc_data_channel = self.consume_connection.channel()

        self.sensor_data_channel.queue_declare(queue="sensor_data")
        self.event_data_channel.queue_declare(queue="event_data")
        self.rpc_data_channel.queue_declare(queue="rpc_data")
        self.rpc_data_channel.basic_qos(prefetch_count=1)
        self.rpc_data_channel.basic_consume(queue="rpc_data", on_message_callback=self.handle_rpc)
        Thread(target=self.rpc_data_channel.start_consuming).start()

    def __del__(self):
        self.consume_connection.close()
        self.publish_connection.close()

    @property
    def current_timestamp(self):
        return int(datetime.timestamp(datetime.utcnow()))

    def send_temperature_status(self, temperature: WaterTemperature):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key="measurement.temperature",
                body=json.dumps({"temperature": temperature.value}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_ph_value(self, ph: PH):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key="measurement.ph",
                body=json.dumps({"ph": ph.value}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_fertilizer_level(self, ec: Conductivity):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key="measurement.ec",
                body=json.dumps({"ec": ec.microsiemens_per_meter}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_pressure_status(self, pressure: Pressure):
        if not self.sensor_data_channel:
            return

        with self.publish_lock:
            self.sensor_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key="measurement.pressure",
                body=json.dumps({"pressure": pressure.bar}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_spray_message(self, index: int, duration: int):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.boxes.spray.{index}",
                body=json.dumps({"index": index, "duration": duration}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_ph_raised(self, amount: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.adjustment.ph.up",
                body=json.dumps({"amount": amount}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_ph_lowered(self, amount: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.adjustment.ph.down",
                body=json.dumps({"amount": amount}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_ec_lowered(self, amount: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.adjustment.ec.down",
                body=json.dumps({"amount": amount}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_ec_increased(self, amount_grow: float, amount_micro: float, amount_bloom: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.adjustment.ec.up",
                body=json.dumps(
                    {"amount_grow": amount_grow, "amount_micro": amount_micro, "amount_bloom": amount_bloom}
                ),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_pressure_raised(self, pressure: Pressure):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.adjustment.pressure.up",
                body=json.dumps({"bar": pressure.bar}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_unexpected_pressure_drop(self, pressure_drop: float):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.exception.pressure.drop",
                body=json.dumps({"drop": pressure_drop}),
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def send_could_not_raise_pressure(self):
        if not self.event_data_channel:
            return

        with self.publish_lock:
            self.event_data_channel.basic_publish(
                exchange="sensor_data_exchange",
                routing_key=f"event.exception.pressure.not_increasing",
                body="",
                properties=pika.BasicProperties(timestamp=self.current_timestamp),
                mandatory=True,
            )

    def handle_rpc(self, channel: pika.channel.Channel, method, props, body):
        routing_key = method.routing_key
        self.logging.info(f"Got RPC command: {routing_key}")
        body = json.loads(body)

        try:
            if routing_key == "rpc.get_config":
                response = self.subscriber.get_config()
            elif routing_key == "rpc.set_minimum_ph":
                self.subscriber.set_minimum_ph_level(PH(value=body["ph"]))
                response = ""
            elif routing_key == "rpc.set_maximum_ph":
                self.subscriber.set_maximum_ph_level(PH(value=body["ph"]))
                response = ""
            elif routing_key == "rpc.set_minimum_ec":
                self.subscriber.set_minimum_conductivity_level(Conductivity(microsiemens_per_meter=body["ec"]))
                response = ""
            elif routing_key == "rpc.set_maximum_ec":
                self.subscriber.set_maximum_conductivity_level(Conductivity(microsiemens_per_meter=body["ec"]))
                response = ""
            elif routing_key == "rpc.set_minimum_pump_pressure":
                self.subscriber.set_minimum_pump_pressure(Pressure(bar=body["pressure"]))
                response = ""
            elif routing_key == "rpc.set_maximum_pump_pressure":
                self.subscriber.set_target_pump_pressure(Pressure(bar=body["pressure"]))
                response = ""
            elif routing_key == "rpc.set_spray_timing":
                self.subscriber.set_spray_timing(
                    SprayTiming(duration_ms=body["duration"], interval_ms=body["interval"])
                )
                response = ""
            elif routing_key == "rpc.pause_system":
                self.subscriber.pause_system()
                response = ""
            elif routing_key == "rpc.unpause_system":
                self.subscriber.unpause_system()
                response = ""
            elif routing_key == "rpc.get_system_state":
                response = self.subscriber.pause_system()
            elif routing_key == "rpc.spray_boxes":
                response = self.subscriber.spray_boxes()
            elif routing_key == "rpc.ph_up":
                response = self.subscriber.increase_ph()
            elif routing_key == "rpc.ph_down":
                response = self.subscriber.decrease_ph()
            elif routing_key == "rpc.ec_up":
                response = self.subscriber.increase_ec()
            elif routing_key == "rpc.ec_down":
                response = self.subscriber.decrease_ec()
            elif routing_key == "rpc.empty_tank":
                response = self.subscriber.empty_tank()
            elif routing_key == "rpc.pressure_up":
                response = self.subscriber.increase_pressure()
            else:
                self.logging.error(f"Got unknown RPC request: {routing_key}, {body}")
                channel.basic_nack(delivery_tag=method.delivery_tag)
                return

            self.logging.info(f"Sending reply: {response}")
            channel.basic_publish(
                exchange="",
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id=props.correlation_id),
                body=response,
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logging.error(f"RPC Error: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag)
