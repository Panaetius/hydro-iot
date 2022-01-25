from dataclasses import dataclass


@dataclass
class Timings:
    check_ph_ex_interval: int
    check_temperature_interval: int


class IMessageQueueConnectionInfo:
    pass


@dataclass
class IConfig:
    timings: Timings
    message_queue_connection: IMessageQueueConnectionInfo
