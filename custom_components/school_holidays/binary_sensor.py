"""Binary sensor platform for Israel School Holidays.

This platform provides binary sensors to track school vacations for
elementary and high schools in Israel, supporting language selection
and data from the coordinator.
"""
import logging
from typing import Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    BINARY_SENSOR_TYPES,
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
    Set up the Israel School Holidays binary sensor platform.

    Creates and adds sensors to track vacations for elementary and high schools
    based on user configuration.
    """
    coordinator: SchoolHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    if coordinator.elementary_enabled:
        entities.append(SchoolHolidaysBinarySensor(coordinator, "elementary_vacation", entry))

    if coordinator.high_enabled:
        entities.append(SchoolHolidaysBinarySensor(coordinator, "high_vacation", entry))

    async_add_entities(entities)


class SchoolHolidaysBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """
    Representation of a school holidays binary sensor.

    The sensor indicates whether the current day is a vacation day for
    elementary or high schools.
    """

    def __init__(
        self,
        coordinator: SchoolHolidaysCoordinator,
        sensor_type: str,
        entry: ConfigEntry
    ) -> None:
        """
        Initialize the binary sensor.

        :param coordinator: The main data coordinator for vacation data.
        :param sensor_type: The sensor type (e.g., "elementary_vacation" or "high_vacation").
        :param entry: The integration config entry.
        """
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._entry = entry
        self._coordinator = coordinator

        # Set name, icon, and unique ID based on language and sensor type
        language = coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        self.entity_id = f"binary_sensor.{sensor_type}"
        self._attr_name = entity_names[sensor_type]
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = BINARY_SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_class = BINARY_SENSOR_TYPES[sensor_type]["device_class"]

    @property
    def name(self) -> str:
        """Return the sensor name considering the current display language."""
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
            sw_version="3.0.0",
            configuration_url="https://github.com/rt400/School-Vacation",
        )

    @property
    def is_on(self) -> Optional[bool]:
        """
        Return True if the sensor is on (i.e., if today is a vacation day).

        Returns None if data is unavailable.
        """
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type, False)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        return {
            "summary": self.coordinator.data.get("summary"),
            "last_update": self.coordinator.data.get("last_update"),
            "sensor_type": self._sensor_type,
            "language": self._coordinator.language,
        }

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return self.coordinator.last_update_success
