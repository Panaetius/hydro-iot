from dataclasses import dataclass
import dataconf


@dataclass
class Timings:
    check_ph_ex_interval: float


@dataclass
class Config:
    timings: Timings


def load_config() -> Config:
    return dataconf.load("/etc/hydro-iot/hydro-iot.conf", Config)


def save_config(config: Config):
    dataconf.dump("/etc/hydro-iot/hydro-iot.conf", config, out="properties")
