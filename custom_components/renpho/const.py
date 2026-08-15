"""Constants for the Renpho integration."""

from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "renpho"
LOGGER = logging.getLogger(__package__)

ATTRIBUTION: Final = "Data provided by Renpho"

CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_EXTRA_USER_IDS: Final = "extra_user_ids"

DEFAULT_SCAN_INTERVAL: Final = 60  # minutes
MIN_SCAN_INTERVAL: Final = 5  # minutes
MAX_SCAN_INTERVAL: Final = 1440  # minutes (24 hours)
