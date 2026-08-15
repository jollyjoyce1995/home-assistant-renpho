"""Tests for the Renpho config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests
from renpho.client import RenphoAPIError

from custom_components.renpho.config_flow import (
    RenphoFlowHandler,
    RenphoOptionsFlowHandler,
)
from custom_components.renpho.const import (
    CONF_EXTRA_USER_IDS,
    CONF_SCAN_INTERVAL,
)


@pytest.mark.asyncio
async def test_flow_user_init():
    """Test user step form displays correctly."""
    flow = RenphoFlowHandler()
    flow.hass = MagicMock()

    result = await flow.async_step_user()
    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_flow_user_success(mock_renpho_client):
    """Test successful user step configuration."""
    flow = RenphoFlowHandler()
    flow.hass = MagicMock()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()

    user_input = {
        "email": "test@example.com",
        "password": "password123",
        "scan_interval": 60,
    }

    async def mock_async_add_executor_job(func, *args):
        return func(*args)

    flow.hass.async_add_executor_job = mock_async_add_executor_job

    with patch(
        "custom_components.renpho.config_flow.RenphoClient",
        return_value=mock_renpho_client,
    ):
        result = await flow.async_step_user(user_input)

    assert result["type"] == "create_entry"
    assert result["title"] == "Renpho (Test User)"
    assert result["data"] == user_input
    flow.async_set_unique_id.assert_called_once_with("987654321")


@pytest.mark.asyncio
async def test_flow_user_invalid_auth():
    """Test user step with invalid authentication."""
    flow = RenphoFlowHandler()
    flow.hass = MagicMock()

    user_input = {
        "email": "test@example.com",
        "password": "wrong_password",
        "scan_interval": 60,
    }

    async def mock_async_add_executor_job(func, *args):
        raise RenphoAPIError("Login", 401, "Invalid password")

    flow.hass.async_add_executor_job = mock_async_add_executor_job

    result = await flow.async_step_user(user_input)
    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}


@pytest.mark.asyncio
async def test_flow_user_cannot_connect():
    """Test user step with network connection error."""
    flow = RenphoFlowHandler()
    flow.hass = MagicMock()

    user_input = {
        "email": "test@example.com",
        "password": "password123",
        "scan_interval": 60,
    }

    async def mock_async_add_executor_job(func, *args):
        raise requests.exceptions.ConnectionError("Failed to connect")

    flow.hass.async_add_executor_job = mock_async_add_executor_job

    result = await flow.async_step_user(user_input)
    assert result["type"] == "form"
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_options_flow():
    """Test options flow initialization and update."""
    config_entry = MagicMock()
    config_entry.options = {CONF_SCAN_INTERVAL: 60, CONF_EXTRA_USER_IDS: ""}
    config_entry.data = {CONF_SCAN_INTERVAL: 60}

    handler = RenphoOptionsFlowHandler(config_entry)

    # Test initial form view
    result = await handler.async_step_init()
    assert result["type"] == "form"
    assert result["step_id"] == "init"

    # Test options update
    new_options = {
        CONF_SCAN_INTERVAL: 30,
        CONF_EXTRA_USER_IDS: "123456, 789012",
    }
    result = await handler.async_step_init(new_options)
    assert result["type"] == "create_entry"
    assert result["data"] == new_options
