"""Sensor platform for the Renpho integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfMass,
)

from .entity import RenphoEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RenphoDataUpdateCoordinator
    from .data import RenphoConfigEntry

EPOCH_MS_THRESHOLD = 1e12
MILLISECONDS_IN_SECOND = 1000


def _parse_timestamp(ts: Any) -> datetime | None:
    """Parse Renpho timestamp to UTC datetime."""
    if ts is None or ts == 0:
        return None
    try:
        ts_int = int(ts)
        if ts_int > EPOCH_MS_THRESHOLD:
            ts_int //= MILLISECONDS_IN_SECOND
        return datetime.fromtimestamp(ts_int, tz=UTC)
    except (ValueError, TypeError, OSError):
        return None


def _get_metric_float(key: str) -> Callable[[dict[str, Any]], float | None]:
    """Retrieve a float metric value."""

    def _fn(measurement: dict[str, Any]) -> float | None:
        val = measurement.get(key)
        if val is None or val in ("", 0):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    return _fn


def _get_metric_int(key: str) -> Callable[[dict[str, Any]], int | None]:
    """Retrieve an integer metric value."""

    def _fn(measurement: dict[str, Any]) -> int | None:
        val = measurement.get(key)
        if val is None or val in ("", 0):
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None

    return _fn


@dataclass(frozen=True, kw_only=True)
class RenphoSensorEntityDescription(SensorEntityDescription):
    """Class describing Renpho sensor entities."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[RenphoSensorEntityDescription, ...] = (
    RenphoSensorEntityDescription(
        key="weight",
        translation_key="weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:scale-bathroom",
        value_fn=_get_metric_float("weight"),
    ),
    RenphoSensorEntityDescription(
        key="bmi",
        translation_key="bmi",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:human",
        value_fn=_get_metric_float("bmi"),
    ),
    RenphoSensorEntityDescription(
        key="bodyfat",
        translation_key="bodyfat",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        value_fn=_get_metric_float("bodyfat"),
    ),
    RenphoSensorEntityDescription(
        key="water",
        translation_key="water",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        value_fn=_get_metric_float("water"),
    ),
    RenphoSensorEntityDescription(
        key="muscle",
        translation_key="muscle",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:arm-flex",
        value_fn=_get_metric_float("muscle"),
    ),
    RenphoSensorEntityDescription(
        key="bone",
        translation_key="bone",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bone",
        value_fn=_get_metric_float("bone"),
    ),
    RenphoSensorEntityDescription(
        key="bmr",
        translation_key="bmr",
        native_unit_of_measurement="kcal",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
        value_fn=_get_metric_int("bmr"),
    ),
    RenphoSensorEntityDescription(
        key="visfat",
        translation_key="visfat",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heart-pulse",
        value_fn=_get_metric_int("visfat"),
    ),
    RenphoSensorEntityDescription(
        key="subfat",
        translation_key="subfat",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        value_fn=_get_metric_float("subfat"),
    ),
    RenphoSensorEntityDescription(
        key="protein",
        translation_key="protein",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:food-drumstick",
        value_fn=_get_metric_float("protein"),
    ),
    RenphoSensorEntityDescription(
        key="bodyage",
        translation_key="bodyage",
        native_unit_of_measurement="years",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-account",
        value_fn=_get_metric_int("bodyage"),
    ),
    RenphoSensorEntityDescription(
        key="sinew",
        translation_key="sinew",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:scale-bathroom",
        value_fn=_get_metric_float("sinew"),
    ),
    RenphoSensorEntityDescription(
        key="fat_free_weight",
        translation_key="fat_free_weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:scale-bathroom",
        value_fn=lambda m: (
            _get_metric_float("fatFreeWeight")(m)
            or _get_metric_float("fat_free_weight")(m)
        ),
    ),
    RenphoSensorEntityDescription(
        key="heart_rate",
        translation_key="heart_rate",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heart-pulse",
        value_fn=lambda m: (
            _get_metric_int("heartRate")(m) or _get_metric_int("heart_rate")(m)
        ),
    ),
    RenphoSensorEntityDescription(
        key="cardiac_index",
        translation_key="cardiac_index",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heart-speed",
        value_fn=lambda m: (
            _get_metric_float("cardiacIndex")(m)
            or _get_metric_float("cardiac_index")(m)
        ),
    ),
    RenphoSensorEntityDescription(
        key="last_measurement",
        translation_key="last_measurement",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
        value_fn=lambda m: _parse_timestamp(m.get("timeStamp") or m.get("time_stamp")),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: RenphoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Renpho sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        RenphoSensor(
            coordinator=coordinator,
            entity_description=description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class RenphoSensor(RenphoEntity, SensorEntity):
    """Representation of a Renpho Sensor."""

    entity_description: RenphoSensorEntityDescription

    def __init__(
        self,
        coordinator: RenphoDataUpdateCoordinator,
        entity_description: RenphoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        if not self.coordinator.data:
            return None
        latest = self.coordinator.data.get("latest_measurement")
        if not latest:
            return None
        return self.entity_description.value_fn(latest)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes for the sensor."""
        if not self.coordinator.data:
            return {}
        latest = self.coordinator.data.get("latest_measurement")
        if not latest:
            return {}

        attrs: dict[str, Any] = {}
        if self.entity_description.key in ("weight", "last_measurement"):
            if "scaleName" in latest:
                attrs["scale_name"] = latest["scaleName"]
            if "localCreatedAt" in latest:
                attrs["local_created_at"] = latest["localCreatedAt"]
            if "timeStamp" in latest or "time_stamp" in latest:
                attrs["timestamp_raw"] = latest.get("timeStamp") or latest.get(
                    "time_stamp"
                )
            if "userId" in latest:
                attrs["user_id"] = str(latest["userId"])
        return attrs
