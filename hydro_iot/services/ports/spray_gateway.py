from abc import ABC


class ISprayGateway(ABC):
    def spray_box(self, index: int, duration: int):
        raise NotImplementedError()
