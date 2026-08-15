"""DataUpdateCoordinator for the Renpho integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

import requests
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from renpho.client import RenphoAPIError

from .const import (
    CONF_EXTRA_USER_IDS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from renpho import RenphoClient

    from .data import RenphoConfigEntry


class RenphoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the Renpho API."""

    config_entry: RenphoConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: RenphoConfigEntry,
        client: RenphoClient,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        scan_interval_minutes = config_entry.options.get(
            CONF_SCAN_INTERVAL,
            config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=f"{DOMAIN}_{config_entry.entry_id}",
            update_interval=timedelta(minutes=scan_interval_minutes),
            config_entry=config_entry,
        )

    def _get_extra_user_ids(self) -> list[str] | None:
        """Parse extra user IDs from options or config data."""
        raw = self.config_entry.options.get(
            CONF_EXTRA_USER_IDS,
            self.config_entry.data.get(CONF_EXTRA_USER_IDS),
        )
        if not raw:
            return None
        if isinstance(raw, list):
            return [str(uid).strip() for uid in raw if str(uid).strip()]
        if isinstance(raw, str):
            return [uid.strip() for uid in raw.split(",") if uid.strip()]
        return None

    def _fetch_data(self) -> dict[str, Any]:
        """Fetch latest data from Renpho API synchronously (runs in executor)."""
        if not self.client.token:
            self.client.login()

        extra_user_ids = self._get_extra_user_ids()
        try:
            measurements = self.client.get_all_measurements(
                extra_user_ids=extra_user_ids
            )
        except RenphoAPIError as err:
            # Token might have expired, try logging in once
            LOGGER.debug(
                "Renpho API error during measurement fetch, attempting re-login: %s",
                err,
            )
            self.client.login()
            measurements = self.client.get_all_measurements(
                extra_user_ids=extra_user_ids
            )

        device_info: dict[str, Any] = {}
        try:
            device_info = self.client.get_device_info()
        except (RenphoAPIError, requests.RequestException) as err:
            LOGGER.debug("Failed to fetch device info: %s", err)

        latest = measurements[0] if measurements else {}

        return {
            "latest_measurement": latest,
            "measurements": measurements,
            "device_info": device_info,
            "user_info": self.client.user_info or {},
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via executor."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except RenphoAPIError as exception:
            if (
                exception.code in (401, 403)
                or "auth" in exception.msg.lower()
                or "login" in exception.context.lower()
            ):
                raise ConfigEntryAuthFailed(exception) from exception
            error_msg = f"Renpho API error: {exception}"
            raise UpdateFailed(error_msg) from exception
        except requests.RequestException as exception:
            error_msg = f"Error communicating with Renpho API: {exception}"
            raise UpdateFailed(error_msg) from exception
        except Exception as exception:
            LOGGER.exception("Unexpected error fetching Renpho data")
            error_msg = f"Unexpected error: {exception}"
            raise UpdateFailed(error_msg) from exception
