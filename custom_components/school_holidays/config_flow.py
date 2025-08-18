"""
Config flow for Israel School Holidays integration.

Handles the configuration and options flow for the Israel School Holidays
integration within Home Assistant. Supports selecting languages,
enabling vacation tracking for elementary and high schools, and other options.
"""

from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_ELEMENTARY_SCHOOL,
    CONF_HIGH_SCHOOL,
    CONF_FRIDAY_HIGH_SCHOOL,
    CONF_LANGUAGE,
    DEFAULT_ELEMENTARY_SCHOOL,
    DEFAULT_HIGH_SCHOOL,
    DEFAULT_FRIDAY_HIGH_SCHOOL,
    DEFAULT_LANGUAGE,
    LANGUAGE_OPTIONS,
)

# Schema used in the initial configuration step
STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(LANGUAGE_OPTIONS),
    vol.Optional(CONF_ELEMENTARY_SCHOOL, default=DEFAULT_ELEMENTARY_SCHOOL): bool,
    vol.Optional(CONF_HIGH_SCHOOL, default=DEFAULT_HIGH_SCHOOL): bool,
    vol.Optional(CONF_FRIDAY_HIGH_SCHOOL, default=DEFAULT_FRIDAY_HIGH_SCHOOL): bool,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Israel School Holidays integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """
        Handle the initial configuration step.

        Args:
            user_input: Optional dictionary containing user-selected options.

        Returns:
            FlowResult: Either shows the form or creates a new config entry.
        """
        if user_input is None:
            # Show the initial configuration form
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        # Create the config entry with user input
        return self.async_create_entry(title="Israel School Holidays", data=user_input)

    @staticmethod
    def async_get_options_flow(config_entry):
        """
        Return the options flow handler for this config entry.

        Args:
            config_entry: The configuration entry to manage options for.

        Returns:
            OptionsFlowHandler instance
        """
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Israel School Holidays integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """
        Initialize the options flow handler.

        Args:
            config_entry: The configuration entry for which options are managed.
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """
        Manage user options during the options flow.

        Args:
            user_input: Optional dictionary containing user-selected options.

        Returns:
            FlowResult: Either shows the options form or updates the entry.
        """
        if user_input is not None:
            # Update options and finish flow
            return self.async_create_entry(title="", data=user_input)

        # Show options form with current or default values
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
            }),
        )
