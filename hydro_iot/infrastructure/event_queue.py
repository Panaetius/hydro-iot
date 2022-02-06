import asyncio
import re
import threading
from contextlib import contextmanager
from typing import Dict, Iterator, Tuple

from hydro_iot.services.ports.event_queue import IEventHub


class AsyncioEventHub(IEventHub):
    def __init__(self):
        self.subscriptions: Dict[str, Tuple[asyncio.Queue, int]] = dict()
        self.lock = threading.Lock()

    def publish(self, key: str, message: str) -> None:
        for topic, (queue, _) in self.subscriptions.items():
            if re.search(pattern=topic, string=key):
                queue.put_nowait(message)

    @contextmanager
    def subscribe(self, topic: str) -> Iterator:
        with self.lock:
            if topic in self.subscriptions:
                queue, subscription_count = self.subscriptions["topic"]
                self.subscriptions["topic"] = (queue, subscription_count + 1)
            else:
                queue, _ = self.subscriptions.setdefault(topic, (asyncio.Queue(), 1))

        yield queue

        with self.lock:
            if topic in self.subscriptions and self.subscriptions[topic][1] == 1:
                del self.subscriptions[topic]
            else:
                queue, subscription_count = self.subscriptions["topic"]
                self.subscriptions["topic"] = (queue, subscription_count - 1)
