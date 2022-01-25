from abc import ABC


class ISensorGateway(ABC):
    def get_temperature(self) -> float:
        pass

    def get_ph(self) -> float:
        pass

    def get_ec(self) -> float:
        pass

    def get_pressure(self) -> float:
        pass
