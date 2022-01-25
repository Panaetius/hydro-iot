from hydro_iot.usecase.interface.sensors_gateway import ISensorGateway

from pi1wire import Pi1Wire


class RaspberrySensorGateway(ISensorGateway):
    def get_temperature(self) -> float:
        sensor = next(iter(Pi1Wire().find_all_sensors()), None)

        if not sensor:
            raise FileNotFoundError("Couldn't find 1-wire enable device.")

        return sensor.temperature()
