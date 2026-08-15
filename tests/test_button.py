"""Tests for the Renpho button platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.renpho.button import (
    BUTTON_DESCRIPTIONS,
    RenphoButton,
    async_setup_entry,
)
from tests.conftest import MOCK_MEASUREMENT, MOCK_USER_INFO


@pytest.mark.asyncio
async def test_button_setup():
    """Test button platform setup."""
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
    assert len(added_entities) == len(BUTTON_DESCRIPTIONS)


@pytest.mark.asyncio
async def test_button_press_refresh():
    """Test pressing the manual refresh button."""
    coordinator = MagicMock()
    coordinator.data = {
        "latest_measurement": MOCK_MEASUREMENT,
        "user_info": MOCK_USER_INFO,
    }
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.config_entry.unique_id = "987654321"
    coordinator.client.user_id = "987654321"
    coordinator.async_request_refresh = AsyncMock()

    refresh_desc = next(d for d in BUTTON_DESCRIPTIONS if d.key == "refresh")
    button = RenphoButton(coordinator, refresh_desc)

    await button.async_press()
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_button_press_import_history():
    """Test pressing the import history button."""
    coordinator = MagicMock()
    coordinator.data = {
        "latest_measurement": MOCK_MEASUREMENT,
        "user_info": MOCK_USER_INFO,
    }
    coordinator.config_entry.entry_id = "test_entry"
    coordinator.config_entry.unique_id = "987654321"
    coordinator.client.user_id = "987654321"
    coordinator.async_import_history = AsyncMock()

    history_desc = next(d for d in BUTTON_DESCRIPTIONS if d.key == "import_history")
    button = RenphoButton(coordinator, history_desc)

    await button.async_press()
    coordinator.async_import_history.assert_awaited_once()
