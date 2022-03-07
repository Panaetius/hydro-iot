from time import sleep

import cmapy
import cv2
import inject
import numpy
import picamera
import picamera.array
import RPi.GPIO as GPIO

from hydro_iot.domain.config import IConfig
from hydro_iot.services.ports.camera_gateway import ICameraGateway


class PiCameraGateway(ICameraGateway):
    custom_gains = (2.26, 0.74)
    config: IConfig = inject.attr(IConfig)

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.config.pins.camera_ir_filter_pin, GPIO.OUT)

    def _stretch_contrast(self, image, in_min=None, in_max=None):
        if not in_min:
            in_min = numpy.percentile(image, 5)
        if not in_max:
            in_max = numpy.percentile(image, 95)

        out_min = 0.0
        out_max = 255.0
        out = image - in_min
        out *= (out_min - out_max) / (in_min - in_max)
        out += in_min

        return out

    def _calculate_ndvi(self, normal_image, ir_image):
        _, _, r = cv2.split(normal_image)
        _, _, ir = cv2.split(ir_image)

        bottom = r.astype(float) + ir.astype(float)
        bottom[bottom == 0] = 0.01
        ndvi = (ir.astype(float) - r) / bottom

        return ndvi

    def take_ndvi_picture(self) -> numpy.ndarray:
        camera = picamera.PiCamera()
        try:
            camera.resolution = (2592, 1944)
            GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.HIGH)
            sleep(2)

            # Get non-IR image
            original_stream = picamera.array.PiRGBArray(camera)
            camera.capture(original_stream, format="bgr", use_video_port=True)
            cv2.imwrite("/home/pi/images/original.png", original_stream.array)
            # contrasted = self._stretch_contrast(original_stream.array)
            # cv2.imwrite("/home/pi/images/contrasted.png", contrasted)

            # Get IR image
            GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.LOW)
            sleep(2)
            ir_stream = picamera.array.PiRGBArray(camera)
            camera.capture(ir_stream, format="bgr", use_video_port=True)
            cv2.imwrite("/home/pi/images/ir.png", ir_stream.array)
            GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.LOW)

            ndvi = self._calculate_ndvi(original_stream.array, ir_stream.array)
            ndvi = self._stretch_contrast(ndvi, in_min=-1, in_max=1)
            cv2.imwrite("/home/pi/images/ndvi.png", ndvi)
            cm = ndvi.astype(numpy.uint8)

            # add minimum/maximum pixel to force full color range
            cm[0, 0] = 0
            cm[0, 1] = 255
            colormapped = cv2.applyColorMap(cm, cmapy.cmap("viridis"))
            cv2.imwrite("/home/pi/images/colormapped.png", colormapped)

            return ndvi

        finally:
            GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.LOW)
            camera.close()
