from io import BytesIO
from time import sleep

import numpy
import picamera
from PIL import Image

from hydro_iot.services.ports.camera_gateway import ICameraGateway


class PiCameraGateway(ICameraGateway):
    custom_gains = (2.26, 0.74)

    def take_ndvi_picture(self) -> numpy.ndarray:
        camera = picamera.PiCamera()
        try:
            camera.awb_mode = "off"
            camera.awb_gains = self.customGains
            camera.led = False
            camera.resolution = (1920, 1080)
            sleep(1)
            stream = BytesIO()
            camera.capture(stream, format="png")
            stream.seek(0)
            normal_image = Image.open(stream)

            near_infrared, _, normal_red, _ = normal_image.split()
            normal_red = numpy.asarray(normal_red).astype(float)

            # camera.led = True
            # sleep(1)
            # stream = BytesIO()
            # camera.capture(stream, format="png")
            # stream.seek(0)
            # infrared_image = Image.open(stream)

            # near_infrared, _, _, _ = infrared_image.split()
            near_infrared = numpy.asarray(near_infrared).astype(float)

            nominator = near_infrared - normal_red
            denominator = near_infrared + normal_red
            denominator[denominator == 0] = 0.01
            ndvi = nominator / denominator

            # ignore non-plant values of ndvi
            ndvi[ndvi < 0.2] = 0
            ndvi[ndvi > 1.0] = 1.0

            return ndvi

        finally:
            camera.led = False
            camera.close()
