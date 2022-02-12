import asyncio
import re
import threading
from contextlib import contextmanager
from typing import Dict, Iterator, Tuple

import inject

from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging


class AsyncioEventHub(IEventHub):
    logging = inject.attr(ILogging)

    def __init__(self):
        self.subscriptions: Dict[str, Tuple[asyncio.Queue, int]] = dict()
        self.lock = threading.Lock()

    def publish(self, key: str, message: str) -> None:
        for topic, (queue, _) in self.subscriptions.items():
            if re.search(pattern=topic, string=key):
                self.logging.info(f"Put message into queue {topic} ({id(self)})")
                queue.put_nowait(message)

    @contextmanager
    def subscribe(self, topic: str) -> Iterator:
        with self.lock:
            if topic in self.subscriptions:
                queue, subscription_count = self.subscriptions["topic"]
                self.subscriptions["topic"] = (queue, subscription_count + 1)
            else:
                self.logging.info(f"created queue {topic} ({id(self)})")
                queue, _ = self.subscriptions.setdefault(topic, (asyncio.Queue(), 1))

        yield queue

        with self.lock:
            if topic in self.subscriptions and self.subscriptions[topic][1] == 1:
                del self.subscriptions[topic]
                self.logging.info(f"removed queue {topic}")
            else:
                queue, subscription_count = self.subscriptions["topic"]
                self.subscriptions["topic"] = (queue, subscription_count - 1)
