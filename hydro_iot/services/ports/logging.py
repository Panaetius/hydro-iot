from abc import ABC


class ILogging(ABC):
    def info(self, message: str):
        raise NotImplementedError()

    def warn(self, message: str):
        raise NotImplementedError()

    def error(self, message: str):
        raise NotImplementedError()
