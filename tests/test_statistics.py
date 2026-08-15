"""Tests for Renpho historical statistics import."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from custom_components.renpho.statistics import (
    _parse_utc_timestamp,
    async_import_renpho_history,
)
from tests.conftest import MOCK_MEASUREMENT, MOCK_MEASUREMENT_2


@pytest.mark.asyncio
async def test_async_import_renpho_history_success(mock_renpho_client):
    """Test importing historical measurements successfully."""
    hass = MagicMock()
    coordinator = MagicMock()
    coordinator.config_entry.entry_id = "test_entry_id"
    coordinator.config_entry.unique_id = "987654321"
    coordinator.config_entry.title = "Renpho (Test User)"
    coordinator.client = mock_renpho_client

    measurements = [
        MOCK_MEASUREMENT_2,
        MOCK_MEASUREMENT,
    ]  # Out of order to test sorting

    with patch(
        "custom_components.renpho.statistics.async_import_statistics"
    ) as mock_import_stats:
        imported_count = await async_import_renpho_history(
            hass, coordinator, measurements
        )

        assert imported_count > 0
        assert mock_import_stats.called


@pytest.mark.asyncio
async def test_async_import_renpho_history_empty():
    """Test importing with empty measurements list."""
    hass = MagicMock()
    coordinator = MagicMock()

    imported_count = await async_import_renpho_history(hass, coordinator, [])
    assert imported_count == 0


def test_parse_utc_timestamp():
    """Test UTC timestamp parsing with second and millisecond values."""
    # Test seconds
    dt_sec = _parse_utc_timestamp(1700000000)
    assert dt_sec is not None
    assert dt_sec.year == 2023

    # Test milliseconds (> 1e12)
    dt_ms = _parse_utc_timestamp(1700000000000)
    assert dt_ms is not None
    assert dt_ms == dt_sec

    # Test invalid / zero
    assert _parse_utc_timestamp(0) is None
    assert _parse_utc_timestamp(None) is None
    assert _parse_utc_timestamp("invalid") is None
