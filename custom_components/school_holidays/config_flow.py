"""Config flow for Israel School Holidays integration.

This module handles the configuration flow for the Israel School Holidays
integration within Home Assistant. It manages user input, validation,
and options for the integration setup and updates.

The flow supports selecting languages, enabling vacation tracking
for elementary and high schools, setting update intervals, and
handling errors during configuration.
"""
import logging
from typing import Any, Dict, Optional
import voluptuous as vol
import aiohttp
import json

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_ELEMENTARY_SCHOOL,
    CONF_HIGH_SCHOOL,
    CONF_FRIDAY_HIGH_SCHOOL,
    CONF_UPDATE_INTERVAL,
    CONF_LANGUAGE,
    DEFAULT_ELEMENTARY_SCHOOL,
    DEFAULT_HIGH_SCHOOL,
    DEFAULT_FRIDAY_HIGH_SCHOOL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_LANGUAGE,
    LANGUAGE_OPTIONS,
    DATA_URL,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_DATA,
    ERROR_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(LANGUAGE_OPTIONS),
    vol.Optional(CONF_ELEMENTARY_SCHOOL, default=DEFAULT_ELEMENTARY_SCHOOL): bool,
    vol.Optional(CONF_HIGH_SCHOOL, default=DEFAULT_HIGH_SCHOOL): bool,
    vol.Optional(CONF_FRIDAY_HIGH_SCHOOL, default=DEFAULT_FRIDAY_HIGH_SCHOOL): bool,
    vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=168)
    ),
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the user input by attempting to connect and retrieve data.

    This function attempts to fetch data from the predefined DATA_URL to
    verify connectivity and validate the data structure returned by the server.

    Args:
        hass: Home Assistant instance.
        data: User input data from the config flow form.

    Raises:
        CannotConnect: If the integration cannot connect to the data source.
        InvalidData: If the returned data is invalid or malformed.

    Returns:
        A dictionary with configuration info (e.g., title) if validation succeeds.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DATA_URL, timeout=30) as response:
                if response.status != 200:
                    raise CannotConnect
                
                content = await response.text()
                school_data = json.loads(content)
                
                if not isinstance(school_data, list) or not school_data:
                    raise InvalidData
                
                # Validate structure of first few entries
                for item in school_data[:3]:
                    if not all(key in item for key in ['START', 'END']):
                        raise InvalidData
                        
    except aiohttp.ClientError:
        raise CannotConnect
    except json.JSONDecodeError:
        raise InvalidData
    except Exception:
        raise InvalidData

    return {"title": "Israel School Holidays"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Israel School Holidays integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """
        Handle the initial configuration step.

        Displays a form to the user to collect configuration options.
        Validates the input by attempting to fetch and verify data.
        """
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "language_desc": "Choose the display language for entity names",
                    "elementary_desc": "Enable elementary school vacation tracking",
                    "high_desc": "Enable high school vacation tracking",
                    "friday_desc": "High schools have no classes on Fridays",
                    "interval_desc": "Hours between data updates (1-168)"
                }
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = ERROR_CANNOT_CONNECT
        except InvalidData:
            errors["base"] = ERROR_INVALID_DATA
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception during config flow")
            errors["base"] = ERROR_UNKNOWN
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "language_desc": "Choose the display language for entity names",
                "elementary_desc": "Enable elementary school vacation tracking",
                "high_desc": "Enable high school vacation tracking",
                "friday_desc": "High schools have no classes on Fridays",
                "interval_desc": "Hours between data updates (1-168)"
            }
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """
        Create and return the options flow handler for this config entry.
        """
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Israel School Holidays integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow handler."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """
        Manage user options during the flow.

        Allows updating language, vacation tracking options, and update interval.
        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_LANGUAGE,
                    default=self.config_entry.options.get(
                        CONF_LANGUAGE,
                        self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
                    ),
                ): vol.In(LANGUAGE_OPTIONS),
                vol.Optional(
                    CONF_ELEMENTARY_SCHOOL,
                    default=self.config_entry.options.get(
                        CONF_ELEMENTARY_SCHOOL,
                        self.config_entry.data.get(CONF_ELEMENTARY_SCHOOL, DEFAULT_ELEMENTARY_SCHOOL)
                    ),
                ): bool,
                vol.Optional(
                    CONF_HIGH_SCHOOL,
                    default=self.config_entry.options.get(
                        CONF_HIGH_SCHOOL,
                        self.config_entry.data.get(CONF_HIGH_SCHOOL, DEFAULT_HIGH_SCHOOL)
                    ),
                ): bool,
                vol.Optional(
                    CONF_FRIDAY_HIGH_SCHOOL,
                    default=self.config_entry.options.get(
                        CONF_FRIDAY_HIGH_SCHOOL,
                        self.config_entry.data.get(CONF_FRIDAY_HIGH_SCHOOL, DEFAULT_FRIDAY_HIGH_SCHOOL)
                    ),
                ): bool,
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL,
                        self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            }),
        )


class CannotConnect(HomeAssistantError):
    """Exception to indicate connection failure during validation."""


class InvalidData(HomeAssistantError):
    """Exception to indicate invalid data returned during validation."""
