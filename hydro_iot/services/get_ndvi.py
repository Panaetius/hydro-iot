import inject
import numpy
from PIL import Image

from hydro_iot.services.ports.camera_gateway import ICameraGateway
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher


@inject.autoparams()
def calculate_ndvi(
    camera_gateway: ICameraGateway,
    logging: ILogging,
    message_gateway: IMessageQueuePublisher,
):
    logging.info("Capturing image")
    ndvi = camera_gateway.take_ndvi_picture()
    logging.info("Captured ndvi image")

    #image = Image.fromarray(numpy.uint8((ndvi + 1) / 2 * 255), "L")
    #image.save("/home/pi/images/ndvi.png")

    # message_gateway.send_temperature_status(temperature)
    # logging.info("Sent temperature status message")
