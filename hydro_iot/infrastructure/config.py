import json
import os
from dataclasses import dataclass
from typing import List

import dataconf

from hydro_iot.domain.config import IConfig, IMessageQueueConnectionInfo


@dataclass
class RabbitMqConfig(IMessageQueueConnectionInfo):
    host: str
    port: int
    user: str
    password: str


@dataclass
class Config(IConfig):
    @classmethod
    def load_config(cls, paths: List[str]) -> "Config":
        conf = dataconf.multi

        for path in paths:
            if os.path.exists(path):
                conf = conf.file(path)
        return conf.on(Config)

    def save_config(self, path: str):
        dataconf.dump(path, self, out="properties")

    def to_json(self) -> str:
        result = dataconf.dumps(self, out="json")
        result = json.loads(result)
        del result["message_queue_connection"]
        return json.dumps(result)
