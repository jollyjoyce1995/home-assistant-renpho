"""Config flow and options flow for the Renpho integration."""

from __future__ import annotations

from typing import Any

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.helpers import selector

from renpho import RenphoClient
from renpho.client import RenphoAPIError

from .const import (
    CONF_EXTRA_USER_IDS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


class RenphoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renpho."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> RenphoOptionsFlowHandler:
        """Get the options flow for this handler."""
        return RenphoOptionsFlowHandler(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL].strip()
            password = user_input[CONF_PASSWORD]
            client = RenphoClient(email=email, password=password)

            try:
                await self.hass.async_add_executor_job(client.login)
            except RenphoAPIError as err:
                LOGGER.warning("Renpho API error during auth: %s", err)
                if (
                    err.code in (401, 403)
                    or "auth" in err.msg.lower()
                    or "login" in err.context.lower()
                    or "password" in err.msg.lower()
                    or "token" in err.msg.lower()
                ):
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
            except requests.RequestException as err:
                LOGGER.error("Connection error communicating with Renpho: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error during Renpho config flow")
                errors["base"] = "unknown"
            else:
                unique_id = str(client.user_id or email.lower())
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                user_info = client.user_info or {}
                title = user_info.get("nickName") or user_info.get("email") or email

                return self.async_create_entry(
                    title=f"Renpho ({title})",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_EMAIL,
                    default=(user_input or {}).get(CONF_EMAIL, vol.UNDEFINED),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.EMAIL,
                        autocomplete="email",
                    ),
                ),
                vol.Required(CONF_PASSWORD): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD,
                        autocomplete="current-password",
                    ),
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=(user_input or {}).get(
                        CONF_SCAN_INTERVAL,
                        DEFAULT_SCAN_INTERVAL,
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        unit_of_measurement="min",
                        mode=selector.NumberSelectorMode.BOX,
                    ),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


class RenphoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Renpho."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize Renpho options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage the Renpho options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        current_extra_users = self._config_entry.options.get(
            CONF_EXTRA_USER_IDS,
            self._config_entry.data.get(CONF_EXTRA_USER_IDS, ""),
        )

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        unit_of_measurement="min",
                        mode=selector.NumberSelectorMode.BOX,
                    ),
                ),
                vol.Optional(
                    CONF_EXTRA_USER_IDS,
                    default=current_extra_users or "",
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    ),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
