"""Tests for the Renpho DataUpdateCoordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from renpho.client import RenphoAPIError

from custom_components.renpho.const import (
    CONF_EXTRA_USER_IDS,
    CONF_SCAN_INTERVAL,
)
from custom_components.renpho.coordinator import RenphoDataUpdateCoordinator


@pytest.mark.asyncio
async def test_coordinator_fetch_data_success(mock_renpho_client):
    """Test successful data fetching via coordinator."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.options = {CONF_SCAN_INTERVAL: 45, CONF_EXTRA_USER_IDS: "111, 222"}
    entry.data = {}

    coordinator = RenphoDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=mock_renpho_client,
    )

    data = coordinator._fetch_data()
    assert "latest_measurement" in data
    assert data["latest_measurement"]["weight"] == 72.5
    assert data["user_info"]["nickName"] == "Test User"
    mock_renpho_client.get_all_measurements.assert_called_once_with(
        extra_user_ids=["111", "222"]
    )


@pytest.mark.asyncio
async def test_coordinator_fetch_retry_on_token_expiry(mock_renpho_client):
    """Test coordinator retrying login on token expiry."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.options = {}
    entry.data = {}

    # Fail first call with RenphoAPIError, succeed on second call
    mock_renpho_client.get_all_measurements.side_effect = [
        RenphoAPIError("Query", 1001, "Token expired"),
        [{"weight": 70.0}],
    ]

    coordinator = RenphoDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=mock_renpho_client,
    )

    data = coordinator._fetch_data()
    assert mock_renpho_client.login.call_count >= 1
    assert data["latest_measurement"]["weight"] == 70.0


@pytest.mark.asyncio
async def test_coordinator_async_update_auth_failure(mock_renpho_client):
    """Test coordinator raising ConfigEntryAuthFailed on auth error."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.options = {}
    entry.data = {}

    coordinator = RenphoDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=mock_renpho_client,
    )

    async def mock_async_add_executor_job(func, *args):
        raise RenphoAPIError("Login", 401, "Invalid auth credentials")

    hass.async_add_executor_job = mock_async_add_executor_job

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_async_update_network_failure(mock_renpho_client):
    """Test coordinator raising UpdateFailed on network error."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.options = {}
    entry.data = {}

    coordinator = RenphoDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=mock_renpho_client,
    )

    async def mock_async_add_executor_job(func, *args):
        raise requests.exceptions.RequestException("Connection timeout")

    hass.async_add_executor_job = mock_async_add_executor_job

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_async_import_history(mock_renpho_client):
    """Test coordinator async_import_history method."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.options = {}
    entry.data = {}

    coordinator = RenphoDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=mock_renpho_client,
    )

    async def mock_async_add_executor_job(func, *args):
        return func(*args)

    hass.async_add_executor_job = mock_async_add_executor_job

    with patch(
        "custom_components.renpho.coordinator.async_import_renpho_history",
        new_callable=AsyncMock,
        return_value=10,
    ) as mock_import:
        count = await coordinator.async_import_history()
        assert count == 10
        mock_import.assert_awaited_once()
