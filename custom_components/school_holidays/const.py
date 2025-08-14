"""Constants for the Israel School Holidays integration."""

DOMAIN = "school_holidays"
VERSION = "3.0.1"

# Configuration keys
CONF_ELEMENTARY_SCHOOL = "elementary_school"
CONF_HIGH_SCHOOL = "high_school"
CONF_FRIDAY_HIGH_SCHOOL = "friday_high_school"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_LANGUAGE = "language"

# Default values
DEFAULT_ELEMENTARY_SCHOOL = True
DEFAULT_HIGH_SCHOOL = True
DEFAULT_FRIDAY_HIGH_SCHOOL = True
DEFAULT_UPDATE_INTERVAL = 24
DEFAULT_LANGUAGE = "he"

# Language options
LANGUAGE_OPTIONS = {
    "he": "עברית",
    "en": "English"
}

# Data source
DATA_URL = "https://raw.githubusercontent.com/rt400/School-Vacation/master/data.json"
DATA_FILE = "school_data.json"

# Entity names by language
ENTITY_NAMES = {
    "he": {
        "summary": "סטטוס חופשת בתי ספר",
        "elementary_vacation": "חופש בית ספר יסודי",
        "high_vacation": "חופש בית ספר על יסודי",
        "device_name": "חופשות בתי ספר בישראל"
    },
    "en": {
        "summary": "School Status",
        "elementary_vacation": "Elementary School Vacation",
        "high_vacation": "High School Vacation",
        "device_name": "Israel School Holidays"
    }
}

# Sensor types (icons only, names will be dynamic)
SENSOR_TYPES = {
    "summary": {
        "icon": "mdi:school",
        "device_class": None,
    }
}

BINARY_SENSOR_TYPES = {
    "elementary_vacation": {
        "icon": "mdi:school",
        "device_class": None,
    },
    "high_vacation": {
        "icon": "mdi:school-outline",
        "device_class": None,
    }
}

# Status text constants (these come from DATA file, keep as is)
HEBREW_TEXTS = {
    "big_vacation_high": "חופש גדול - על יסודי",
    "sabbath": "יום שבת",
    "no_classes_high": "אין לימודים - על יסודי", 
    "school_day": "יום לימודים",
    "error": "שגיאה"
}

# Error messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_DATA = "invalid_data"
ERROR_UNKNOWN = "unknown"
