from fractions import Fraction
from time import sleep

import cmapy
import cv2
import inject
import numpy
import picamera
import picamera.array
import RPi.GPIO as GPIO

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.camera_gateway import ICameraGateway
from hydro_iot.services.ports.logging import ILogging


class PiCameraGateway(ICameraGateway):
    custom_gains = (1.3, 1.0)
    config: IConfig = inject.attr(IConfig)
    logging: ILogging = inject.attr(ILogging)
    system_state: SystemState = inject.attr(SystemState)

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
        camera.resolution = (2560, 1920)
        camera.iso = 100
        try:
            sleep(2)
            camera.awb_mode = "auto"
            camera.shutter_speed = camera.exposure_speed
            camera.exposure_mode = "off"
            # Get IR image
            ir_stream = picamera.array.PiRGBArray(camera)
            camera.capture(ir_stream, format="bgr", use_video_port=True)
            # contrasted = self._stretch_contrast(original_stream.array)
            # cv2.imwrite("/home/pi/images/contrasted.png", contrasted)
            gains = camera.awb_gains
            camera.awb_mode = "off"
            camera.awb_gains = gains

            # Get non-IR image
            with self.system_state.power_output_lock:
                GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.HIGH)
                sleep(3)
                original_stream = picamera.array.PiRGBArray(camera)
                camera.capture(original_stream, format="bgr", use_video_port=True)
                GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.LOW)

            cv2.imwrite("/home/pi/images/ir.png", ir_stream.array, [cv2.IMWRITE_PNG_COMPRESSION, 6])
            cv2.imwrite("/home/pi/images/original.png", original_stream.array, [cv2.IMWRITE_PNG_COMPRESSION, 6])
            ndvi = self._calculate_ndvi(original_stream.array, ir_stream.array)
            ndvi = self._stretch_contrast(ndvi, in_min=-1, in_max=1)
            cv2.imwrite("/home/pi/images/ndvi.png", ndvi, [cv2.IMWRITE_PNG_COMPRESSION, 6])
            cm = ndvi.astype(numpy.uint8)

            # add minimum/maximum pixel to force full color range
            cm[0, 0] = 0
            cm[0, 1] = 255
            colormapped = cv2.applyColorMap(cm, cmapy.cmap("viridis"))
            cv2.imwrite("/home/pi/images/colormapped.png", colormapped, [cv2.IMWRITE_PNG_COMPRESSION, 6])

            return ndvi

        finally:
            GPIO.output(self.config.pins.camera_ir_filter_pin, GPIO.LOW)
            camera.close()
