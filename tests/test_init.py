"""Tests for the Renpho integration initialization."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from custom_components.renpho import (
    PLATFORMS,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)


@pytest.mark.asyncio
async def test_async_setup_entry_success(mock_renpho_client):
    """Test successful entry setup."""
    hass = MagicMock()
    entry = MagicMock()
    entry.data = {
        CONF_EMAIL: "test@example.com",
        CONF_PASSWORD: "password123",
    }
    entry.options = {}
    entry.entry_id = "test_entry_id"
    entry.title = "Renpho (Test User)"
    entry.domain = "renpho"

    hass.config_entries.async_forward_entry_setups = AsyncMock()

    with (
        patch("custom_components.renpho.RenphoClient", return_value=mock_renpho_client),
        patch(
            "custom_components.renpho.coordinator.RenphoDataUpdateCoordinator.async_config_entry_first_refresh",
            new_callable=AsyncMock,
        ) as mock_first_refresh,
        patch("custom_components.renpho.async_get_loaded_integration"),
    ):
        result = await async_setup_entry(hass, entry)

    assert result is True
    mock_first_refresh.assert_awaited_once()
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, PLATFORMS
    )


@pytest.mark.asyncio
async def test_async_unload_entry():
    """Test entry unloading."""
    hass = MagicMock()
    entry = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, entry)
    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry, PLATFORMS
    )


@pytest.mark.asyncio
async def test_async_reload_entry():
    """Test entry reloading."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    hass.config_entries.async_reload = AsyncMock()

    await async_reload_entry(hass, entry)
    hass.config_entries.async_reload.assert_awaited_once_with("test_entry_id")
