"""Custom types for the Renpho integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from renpho import RenphoClient

    from .coordinator import RenphoDataUpdateCoordinator

type RenphoConfigEntry = ConfigEntry[RenphoData]


@dataclass
class RenphoData:
    """Data for the Renpho integration."""

    client: RenphoClient
    coordinator: RenphoDataUpdateCoordinator
    integration: Integration
