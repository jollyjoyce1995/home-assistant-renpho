"""Tests for Renpho services."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.renpho.const import DOMAIN
from custom_components.renpho.services import (
    SERVICE_IMPORT_HISTORY,
    async_setup_services,
    async_unload_services,
)


@pytest.mark.asyncio
async def test_services_setup_and_call():
    """Test service registration and handling."""
    hass = MagicMock()
    registered_handlers = {}

    def mock_register(domain, service, handler, schema=None):
        registered_handlers[(domain, service)] = handler

    hass.services.has_service.return_value = False
    hass.services.async_register.side_effect = mock_register

    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    coordinator = MagicMock()
    coordinator.async_import_history = AsyncMock()
    entry.runtime_data.coordinator = coordinator

    hass.config_entries.async_entries.return_value = [entry]

    await async_setup_services(hass)
    assert (DOMAIN, SERVICE_IMPORT_HISTORY) in registered_handlers

    # Call handler
    handler = registered_handlers[(DOMAIN, SERVICE_IMPORT_HISTORY)]
    service_call = MagicMock()
    service_call.data = {"entry_id": "test_entry_id"}
    await handler(service_call)

    coordinator.async_import_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_services_unload():
    """Test service unregistration."""
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = []

    await async_unload_services(hass)
    hass.services.async_remove.assert_called_once_with(DOMAIN, SERVICE_IMPORT_HISTORY)
