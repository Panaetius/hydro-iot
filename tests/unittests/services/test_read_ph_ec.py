from time import monotonic

from hydro_iot.domain.conductivity import Conductivity
from hydro_iot.domain.ph import PH
from hydro_iot.services.read_ph_ec import read_ph_conductivity


def test_normal_ph_ec(mocker, mock_sensor_gateway, test_config):
    """Test everything works with ph and ec within bounds."""

    message_gateway = mocker.MagicMock()
    event_hub = mocker.MagicMock()
    system_state = mocker.MagicMock(last_fertilizer_adjustment=monotonic(), last_ph_adjustment=monotonic())
    logging = mocker.MagicMock()

    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=6.0, conductivity=1500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )

    message_gateway.send_ph_value.assert_called_once()
    message_gateway.send_fertilizer_level.assert_called_once()
    event_hub.publish.assert_not_called()


def test_high_ph(mocker, mock_sensor_gateway, test_config):
    """Test everything works with high ph."""

    message_gateway = mocker.MagicMock()
    event_hub = mocker.MagicMock()
    system_state = mocker.MagicMock(last_fertilizer_adjustment=monotonic(), last_ph_adjustment=monotonic())
    logging = mocker.MagicMock()

    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=7.0, conductivity=1500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )

    message_gateway.send_ph_value.assert_called_once()
    message_gateway.send_fertilizer_level.assert_called_once()
    event_hub.publish.assert_not_called()

    system_state = mocker.MagicMock(
        last_ph_adjustment=monotonic() - test_config.timings.ph_adjustment_downtime_ms - 1000,
        last_fertilizer_adjustment=monotonic() - test_config.timings.ec_adjustment_downtime_ms - 1000,
    )
    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=7.0, conductivity=1500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )
    event_hub.publish.assert_called_once_with(key="ph.down", message="decrease_ph")


def test_low_ph(mocker, mock_sensor_gateway, test_config):
    """Test everything works with low ph."""

    message_gateway = mocker.MagicMock()
    event_hub = mocker.MagicMock()
    system_state = mocker.MagicMock(last_ph_adjustment=monotonic(), last_fertilizer_adjustment=monotonic())
    logging = mocker.MagicMock()

    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=7.0, conductivity=1500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )

    message_gateway.send_ph_value.assert_called_once()
    message_gateway.send_fertilizer_level.assert_called_once()
    event_hub.publish.assert_not_called()

    system_state = mocker.MagicMock(
        last_ph_adjustment=monotonic() - test_config.timings.ph_adjustment_downtime_ms - 1000,
        last_fertilizer_adjustment=monotonic() - test_config.timings.ec_adjustment_downtime_ms - 1000,
    )
    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=5.0, conductivity=1500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )
    event_hub.publish.assert_called_once_with(key="ph.up", message="increase_ph")


def test_low_ec(mocker, mock_sensor_gateway, test_config):
    """Test everything works with low ph."""

    message_gateway = mocker.MagicMock()
    event_hub = mocker.MagicMock()
    system_state = mocker.MagicMock(last_fertilizer_adjustment=monotonic(), last_ph_adjustment=monotonic())
    logging = mocker.MagicMock()

    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=6.0, conductivity=500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )

    message_gateway.send_ph_value.assert_called_once()
    message_gateway.send_fertilizer_level.assert_called_once()
    event_hub.publish.assert_not_called()

    system_state = mocker.MagicMock(
        last_ph_adjustment=monotonic() - test_config.timings.ph_adjustment_downtime_ms - 1000,
        last_fertilizer_adjustment=monotonic() - test_config.timings.ec_adjustment_downtime_ms - 1000,
    )
    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=6.0, conductivity=500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )
    event_hub.publish.assert_called_once_with(key="ec.up", message="increase_ec")


def test_high_ec(mocker, mock_sensor_gateway, test_config):
    """Test everything works with low ph."""

    message_gateway = mocker.MagicMock()
    event_hub = mocker.MagicMock()
    system_state = mocker.MagicMock(last_fertilizer_adjustment=monotonic(), last_ph_adjustment=monotonic())
    logging = mocker.MagicMock()

    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=6.0, conductivity=2500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )

    message_gateway.send_ph_value.assert_called_once()
    message_gateway.send_fertilizer_level.assert_called_once()
    event_hub.publish.assert_not_called()

    system_state = mocker.MagicMock(
        last_ph_adjustment=monotonic() - test_config.timings.ph_adjustment_downtime_ms - 1000,
        last_fertilizer_adjustment=monotonic() - test_config.timings.ec_adjustment_downtime_ms - 1000,
    )
    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=6.0, conductivity=2500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )
    event_hub.publish.assert_called_once_with(key="ec.down", message="decrease_ec")


def test_low_ec_and_ph(mocker, mock_sensor_gateway, test_config):
    """Test everything works with low ph."""

    message_gateway = mocker.MagicMock()
    event_hub = mocker.MagicMock()
    system_state = mocker.MagicMock(last_fertilizer_adjustment=monotonic(), last_ph_adjustment=monotonic())
    logging = mocker.MagicMock()

    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=5.0, conductivity=500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )

    message_gateway.send_ph_value.assert_called_once()
    message_gateway.send_fertilizer_level.assert_called_once()
    event_hub.publish.assert_not_called()

    system_state = mocker.MagicMock(
        last_ph_adjustment=monotonic() - test_config.timings.ph_adjustment_downtime_ms - 1000,
        last_fertilizer_adjustment=monotonic() - test_config.timings.ec_adjustment_downtime_ms - 1000,
    )
    read_ph_conductivity(
        sensor_gateway=mock_sensor_gateway(ph=5.0, conductivity=500),
        message_gateway=message_gateway,
        event_hub=event_hub,
        config=test_config,
        system_state=system_state,
        logging=logging,
    )
    event_hub.publish.assert_called_once_with(key="ec.up", message="increase_ec")
