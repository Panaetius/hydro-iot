from io import BytesIO

import numpy
import picamera
from PIL import Image

from hydro_iot.services.ports.camera_gateway import ICameraGateway


class PiCameraGateway(ICameraGateway):
    def take_ndvi_picture(self) -> numpy.ndarray:
        camera = picamera.PiCamera()
        try:
            camera.led = False
            stream = BytesIO()
            camera.capture(stream, format="png")
            stream.seek(0)
            normal_image = Image.open(stream)

            normal_red, _, _, _ = normal_image.split()
            normal_red = numpy.asarray(normal_red).astype(float)

            camera.led = True
            stream = BytesIO()
            camera.capture(stream, format="png")
            stream.seek(0)
            infrared_image = Image.open(stream)

            near_infrared, _, _, _ = infrared_image.split()
            near_infrared = numpy.asarray(near_infrared).astype(float)

            nominator = near_infrared - normal_red
            denominator = near_infrared + normal_red
            denominator[denominator == 0] = 0.01
            ndvi = nominator / denominator

            # ignore non-plant values of ndvi
            ndvi[ndvi < 0.2] = 0

            return ndvi

        finally:
            camera.led = False
