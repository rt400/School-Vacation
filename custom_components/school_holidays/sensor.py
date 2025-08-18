"""
Sensor platform for Israel School Holidays integration.

Creates a sensor entity that provides a summary of school holidays
in Israel. Uses data from the SchoolHolidaysCoordinator.
"""

import logging
from typing import Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    ENTITY_NAMES,
    VERSION,
)
from .coordinator import SchoolHolidaysCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up the Israel School Holidays sensor platform.

    Args:
        hass: HomeAssistant instance
        entry: ConfigEntry instance
        async_add_entities: Callback function to add entities
    """
    coordinator: SchoolHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Ensure coordinator has initial data before creating entities
    await coordinator.async_config_entry_first_refresh()

    entities = [SchoolHolidaysSensor(coordinator, "summary", entry)]
    async_add_entities(entities)


class SchoolHolidaysSensor(CoordinatorEntity, SensorEntity):
    """Representation of a school holidays summary sensor."""

    def __init__(
        self,
        coordinator: SchoolHolidaysCoordinator,
        sensor_type: str,
        entry: ConfigEntry
    ) -> None:
        """
        Initialize the sensor entity.

        Args:
            coordinator: The coordinator instance providing data updates
            sensor_type: Type of sensor (e.g., "summary")
            entry: The associated config entry
        """
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._entry = entry
        self._coordinator = coordinator

        language = coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        self.entity_id = "sensor.school_summary"
        self._attr_name = entity_names[sensor_type]
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_class = SENSOR_TYPES[sensor_type]["device_class"]

    @property
    def name(self) -> str:
        """Return the sensor name according to the selected language."""
        language = self._coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        return entity_names[self._sensor_type]

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device this sensor belongs to."""
        language = self._coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=entity_names["device_name"],
            manufacturer="Yuval Mejahez",
            model="School Calendar Tracker",
            sw_version=VERSION,
            configuration_url="https://github.com/rt400/School-Vacation",
        )

    @property
    def native_value(self) -> Optional[str]:
        """
        Return the main value of the sensor (summary of school holidays).

        Returns:
            str: Summary text, or None if data is not yet available
        """
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._sensor_type)

    @property
    def extra_state_attributes(self) -> dict:
        """
        Return additional state attributes for the sensor.

        Includes elementary/high school vacation status, last update, and language.
        """
        if not self.coordinator.data:
            return {}

        return {
            "elementary_vacation": self.coordinator.data.get("elementary_vacation"),
            "high_vacation": self.coordinator.data.get("high_vacation"),
            "last_update": self.coordinator.data.get("last_update"),
            "language": self._coordinator.language,
        }

    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self.coordinator.last_update_success
