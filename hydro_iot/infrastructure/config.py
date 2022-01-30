from dataclasses import dataclass

import dataconf

from hydro_iot.domain.config import IConfig, IMessageQueueConnectionInfo


@dataclass
class RabbitMqConfig(IMessageQueueConnectionInfo):
    host: str
    port: int


@dataclass
class Config(IConfig):
    @classmethod
    def load_config(cls, path: str) -> "Config":
        return dataconf.load(path, Config)

    def save_config(self, path: str):
        dataconf.dump(path, self, out="properties")
