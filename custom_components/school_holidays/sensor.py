"""Sensor platform for Israel School Holidays.

This platform provides a sensor to report the current summary status of
school vacations for elementary and high schools in Israel. The sensor's
state and attributes update dynamically based on data fetched by the coordinator.
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

    This function is called by Home Assistant to create and add sensor entities
    based on the configuration entry.
    """
    coordinator: SchoolHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Always create the summary sensor entity
    entities.append(SchoolHolidaysSensor(coordinator, "summary", entry))

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
            coordinator: The data update coordinator instance.
            sensor_type: Type of the sensor, e.g., 'summary'.
            entry: The config entry for this integration.
        """
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._entry = entry
        self._coordinator = coordinator

        # Determine entity display name and properties based on selected language
        language = coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        self.entity_id = "sensor.school_summary"
        self._attr_name = entity_names[sensor_type]
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_class = SENSOR_TYPES[sensor_type]["device_class"]

    @property
    def name(self) -> str:
        """Return the name of the sensor, updating with language changes."""
        language = self._coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        return entity_names[self._sensor_type]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the integration."""
        language = self._coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=entity_names["device_name"],
            manufacturer="Yuval Mejahez",
            model="School Calendar Tracker",
            sw_version="3.0.0",
            configuration_url="https://github.com/rt400/School-Vacation",
        )

    @property
    def native_value(self) -> Optional[str]:
        """
        Return the current state of the sensor.

        This typically returns the summary text describing
        the current vacation status.
        """
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes related to the current vacation state."""
        if self.coordinator.data is None:
            return {}

        return {
            "elementary_vacation": self.coordinator.data.get("elementary_vacation"),
            "high_vacation": self.coordinator.data.get("high_vacation"),
            "last_update": self.coordinator.data.get("last_update"),
            "language": self._coordinator.language,
        }

    @property
    def available(self) -> bool:
        """Return True if the entity is available (data successfully updated)."""
        return self.coordinator.last_update_success
