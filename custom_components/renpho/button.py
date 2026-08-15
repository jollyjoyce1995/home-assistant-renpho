"""Button platform for the Renpho integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import RenphoEntity

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RenphoDataUpdateCoordinator
    from .data import RenphoConfigEntry


@dataclass(frozen=True, kw_only=True)
class RenphoButtonEntityDescription(ButtonEntityDescription):
    """Class describing Renpho button entities."""

    press_action: Callable[[RenphoDataUpdateCoordinator], Coroutine[Any, Any, Any]]


BUTTON_DESCRIPTIONS: tuple[RenphoButtonEntityDescription, ...] = (
    RenphoButtonEntityDescription(
        key="refresh",
        translation_key="refresh",
        icon="mdi:refresh",
        press_action=lambda coordinator: coordinator.async_request_refresh(),
    ),
    RenphoButtonEntityDescription(
        key="import_history",
        translation_key="import_history",
        icon="mdi:database-import",
        entity_category=EntityCategory.CONFIG,
        press_action=lambda coordinator: coordinator.async_import_history(),
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
        RenphoButton(
            coordinator=coordinator,
            entity_description=description,
        )
        for description in BUTTON_DESCRIPTIONS
    )


class RenphoButton(RenphoEntity, ButtonEntity):
    """Representation of a Renpho button entity."""

    entity_description: RenphoButtonEntityDescription

    def __init__(
        self,
        coordinator: RenphoDataUpdateCoordinator,
        entity_description: RenphoButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    async def async_press(self) -> None:
        """Handle button press."""
        await self.entity_description.press_action(self.coordinator)
