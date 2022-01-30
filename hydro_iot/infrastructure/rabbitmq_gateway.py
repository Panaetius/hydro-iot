from typing import Callable

import inject
import pika

from hydro_iot.domain.config import IConfig
from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)


class RabbitMQGateway(IMessageQueuePublisher):
    config: IConfig = inject.attr(IConfig)

    def __init__(self) -> None:
        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(
                host=self.config.message_queue_connection.host,
                port=self.config.message_queue_connection.port,
            ),
            on_open_callback=self._open_callback,
        )
        self.channels = dict()

    # def send_message(self, key: str, body: str) -> None:
    #     pass

    # def declare_listener(self, queue: str, key: str, callback: Callable):
    #     self.channels[(queue, key)] = callback

    # def start_listening(self):
    #     try:
    #         self.connection.ioloop.start()
    #     except KeyboardInterrupt:
    #         self.connection.close()

    def _open_callback(self, connection):
        for (queue, key), callback in self.channels.items():
            channel = connection.channel()
            channel.queue_declare(queue)
            channel.queue_bind(queue=queue, routing_key=key)
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
