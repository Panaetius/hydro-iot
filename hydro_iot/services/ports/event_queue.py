from abc import ABC
from contextlib import contextmanager


class IEventHub(ABC):
    def publish(self, key: str, message: str):
        raise NotImplementedError()

    @contextmanager
    def subscribe(self, topic: str):
        raise NotImplementedError()
