"""Tests for the Renpho sensor platform."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from custom_components.renpho.sensor import (
    SENSOR_DESCRIPTIONS,
    RenphoSensor,
    async_setup_entry,
)
from tests.conftest import MOCK_MEASUREMENT, MOCK_USER_INFO


@pytest.mark.asyncio
async def test_sensor_setup(mock_renpho_client):
    """Test sensor platform setup."""
    hass = MagicMock()
    entry = MagicMock()
    coordinator = MagicMock()
    coordinator.data = {
        "latest_measurement": MOCK_MEASUREMENT,
        "user_info": MOCK_USER_INFO,
    }
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.client.user_id = "987654321"

    entry.runtime_data.coordinator = coordinator

    added_entities = []

    def mock_add_entities(entities):
        added_entities.extend(entities)

    await async_setup_entry(hass, entry, mock_add_entities)
    assert len(added_entities) == len(SENSOR_DESCRIPTIONS)


def test_sensor_values(mock_renpho_client):
    """Test sensor value parsing for all metrics."""
    coordinator = MagicMock()
    coordinator.data = {
        "latest_measurement": MOCK_MEASUREMENT,
        "user_info": MOCK_USER_INFO,
    }
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.config_entry.unique_id = "987654321"
    coordinator.config_entry.title = "Renpho (Test User)"
    coordinator.client.user_id = "987654321"

    sensors = {
        desc.key: RenphoSensor(coordinator, desc) for desc in SENSOR_DESCRIPTIONS
    }

    assert sensors["weight"].native_value == 72.5
    assert sensors["bmi"].native_value == 22.4
    assert sensors["bodyfat"].native_value == 18.5
    assert sensors["water"].native_value == 58.2
    assert sensors["muscle"].native_value == 45.1
    assert sensors["bone"].native_value == 3.2
    assert sensors["bmr"].native_value == 1650
    assert sensors["visfat"].native_value == 6
    assert sensors["subfat"].native_value == 14.2
    assert sensors["protein"].native_value == 19.1
    assert sensors["bodyage"].native_value == 28
    assert sensors["sinew"].native_value == 59.1
    assert sensors["fat_free_weight"].native_value == 59.1
    assert sensors["heart_rate"].native_value == 68
    assert sensors["cardiac_index"].native_value == 2.8

    expected_ts = datetime.fromtimestamp(1700000000, tz=UTC)
    assert sensors["last_measurement"].native_value == expected_ts

    # Test attributes on weight sensor
    attrs = sensors["weight"].extra_state_attributes
    assert attrs["scale_name"] == "ES-26M-W"
    assert attrs["local_created_at"] == "2023-11-14 22:13:20"
    assert attrs["user_id"] == "987654321"


def test_sensor_empty_measurement(mock_renpho_client):
    """Test sensor returns None when no measurement data exists."""
    coordinator = MagicMock()
    coordinator.data = {
        "latest_measurement": {},
        "user_info": MOCK_USER_INFO,
    }
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.config_entry.unique_id = "987654321"
    coordinator.client.user_id = "987654321"

    weight_desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "weight")
    sensor = RenphoSensor(coordinator, weight_desc)

    assert sensor.native_value is None
    assert sensor.extra_state_attributes == {}
