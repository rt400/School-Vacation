"""Binary sensor platform for Israel School Holidays."""
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
)
from .coordinator import SchoolHolidaysCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Israel School Holidays binary sensor platform."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    if coordinator.elementary_enabled:
        entities.append(SchoolHolidaysBinarySensor(coordinator, "elementary_vacation", entry))
    
    if coordinator.high_enabled:
        entities.append(SchoolHolidaysBinarySensor(coordinator, "high_vacation", entry))
    
    async_add_entities(entities)


class SchoolHolidaysBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a school holidays binary sensor."""

    def __init__(
        self, 
        coordinator: SchoolHolidaysCoordinator, 
        sensor_type: str,
        entry: ConfigEntry
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._entry = entry
        self._coordinator = coordinator
        
        # Get name based on selected language
        language = coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        self.entity_id = f"binary_sensor.{sensor_type}"
        self._attr_name = entity_names[sensor_type]
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = BINARY_SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_class = BINARY_SENSOR_TYPES[sensor_type]["device_class"]

    @property
    def name(self) -> str:
        """Return the name of the sensor (updates with language changes)."""
        language = self._coordinator.language
        entity_names = ENTITY_NAMES.get(language, ENTITY_NAMES["he"])
        return entity_names[self._sensor_type]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
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
        """Return true if the binary sensor is on."""
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
        """Return if entity is available."""
        return self.coordinator.last_update_success
