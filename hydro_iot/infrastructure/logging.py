import logging
import sys

from cysystemd import journal

from hydro_iot.services.ports.logging import ILogging


class Logging(ILogging):
    def __init__(self) -> None:
        self._log = logging.getLogger("hydro_iot")
        self._log.addHandler(journal.JournaldLogHandler())
        self._log.addHandler(logging.StreamHandler(stream=sys.stdout))
        self._log.setLevel(logging.INFO)

    def info(self, message: str):
        self._log.info(message)

    def warn(self, message: str):
        self._log.warn(message)

    def error(self, message: str):
        self._log.error(message)
