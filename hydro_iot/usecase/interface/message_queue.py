from abc import ABC
from typing import Callable


class IMessageQueueGateway(ABC):
    def send_message(self, key: str, body: str) -> None:
        pass

    def declare_listener(self, queue: str, key: str, callback: Callable):
        pass

    def start_listening(self):
        pass
