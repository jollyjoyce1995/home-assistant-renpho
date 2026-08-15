"""Services for the Renpho integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .data import RenphoConfigEntry

SERVICE_IMPORT_HISTORY = "import_history"

SERVICE_IMPORT_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Renpho integration."""

    async def handle_import_history(call: ServiceCall) -> None:
        """Handle the import_history service call."""
        entry_id = call.data.get("entry_id")
        entries: list[RenphoConfigEntry] = hass.config_entries.async_entries(DOMAIN)

        if not entries:
            LOGGER.warning("No Renpho config entries found to import history for")
            return

        target_entries = (
            [e for e in entries if e.entry_id == entry_id] if entry_id else entries
        )

        for entry in target_entries:
            if hasattr(entry, "runtime_data") and entry.runtime_data:
                coordinator = entry.runtime_data.coordinator
                LOGGER.info("Executing import_history for entry %s", entry.title)
                await coordinator.async_import_history()

    if not hass.services.has_service(DOMAIN, SERVICE_IMPORT_HISTORY):
        hass.services.async_register(
            DOMAIN,
            SERVICE_IMPORT_HISTORY,
            handle_import_history,
            schema=SERVICE_IMPORT_HISTORY_SCHEMA,
        )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for the Renpho integration."""
    if not hass.config_entries.async_entries(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_IMPORT_HISTORY)
