"""
Israel School Holidays integration for Home Assistant.

This integration creates sensors to indicate whether it is a school holiday
in Israel for elementary and high schools.

It uses a DataUpdateCoordinator to fetch and store holiday data from
a remote API (or local cache), and provides status updates based on the
current date and configuration options.

Main responsibilities:
- Initialize the data coordinator.
- Register binary and standard sensors for school holiday status.
- Handle setup, unloading, and reloading when options are changed.
"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import SchoolHolidaysCoordinator

_LOGGER = logging.getLogger(__name__)

# Platforms provided by this integration (binary sensors + regular sensors)
PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up Israel School Holidays integration from a config entry.

    This function:
    1. Creates the DataUpdateCoordinator instance that manages holiday data.
    2. Performs the initial data refresh.
    3. Stores the coordinator in hass.data for later access by platforms.
    4. Forwards the config entry to the platforms (binary_sensor, sensor).
    5. Registers a listener to reload the integration when options change.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry for this integration.

    Returns:
        bool: True if setup was successful.
    """
    coordinator = SchoolHolidaysCoordinator(hass, entry)

    # Perform the first refresh to ensure sensors have data immediately
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in hass.data so platforms can access it
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to each supported platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for updates in options and reload if needed
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload the Israel School Holidays integration.

    This function:
    1. Unloads all platforms registered for this integration.
    2. Removes the coordinator from hass.data if unloading succeeded.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry to unload.

    Returns:
        bool: True if unloading was successful.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Reload the Israel School Holidays integration.

    This is called when integration options change in the UI.
    It unloads the integration and sets it up again.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry to reload.
    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
