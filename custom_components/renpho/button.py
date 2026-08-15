"""Button platform for the Renpho integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .entity import RenphoEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RenphoDataUpdateCoordinator
    from .data import RenphoConfigEntry

BUTTON_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="refresh",
        translation_key="refresh",
        icon="mdi:refresh",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: RenphoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Renpho button platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        RenphoRefreshButton(
            coordinator=coordinator,
            entity_description=description,
        )
        for description in BUTTON_DESCRIPTIONS
    )


class RenphoRefreshButton(RenphoEntity, ButtonEntity):
    """Representation of a Renpho manual refresh button."""

    entity_description: ButtonEntityDescription

    def __init__(
        self,
        coordinator: RenphoDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    async def async_press(self) -> None:
        """Handle button press to refresh measurements."""
        await self.coordinator.async_request_refresh()
