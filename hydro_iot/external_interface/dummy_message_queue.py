from typing import Callable
from hydro_iot.usecase.interface.message_queue import IMessageQueueGateway
from time import sleep


class DummyMQGateway(IMessageQueueGateway):
    def __init__(self) -> None:
        self.channels = dict()

    def send_message(self, key: str, body: str) -> None:
        pass

    def declare_listener(self, queue: str, key: str, callback: Callable):
        self.channels[(queue, key)] = callback

    def start_listening(self):
        while True:
            sleep(5)
