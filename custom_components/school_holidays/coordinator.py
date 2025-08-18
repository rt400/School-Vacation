"""
Data coordinator for Israel School Holidays.

This module manages local school holiday data for Israel.
Updates are performed:
- Immediately when Home Assistant starts or restarts
- Daily at 12:00 AM
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_change

from .const import (
    DOMAIN,
    CONF_ELEMENTARY_SCHOOL,
    CONF_HIGH_SCHOOL,
    CONF_FRIDAY_HIGH_SCHOOL,
    CONF_LANGUAGE,
    HEBREW_TEXTS,
    HOLIDAYS_DATA,
)

_LOGGER = logging.getLogger(__name__)

class SchoolHolidaysCoordinator(DataUpdateCoordinator):
    """Coordinator that handles Israel school holiday data using local data only."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """
        Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            entry: Config entry containing user options
        """
        self.hass = hass
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # No automatic updates besides scheduled
        )

        self._school_data: List[Dict[str, Any]] = HOLIDAYS_DATA
        self._last_update: datetime = datetime.now()

        # Immediate refresh on HA start/restart
        self.hass.async_create_task(self.async_refresh())

        # Schedule daily refresh at 12:00 AM
        async_track_time_change(
            self.hass,
            self._daily_refresh_callback,
            hour=0,
            minute=0,
            second=0,
        )

    @property
    def elementary_enabled(self) -> bool:
        """Return True if elementary school vacation checks are enabled."""
        return self.entry.options.get(
            CONF_ELEMENTARY_SCHOOL,
            self.entry.data.get(CONF_ELEMENTARY_SCHOOL, True)
        )

    @property
    def high_enabled(self) -> bool:
        """Return True if high school vacation checks are enabled."""
        return self.entry.options.get(
            CONF_HIGH_SCHOOL,
            self.entry.data.get(CONF_HIGH_SCHOOL, True)
        )

    @property
    def friday_high_enabled(self) -> bool:
        """Return True if Fridays are considered vacation for high school."""
        return self.entry.options.get(
            CONF_FRIDAY_HIGH_SCHOOL,
            self.entry.data.get(CONF_FRIDAY_HIGH_SCHOOL, True)
        )

    @property
    def language(self) -> str:
        """Return the selected language for holiday descriptions."""
        return self.entry.options.get(
            CONF_LANGUAGE,
            self.entry.data.get(CONF_LANGUAGE, "he")
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """
        Fetch the latest vacation status.

        Returns:
            Dictionary containing:
            - elementary_vacation (bool)
            - high_vacation (bool)
            - summary (str)
            - last_update (ISO string)
            - raw_data (list of all holiday entries)
        """
        self._last_update = datetime.now()
        _LOGGER.info("Updating school holiday status at %s", self._last_update.isoformat())
        try:
            status = await self._calculate_status()
            return {
                "elementary_vacation": status.get("elementary_vacation", False),
                "high_vacation": status.get("high_vacation", False),
                "summary": status.get("summary", HEBREW_TEXTS["school_day"]),
                "last_update": self._last_update.isoformat(),
                "raw_data": self._school_data
            }
        except Exception as err:
            _LOGGER.error("Error calculating school holidays data: %s", err)
            return {
                "elementary_vacation": False,
                "high_vacation": False,
                "summary": HEBREW_TEXTS["school_day"],
                "last_update": self._last_update.isoformat(),
                "raw_data": self._school_data
            }

    async def _calculate_status(self) -> Dict[str, Any]:
        """
        Determine the current vacation status for today.

        Returns:
            Dictionary with keys:
            - elementary_vacation (bool)
            - high_vacation (bool)
            - summary (str)
        """
        today = date.today()
        weekday = today.isoweekday()

        for vacation_data in self._school_data:
            if self._is_date_in_vacation(today, vacation_data):
                if vacation_data.get("HIGH", False):
                    return {
                        "elementary_vacation": False,
                        "high_vacation": True,
                        "summary": HEBREW_TEXTS["big_vacation_high"]
                    }
                return {
                    "elementary_vacation": True,
                    "high_vacation": True,
                    "summary": vacation_data.get("SUMMARY", "Holiday")
                }

        # Friday special case for high school
        if weekday == 5 and self.friday_high_enabled:
            return {
                "elementary_vacation": False,
                "high_vacation": True,
                "summary": HEBREW_TEXTS["no_classes_high"]
            }

        # Saturday (sabbath)
        if weekday == 6:
            return {
                "elementary_vacation": True,
                "high_vacation": True,
                "summary": HEBREW_TEXTS["sabbath"]
            }

        # Default: school day
        return {
            "elementary_vacation": False,
            "high_vacation": False,
            "summary": HEBREW_TEXTS["school_day"]
        }

    def _is_date_in_vacation(self, check_date: date, vacation_data: Dict[str, Any]) -> bool:
        """
        Check if a given date falls within the specified vacation period.

        Args:
            check_date: Date to check
            vacation_data: Dictionary containing START, END, and optional SUMMARY

        Returns:
            True if check_date is within vacation period, False otherwise
        """
        try:
            start_date = datetime.strptime(str(vacation_data["START"]), "%Y-%m-%d").date()
            end_date = datetime.strptime(str(vacation_data["END"]), "%Y-%m-%d").date()
            return start_date <= check_date <= end_date
        except (KeyError, ValueError) as err:
            _LOGGER.warning("Invalid vacation data format: %s", err)
            return False

    async def _daily_refresh_callback(self, now=None) -> None:
        """
        Callback to refresh data daily at midnight.

        Args:
            now: Optional datetime passed by async_track_time_change
        """
        _LOGGER.info("Daily scheduled refresh triggered at %s", datetime.now().isoformat())
        await self.async_refresh()
