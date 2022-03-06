from abc import ABC

import numpy


class ICameraGateway(ABC):
    def take_ndvi_picture(self) -> numpy.ndarray:
        raise NotImplementedError()
