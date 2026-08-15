"""Historical statistics import for the Renpho integration."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.recorder.models import (
    StatisticData,
    StatisticMetaData,
)
from homeassistant.components.recorder.statistics import (
    async_import_statistics,
)
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, LOGGER
from .sensor import SENSOR_DESCRIPTIONS

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import RenphoDataUpdateCoordinator

EPOCH_MS_THRESHOLD = 1e12
MILLISECONDS_IN_SECOND = 1000


def _parse_utc_timestamp(ts: Any) -> datetime | None:
    """Parse Renpho timestamp to timezone-aware UTC datetime."""
    if ts is None or ts == 0:
        return None
    try:
        ts_int = int(ts)
        if ts_int > EPOCH_MS_THRESHOLD:
            ts_int //= MILLISECONDS_IN_SECOND
        return datetime.fromtimestamp(ts_int, tz=UTC)
    except (ValueError, TypeError, OSError):
        return None


async def async_import_renpho_history(
    hass: HomeAssistant,
    coordinator: RenphoDataUpdateCoordinator,
    measurements: list[dict[str, Any]],
) -> int:
    """Import Renpho measurements into Long-Term Statistics."""
    if not measurements:
        LOGGER.debug("No historical measurements found to import.")
        return 0

    ent_reg = er.async_get(hass)
    entry_id = coordinator.config_entry.entry_id
    user_id = (
        coordinator.client.user_id or coordinator.config_entry.unique_id or entry_id
    )

    # Sort measurements chronologically (oldest to newest)
    sorted_measurements = sorted(
        measurements,
        key=lambda m: int(m.get("timeStamp") or m.get("time_stamp") or 0),
    )

    total_imported = 0

    for description in SENSOR_DESCRIPTIONS:
        # Only import statistics for numerical metrics
        if description.key == "last_measurement":
            continue

        unique_id = f"{entry_id}_{user_id}_{description.key}"
        entity_id = ent_reg.async_get_entity_id("sensor", DOMAIN, unique_id)

        if entity_id:
            stat_id = entity_id
            stat_source = "recorder"
        else:
            stat_id = f"{DOMAIN}:{user_id}_{description.key}"
            stat_source = DOMAIN

        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=f"Renpho {description.key.replace('_', ' ').title()}",
            source=stat_source,
            statistic_id=stat_id,
            unit_of_measurement=description.native_unit_of_measurement,
        )

        seen_timestamps: set[datetime] = set()
        stat_data_list: list[StatisticData] = []

        for m in sorted_measurements:
            raw_ts = m.get("timeStamp") or m.get("time_stamp")
            start_time = _parse_utc_timestamp(raw_ts)
            if not start_time or start_time in seen_timestamps:
                continue

            value = description.value_fn(m)
            if value is None:
                continue

            try:
                float_val = float(value)
            except (ValueError, TypeError):
                continue

            seen_timestamps.add(start_time)
            stat_data_list.append(
                StatisticData(
                    start=start_time,
                    state=float_val,
                    mean=float_val,
                    min=float_val,
                    max=float_val,
                )
            )

        if stat_data_list:
            LOGGER.debug(
                "Importing %d historical statistics points for %s",
                len(stat_data_list),
                stat_id,
            )
            async_import_statistics(hass, metadata, stat_data_list)
            total_imported += len(stat_data_list)

    LOGGER.info(
        "Successfully imported %d data points for %s",
        total_imported,
        coordinator.config_entry.title,
    )
    return total_imported
