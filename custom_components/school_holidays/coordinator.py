"""Data coordinator for Israel School Holidays."""
import asyncio
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import aiofiles
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

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
    """Class to manage fetching school holidays data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        update_interval_hours = entry.options.get(
            CONF_UPDATE_INTERVAL,
            entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_interval_hours),
        )
        self.config_path = hass.config.path(f"custom_components/{DOMAIN}/")
        self._school_data: List[Dict[str, Any]] = []
        self._last_update: Optional[datetime] = None

    @property
    def elementary_enabled(self) -> bool:
        """Check if elementary school tracking is enabled."""
        return self.entry.options.get(
            CONF_ELEMENTARY_SCHOOL,
            self.entry.data.get(CONF_ELEMENTARY_SCHOOL, True)
        )

    @property
    def high_enabled(self) -> bool:
        """Check if high school tracking is enabled."""
        return self.entry.options.get(
            CONF_HIGH_SCHOOL,
            self.entry.data.get(CONF_HIGH_SCHOOL, True)
        )

    @property
    def friday_high_enabled(self) -> bool:
        """Check if Friday high school vacation is enabled."""
        return self.entry.options.get(
            CONF_FRIDAY_HIGH_SCHOOL,
            self.entry.data.get(CONF_FRIDAY_HIGH_SCHOOL, True)
        )

    @property
    def language(self) -> str:
        """Get selected language."""
        return self.entry.options.get(
            CONF_LANGUAGE,
            self.entry.data.get(CONF_LANGUAGE, "he")
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API or local file."""
        try:
            # Try to load from local file first
            if not self._school_data:
                await self._load_local_data()
            
            # If no local data or data is old, fetch from API
            if not self._school_data or self._should_update_data():
                await self._fetch_remote_data()
            
            # Calculate current status
            status = await self._calculate_status()
            
            return {
                "elementary_vacation": status["elementary_vacation"],
                "high_vacation": status["high_vacation"],
                "summary": status["summary"],
                "last_update": self._last_update,
            }
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _load_local_data(self) -> None:
        """Load school data from local file."""
        try:
            file_path = f"{self.config_path}{DATA_FILE}"
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                self._school_data = json.loads(content)
                _LOGGER.debug("Loaded school data from local file")
        except (FileNotFoundError, json.JSONDecodeError) as err:
            _LOGGER.debug(f"Could not load local data: {err}")
            self._school_data = []

    async def _fetch_remote_data(self) -> None:
        """Fetch school data from remote API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DATA_URL, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        self._school_data = json.loads(content)
                        await self._save_local_data()
                        self._last_update = dt_util.utcnow()
                        _LOGGER.info("Successfully fetched school data from API")
                    else:
                        raise aiohttp.ClientError(f"HTTP {response.status}")
        except Exception as err:
            _LOGGER.error(f"Error fetching remote data: {err}")
            if not self._school_data:
                raise UpdateFailed("No data available")

    async def _save_local_data(self) -> None:
        """Save school data to local file."""
        try:
            file_path = f"{self.config_path}{DATA_FILE}"
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                content = json.dumps(
                    self._school_data,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True
                )
                await file.write(content)
                _LOGGER.debug("Saved school data to local file")
        except Exception as err:
            _LOGGER.warning(f"Could not save local data: {err}")

    def _should_update_data(self) -> bool:
        """Check if data should be updated."""
        if not self._last_update:
            return True
        
        update_interval_hours = self.entry.options.get(
            CONF_UPDATE_INTERVAL,
            self.entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        
        time_diff = dt_util.utcnow() - self._last_update
        return time_diff.total_seconds() > (update_interval_hours * 3600)

    async def _calculate_status(self) -> Dict[str, Any]:
        """Calculate current vacation status."""
        today = date.today()
        weekday = today.isoweekday()
        
        # Saturday is always vacation
        if weekday == 6:
            return {
                "elementary_vacation": True,
                "high_vacation": True,
                "summary": HEBREW_TEXTS["sabbath"]
            }
        
        # Friday - only high school vacation (if configured)
        if weekday == 5 and self.friday_high_enabled:
            return {
                "elementary_vacation": False,
                "high_vacation": True,
                "summary": HEBREW_TEXTS["no_classes_high"]
            }
        
        # Check vacation periods
        for vacation_data in self._school_data:
            if self._is_date_in_vacation(today, vacation_data):
                if "HIGH" in vacation_data:
                    # High school only vacation
                    return {
                        "elementary_vacation": False,
                        "high_vacation": True,
                        "summary": HEBREW_TEXTS["big_vacation_high"]
                    }
                else:
                    # General vacation (both schools) - keep original SUMMARY from data
                    return {
                        "elementary_vacation": True,
                        "high_vacation": True,
                        "summary": vacation_data.get("SUMMARY", "חופש")
                    }
        
        # Regular school day
        return {
            "elementary_vacation": False,
            "high_vacation": False,
            "summary": HEBREW_TEXTS["school_day"]
        }

    def _is_date_in_vacation(self, check_date: date, vacation_data: Dict[str, Any]) -> bool:
        """Check if a date falls within a vacation period."""
        try:
            start_date = datetime.strptime(str(vacation_data['START']), '%Y%m%d').date()
            end_date = datetime.strptime(str(vacation_data['END']), '%Y%m%d').date()
            return start_date <= check_date <= end_date
        except (KeyError, ValueError) as err:
            _LOGGER.warning(f"Invalid vacation data format: {err}")
            return False
