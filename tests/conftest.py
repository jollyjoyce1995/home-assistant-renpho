"""Fixtures and Home Assistant mocks for Renpho integration tests."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Generic, TypeVar
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Setup Home Assistant mock modules if not installed in the environment
# ---------------------------------------------------------------------------

_T = TypeVar("_T")

if "homeassistant" not in sys.modules:
    ha = types.ModuleType("homeassistant")
    ha_const = types.ModuleType("homeassistant.const")
    ha_core = types.ModuleType("homeassistant.core")
    ha_exceptions = types.ModuleType("homeassistant.exceptions")
    ha_loader = types.ModuleType("homeassistant.loader")
    ha_config_entries = types.ModuleType("homeassistant.config_entries")
    ha_helpers = types.ModuleType("homeassistant.helpers")
    ha_helpers_device_registry = types.ModuleType(
        "homeassistant.helpers.device_registry"
    )
    ha_helpers_update_coordinator = types.ModuleType(
        "homeassistant.helpers.update_coordinator"
    )
    ha_helpers_entity_platform = types.ModuleType(
        "homeassistant.helpers.entity_platform"
    )
    ha_helpers_selector = types.ModuleType("homeassistant.helpers.selector")
    ha_components = types.ModuleType("homeassistant.components")
    ha_components_sensor = types.ModuleType("homeassistant.components.sensor")
    ha_components_button = types.ModuleType("homeassistant.components.button")

    # const
    ha_const.CONF_EMAIL = "email"
    ha_const.CONF_PASSWORD = "password"
    ha_const.CONF_USERNAME = "username"
    ha_const.PERCENTAGE = "%"

    class Platform(StrEnum):
        SENSOR = "sensor"
        BUTTON = "button"
        BINARY_SENSOR = "binary_sensor"
        SWITCH = "switch"

    class UnitOfMass(StrEnum):
        KILOGRAMS = "kg"
        POUNDS = "lb"

    class UnitOfEnergy(StrEnum):
        KILO_CALORIE = "kcal"

    class UnitOfTime(StrEnum):
        YEARS = "years"

    class EntityCategory(StrEnum):
        CONFIG = "config"
        DIAGNOSTIC = "diagnostic"

    ha_const.Platform = Platform
    ha_const.UnitOfMass = UnitOfMass
    ha_const.UnitOfEnergy = UnitOfEnergy
    ha_const.UnitOfTime = UnitOfTime
    ha_const.EntityCategory = EntityCategory

    # core
    def callback(fn):
        return fn

    ha_core.callback = callback
    ha_core.HomeAssistant = MagicMock

    # exceptions
    class HomeAssistantError(Exception):
        pass

    class ConfigEntryAuthFailed(HomeAssistantError):
        pass

    ha_exceptions.HomeAssistantError = HomeAssistantError
    ha_exceptions.ConfigEntryAuthFailed = ConfigEntryAuthFailed

    # loader
    ha_loader.async_get_loaded_integration = MagicMock()
    ha_loader.Integration = MagicMock

    # config_entries
    class ConfigFlow:
        hass = None

        def __init_subclass__(cls, domain=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls._domain = domain

        def async_show_form(
            self, step_id, data_schema=None, errors=None, description_placeholders=None
        ):
            return {
                "type": "form",
                "step_id": step_id,
                "data_schema": data_schema,
                "errors": errors or {},
            }

        def async_create_entry(self, title, data):
            return {
                "type": "create_entry",
                "title": title,
                "data": data,
            }

        async def async_set_unique_id(self, unique_id):
            pass

        def _abort_if_unique_id_configured(self):
            pass

    class OptionsFlow:
        def __init__(self, config_entry=None):
            self.config_entry = config_entry

        def async_show_form(self, step_id, data_schema=None, errors=None):
            return {
                "type": "form",
                "step_id": step_id,
                "data_schema": data_schema,
                "errors": errors or {},
            }

        def async_create_entry(self, title, data):
            return {
                "type": "create_entry",
                "title": title,
                "data": data,
            }

    class ConfigEntry(Generic[_T]):
        pass

    ha_config_entries.ConfigFlow = ConfigFlow
    ha_config_entries.OptionsFlow = OptionsFlow
    ha_config_entries.ConfigEntry = ConfigEntry
    ha_config_entries.ConfigFlowResult = dict

    # helpers
    @dataclass
    class DeviceInfo:
        identifiers: set
        name: str
        manufacturer: str | None = None
        model: str | None = None
        serial_number: str | None = None

    ha_helpers_device_registry.DeviceInfo = DeviceInfo

    class UpdateFailed(HomeAssistantError):
        pass

    class DataUpdateCoordinator(Generic[_T]):
        def __init__(self, hass, logger, name, update_interval=None, config_entry=None):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval
            self.config_entry = config_entry
            self.data: Any = {}
            self.last_update_success = True

        async def async_config_entry_first_refresh(self):
            pass

        async def async_request_refresh(self):
            pass

    class CoordinatorEntity(Generic[_T]):
        def __init__(self, coordinator):
            self.coordinator = coordinator
            self._attr_has_entity_name = True

    ha_helpers_update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
    ha_helpers_update_coordinator.CoordinatorEntity = CoordinatorEntity
    ha_helpers_update_coordinator.UpdateFailed = UpdateFailed

    ha_helpers_entity_platform.AddEntitiesCallback = MagicMock

    # selectors
    class TextSelectorType(StrEnum):
        TEXT = "text"
        PASSWORD = "password"
        EMAIL = "email"

    @dataclass
    class TextSelectorConfig:
        type: TextSelectorType = TextSelectorType.TEXT
        autocomplete: str | None = None

    class TextSelector:
        def __init__(self, config: TextSelectorConfig | None = None):
            self.config = config

        def __call__(self, value: Any) -> Any:
            return value

    class NumberSelectorMode(StrEnum):
        BOX = "box"
        SLIDER = "slider"

    @dataclass
    class NumberSelectorConfig:
        min: float = 0
        max: float = 100
        step: float = 1
        unit_of_measurement: str | None = None
        mode: NumberSelectorMode = NumberSelectorMode.BOX

    class NumberSelector:
        def __init__(self, config: NumberSelectorConfig | None = None):
            self.config = config

        def __call__(self, value: Any) -> Any:
            return value

    ha_helpers_selector.TextSelector = TextSelector
    ha_helpers_selector.TextSelectorConfig = TextSelectorConfig
    ha_helpers_selector.TextSelectorType = TextSelectorType
    ha_helpers_selector.NumberSelector = NumberSelector
    ha_helpers_selector.NumberSelectorConfig = NumberSelectorConfig
    ha_helpers_selector.NumberSelectorMode = NumberSelectorMode

    ha_helpers.selector = ha_helpers_selector
    ha_helpers.device_registry = ha_helpers_device_registry
    ha_helpers.update_coordinator = ha_helpers_update_coordinator
    ha_helpers.entity_platform = ha_helpers_entity_platform

    # sensor
    class SensorDeviceClass(StrEnum):
        WEIGHT = "weight"
        TIMESTAMP = "timestamp"

    class SensorStateClass(StrEnum):
        MEASUREMENT = "measurement"
        TOTAL = "total"

    @dataclass(frozen=True, kw_only=True)
    class SensorEntityDescription:
        key: str
        translation_key: str | None = None
        device_class: SensorDeviceClass | None = None
        native_unit_of_measurement: str | None = None
        state_class: SensorStateClass | None = None
        icon: str | None = None

    class SensorEntity:
        entity_description: SensorEntityDescription

    ha_components_sensor.SensorDeviceClass = SensorDeviceClass
    ha_components_sensor.SensorStateClass = SensorStateClass
    ha_components_sensor.SensorEntityDescription = SensorEntityDescription
    ha_components_sensor.SensorEntity = SensorEntity

    # button
    class ButtonDeviceClass(StrEnum):
        RESTART = "restart"
        UPDATE = "update"

    @dataclass(frozen=True, kw_only=True)
    class ButtonEntityDescription:
        key: str
        translation_key: str | None = None
        device_class: ButtonDeviceClass | None = None
        icon: str | None = None

    class ButtonEntity:
        entity_description: ButtonEntityDescription

    ha_components_button.ButtonDeviceClass = ButtonDeviceClass
    ha_components_button.ButtonEntityDescription = ButtonEntityDescription
    ha_components_button.ButtonEntity = ButtonEntity

    ha_components.sensor = ha_components_sensor
    ha_components.button = ha_components_button

    ha.const = ha_const
    ha.core = ha_core
    ha.exceptions = ha_exceptions
    ha.loader = ha_loader
    ha.config_entries = ha_config_entries
    ha.helpers = ha_helpers
    ha.components = ha_components

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.const"] = ha_const
    sys.modules["homeassistant.core"] = ha_core
    sys.modules["homeassistant.exceptions"] = ha_exceptions
    sys.modules["homeassistant.loader"] = ha_loader
    sys.modules["homeassistant.config_entries"] = ha_config_entries
    sys.modules["homeassistant.helpers"] = ha_helpers
    sys.modules["homeassistant.helpers.device_registry"] = ha_helpers_device_registry
    sys.modules["homeassistant.helpers.update_coordinator"] = (
        ha_helpers_update_coordinator
    )
    sys.modules["homeassistant.helpers.entity_platform"] = ha_helpers_entity_platform
    sys.modules["homeassistant.helpers.selector"] = ha_helpers_selector
    sys.modules["homeassistant.components"] = ha_components
    sys.modules["homeassistant.components.sensor"] = ha_components_sensor
    sys.modules["homeassistant.components.button"] = ha_components_button


# ---------------------------------------------------------------------------
# Test Fixtures & Data
# ---------------------------------------------------------------------------

MOCK_MEASUREMENT = {
    "id": "12345",
    "timeStamp": 1700000000,
    "time_stamp": 1700000000,
    "localCreatedAt": "2023-11-14 22:13:20",
    "scaleName": "ES-26M-W",
    "userId": "987654321",
    "weight": 72.5,
    "bmi": 22.4,
    "bodyfat": 18.5,
    "water": 58.2,
    "muscle": 45.1,
    "bone": 3.2,
    "bmr": 1650,
    "visfat": 6,
    "subfat": 14.2,
    "protein": 19.1,
    "bodyage": 28,
    "sinew": 59.1,
    "fatFreeWeight": 59.1,
    "heartRate": 68,
    "cardiacIndex": 2.8,
}

MOCK_USER_INFO = {
    "id": "987654321",
    "email": "test@example.com",
    "nickName": "Test User",
    "token": "fake_token_12345",
}

MOCK_DEVICE_INFO = {
    "scale": [
        {
            "tableName": "measurements_info_9",
            "count": 1,
            "userIds": ["987654321"],
        }
    ]
}


@pytest.fixture
def mock_renpho_client():
    """Mock RenphoClient instance."""
    client = MagicMock()
    client.email = "test@example.com"
    client.password = "password123"
    client.token = "fake_token_12345"
    client.user_id = "987654321"
    client.user_info = MOCK_USER_INFO
    client.login.return_value = {"login": MOCK_USER_INFO}
    client.get_all_measurements.return_value = [MOCK_MEASUREMENT]
    client.get_device_info.return_value = MOCK_DEVICE_INFO
    client.get_girth_measurements.return_value = []
    return client
