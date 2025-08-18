"""
Israel School Holidays integration for Home Assistant.

This integration provides sensors to indicate whether it is a school holiday
in Israel for elementary and high schools, based on static local data.
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import SchoolHolidaysCoordinator

# Supported platforms provided by this integration
PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up the Israel School Holidays integration from a config entry.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry for this integration.

    Returns:
        True if setup was successful.

    This function:
    - Creates the SchoolHolidaysCoordinator instance.
    - Stores it in hass.data for access by other components.
    - Forwards the config entry setup to the supported platforms.
    - Listens for option changes to reload the integration if needed.
    """
    coordinator = SchoolHolidaysCoordinator(hass, entry)

    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to each supported platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for option changes and reload integration if necessary
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload the Israel School Holidays integration.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry for this integration.

    Returns:
        True if all platforms were successfully unloaded.

    This function:
    - Unloads all platforms associated with the entry.
    - Removes the coordinator from hass.data.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Reload the Israel School Holidays integration.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry to reload.

    This function is triggered when options of the config entry change.
    It first unloads the entry and then sets it up again.
    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
