import inject
from hydro_iot.usecase.interface.sensors_gateway import ISensorGateway
from hydro_iot.usecase.interface.message_queue import IMessageQueueGateway


@inject.autoparams()
def read_temperature(
    sensor_gateway: ISensorGateway, message_gateway: IMessageQueueGateway
):
    temperature = sensor_gateway.get_temperature()

    message_gateway.send_message("measurement.water_temperature", temperature)

    if temperature > 26:
        message_gateway.send_message("warnings.water_temperature", temperature)
