"""Data coordinator for Israel School Holidays.

This module manages fetching, storing, and evaluating school holiday
data for Israel. It loads data from a local cache, updates from a remote API,
and determines if the current date is a vacation day for elementary or high school.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any

import aiofiles
from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DATA_URL,
    DATA_FILE,
    CONF_ELEMENTARY_SCHOOL,
    CONF_HIGH_SCHOOL,
    CONF_FRIDAY_HIGH_SCHOOL,
    CONF_UPDATE_INTERVAL,
    CONF_LANGUAGE,
    DEFAULT_UPDATE_INTERVAL,
    HEBREW_TEXTS,
)

_LOGGER = logging.getLogger(__name__)


class SchoolHolidaysCoordinator(DataUpdateCoordinator):
    """Coordinator that handles Israel school holiday data.

    This coordinator:
    - Loads holiday data from a local JSON file.
    - Optionally fetches updated data from a remote API.
    - Saves fetched data locally for caching.
    - Determines current vacation status for elementary and high school.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            entry: The configuration entry for this integration.
        """
        self.hass = hass
        self.entry = entry

        self.update_interval_hours = entry.options.get(
            CONF_UPDATE_INTERVAL,
            entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=self.update_interval_hours),
        )

        self.config_path = hass.config.path(f"custom_components/{DOMAIN}/")
        self._school_data: List[Dict[str, Any]] = []
        self._last_update: Optional[datetime] = None

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
        """Fetch and return the latest structured holiday data.

        This method:
        - Loads local cached data if available.
        - Fetches updated data from the remote API if required.
        - Calculates the current vacation status.

        Returns:
            A dictionary containing:
            - elementary_vacation (bool)
            - high_vacation (bool)
            - summary (str)
            - last_update (str, ISO format)
            - raw_data (list)
        """
        try:
            _LOGGER.debug("Starting _async_update_data. Current _school_data: %s", self._school_data)
            if not self._school_data:
                _LOGGER.debug("_school_data is empty, loading local data.")
                await self._load_local_data()
                _LOGGER.debug("After _load_local_data, _school_data: %s", self._school_data)

            if self._should_update_data():
                _LOGGER.debug("Should update data, fetching remote data.")
                await self._fetch_remote_data()
                _LOGGER.debug("After _fetch_remote_data, _school_data: %s", self._school_data)

            status = await self._calculate_status()
            _LOGGER.info("Current school status: %s", status)
            return {
                "elementary_vacation": status.get("elementary_vacation", False),
                "high_vacation": status.get("high_vacation", False),
                "summary": status.get("summary", HEBREW_TEXTS["school_day"]),
                "last_update": self._last_update.isoformat() if self._last_update else None,
                "raw_data": self._school_data
            }

        except Exception as err:
            import traceback
            _LOGGER.error("Error updating school holidays data: %s\n%s", err, traceback.format_exc())
            _LOGGER.error("_school_data at error: %s", self._school_data)
            return {
                "elementary_vacation": False,
                "high_vacation": False,
                "summary": HEBREW_TEXTS["school_day"],
                "last_update": None,
                "raw_data": self._school_data
            }

    async def _load_local_data(self) -> None:
        """Load holiday data from the local cache file."""
        file_path = f"{self.config_path}{DATA_FILE}"
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                saved = json.loads(await file.read())
                _LOGGER.debug("Loaded raw local data type: %s, repr: %r", type(saved), saved)
                if isinstance(saved, list):
                    self._school_data = saved
                    self._last_update = None
                elif isinstance(saved, dict):
                    self._school_data = saved.get("data", [])
                    last_update_str = saved.get("last_update")
                    if last_update_str:
                        self._last_update = datetime.fromisoformat(last_update_str)
                else:
                    _LOGGER.warning("Unexpected local data format: %s", type(saved))
                _LOGGER.debug("Loaded school data from local file (%s): %s", file_path, self._school_data)
        except FileNotFoundError:
            _LOGGER.warning("No local data file found.")
        except json.JSONDecodeError as err:
            _LOGGER.warning("Invalid local data format: %s", err)

    async def _save_local_data(self) -> None:
        """Save the current holiday data to the local cache file."""
        file_path = f"{self.config_path}{DATA_FILE}"
        try:
            async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
                saved = {
                    "data": self._school_data,
                    "last_update": self._last_update.isoformat() if self._last_update else None
                }
                await file.write(json.dumps(saved, ensure_ascii=False, indent=2, sort_keys=True))
                _LOGGER.debug("Saved school data to local file (%s)", file_path)
        except Exception as err:
            _LOGGER.warning("Could not save local data: %s", err)

    async def _fetch_remote_data(self) -> None:
        """Fetch updated holiday data from the remote API."""
        _LOGGER.debug("Fetching school data from API: %s", DATA_URL)
        session = async_get_clientsession(self.hass)
        async with session.get(DATA_URL, timeout=30) as response:
            if response.status != 200:
                raise ClientError(f"HTTP {response.status}")
            self._school_data = json.loads(await response.text())
            self._last_update = dt_util.utcnow()
            await self._save_local_data()
            _LOGGER.info("Successfully fetched school data from API.")

    def _should_update_data(self) -> bool:
        """Return True if it's time to fetch fresh data from the API."""
        if not self._last_update:
            return True
        time_diff = dt_util.utcnow() - self._last_update
        return time_diff.total_seconds() > (self.update_interval_hours * 3600)

    async def _calculate_status(self) -> Dict[str, Any]:
        """Determine the current vacation status for today.

        Returns:
            A dictionary with keys:
            - elementary_vacation (bool)
            - high_vacation (bool)
            - summary (str)
        """
        today = date.today()
        weekday = today.isoweekday()

        if weekday == 6:
            return {
                "elementary_vacation": True,
                "high_vacation": True,
                "summary": HEBREW_TEXTS["sabbath"]
            }

        if weekday == 5 and self.friday_high_enabled:
            return {
                "elementary_vacation": False,
                "high_vacation": True,
                "summary": HEBREW_TEXTS["no_classes_high"]
            }

        for vacation_data in self._school_data:
            if self._is_date_in_vacation(today, vacation_data):
                if "HIGH" in vacation_data:
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

        return {
            "elementary_vacation": False,
            "high_vacation": False,
            "summary": HEBREW_TEXTS["school_day"]
        }

    def _is_date_in_vacation(self, check_date: date, vacation_data: Dict[str, Any]) -> bool:
        """Check if a given date falls within the specified vacation period.

        Args:
            check_date: The date to check.
            vacation_data: A dictionary containing:
                START (str, 'YYYY-MM-DD'),
                END (str, 'YYYY-MM-DD'),
                SUMMARY (optional str).

        Returns:
            True if check_date is within the vacation period, else False.
        """
        try:
            start_date = datetime.strptime(str(vacation_data["START"]), "%Y-%m-%d").date()
            end_date = datetime.strptime(str(vacation_data["END"]), "%Y-%m-%d").date()
            return start_date <= check_date <= end_date
        except (KeyError, ValueError) as err:
            _LOGGER.warning("Invalid vacation data format: %s", err)
            return False
