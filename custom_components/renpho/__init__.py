"""Custom integration for Renpho smart scales in Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.loader import async_get_loaded_integration

from renpho import RenphoClient

from .const import LOGGER
from .coordinator import RenphoDataUpdateCoordinator
from .data import RenphoData
from .services import async_setup_services, async_unload_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import RenphoConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RenphoConfigEntry,
) -> bool:
    """Set up Renpho from a config entry."""
    client = RenphoClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    coordinator = RenphoDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=client,
    )

    entry.runtime_data = RenphoData(
        client=client,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    # Perform initial data refresh
    await coordinator.async_config_entry_first_refresh()

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass)

    # Queue background initial history import
    hass.async_create_task(coordinator.async_import_history())

    # Register reload listener when options are updated
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    LOGGER.debug("Renpho integration initialized for entry: %s", entry.title)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: RenphoConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await async_unload_services(hass)
    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: RenphoConfigEntry,
) -> None:
    """Reload config entry after options change."""
    await hass.config_entries.async_reload(entry.entry_id)
