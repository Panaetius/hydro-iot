from time import sleep
from typing import Callable

from hydro_iot.services.ports.message_queue import (
    IMessageQueuePublisher,
    IMessageQueueSubscriber,
)


class DummyMQGateway(IMessageQueuePublisher):
    def __init__(self) -> None:
        self.channels = dict()

    def send_message(self, key: str, body: str) -> None:
        pass

    def declare_listener(self, queue: str, key: str, callback: Callable):
        self.channels[(queue, key)] = callback

    def start_listening(self):
        return
