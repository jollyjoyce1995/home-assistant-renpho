"""Base entity class for the Renpho integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import RenphoDataUpdateCoordinator


class RenphoEntity(CoordinatorEntity[RenphoDataUpdateCoordinator]):
    """Base entity for Renpho."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: RenphoDataUpdateCoordinator,
        key: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._key = key
        entry_id = coordinator.config_entry.entry_id
        user_id = (
            coordinator.client.user_id or coordinator.config_entry.unique_id or entry_id
        )

        self._attr_unique_id = f"{entry_id}_{user_id}_{key}"

        user_info = coordinator.data.get("user_info", {}) if coordinator.data else {}
        user_name = (
            user_info.get("nickName")
            or user_info.get("email")
            or coordinator.config_entry.title
            or "User"
        )

        latest = (
            coordinator.data.get("latest_measurement", {}) if coordinator.data else {}
        )
        scale_name = latest.get("scaleName") or "Smart Scale"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{user_id}")},
            name=f"Renpho Scale ({user_name})",
            manufacturer="Renpho",
            model=scale_name,
            serial_number=str(user_id) if user_id else None,
        )
