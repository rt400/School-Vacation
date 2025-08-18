"""
Binary sensor platform for the Israel School Holidays integration.

This platform creates binary sensors indicating whether it is a school holiday
in Israel for elementary and high schools based on the coordinator's data.
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
    Set up Israel School Holidays binary sensors from a config entry.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry for this integration.
        async_add_entities: Callback function to add entities.

    This function:
    - Retrieves the coordinator from hass.data.
    - Ensures the coordinator has loaded data initially.
    - Creates binary sensor entities for elementary and high school vacations if enabled.
    - Adds the entities to Home Assistant.
    """
    coordinator: SchoolHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Ensure the coordinator has the initial data loaded
    await coordinator.async_config_entry_first_refresh()

    entities = []

    if coordinator.elementary_enabled:
        entities.append(SchoolHolidaysBinarySensor(coordinator, "elementary_vacation", entry))

    if coordinator.high_enabled:
        entities.append(SchoolHolidaysBinarySensor(coordinator, "high_vacation", entry))

    async_add_entities(entities)


class SchoolHolidaysBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """
    Representation of a school holidays binary sensor.

    This sensor uses the SchoolHolidaysCoordinator to determine if today is a vacation day
    for elementary or high schools.
    """

    def __init__(
        self,
        coordinator: SchoolHolidaysCoordinator,
        sensor_type: str,
        entry: ConfigEntry
    ) -> None:
        """
        Initialize the binary sensor.

        Args:
            coordinator: The data coordinator instance.
            sensor_type: Type of the sensor ("elementary_vacation" or "high_vacation").
            entry: Configuration entry for this integration.
        """
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._entry = entry
        self._coordinator = coordinator

        # Set sensor attributes based on language and type
        language = coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        self.entity_id = f"binary_sensor.{sensor_type}"
        self._attr_name = entity_names[sensor_type]
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = BINARY_SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_class = BINARY_SENSOR_TYPES[sensor_type]["device_class"]

    @property
    def name(self) -> str:
        """Return the sensor name according to the current language."""
        language = self._coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        return entity_names[self._sensor_type]

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return information about the device this sensor belongs to.

        This allows Home Assistant to group sensors under a common device.
        """
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
    def is_on(self) -> Optional[bool]:
        """
        Return True if today is a vacation day, False otherwise.

        Returns None if the coordinator has not yet provided data.
        """
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._sensor_type, False)

    @property
    def extra_state_attributes(self) -> dict:
        """
        Return additional state attributes for the sensor.

        Attributes include:
        - summary: Human-readable description of the day's status
        - last_update: Timestamp of last data update
        - sensor_type: Type of this sensor
        - language: Current language of the integration
        """
        if not self.coordinator.data:
            return {}
        return {
            "summary": self.coordinator.data.get("summary"),
            "last_update": self.coordinator.data.get("last_update"),
            "sensor_type": self._sensor_type,
            "language": self._coordinator.language,
        }

    @property
    def available(self) -> bool:
        """Return True if the entity is currently available."""
        return self.coordinator.last_update_success
