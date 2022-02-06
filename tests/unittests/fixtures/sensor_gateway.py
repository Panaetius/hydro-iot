import pytest

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.domain.pressure import Pressure
from hydro_iot.domain.temperature import WaterTemperature


@pytest.fixture
def mock_sensor_gateway(mocker):
    def _mock_sensor_gateway(
        temperature: float = 20.0, ph: float = 6.0, conductivity: float = 1500, pressure: float = 7.0
    ):
        sensor_gateway = mocker.MagicMock()
        sensor_gateway.get_ph.return_value = PH(value=ph)
        sensor_gateway.get_conductivity.return_value = Conductivity(conductivity)
        sensor_gateway.get_temperature.return_value = Conductivity(temperature)
        sensor_gateway.get_pressure.return_value = Conductivity(pressure)

        return sensor_gateway

    return _mock_sensor_gateway
