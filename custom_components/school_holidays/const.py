"""Constants for the Israel School Holidays integration."""

DOMAIN = "school_holidays"
VERSION = "3.1.0"

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
DEFAULT_LANGUAGE = "he"

# Language options
LANGUAGE_OPTIONS = {
    "he": "עברית",
    "en": "English"
}

# Holidays data (static)
HOLIDAYS_DATA = [
    {"START": "2025-07-01", "END": "2025-08-31", "SUMMARY": "חופשת קיץ"},
    {"START": "2025-09-22", "END": "2025-09-24", "SUMMARY": "ראש השנה"},
    {"START": "2025-10-01", "END": "2025-10-02", "SUMMARY": "יום הכיפורים"},
    {"START": "2025-10-03", "END": "2025-10-05", "SUMMARY": "ימי חופשה בין יום הכיפורים לחג סוכות"},
    {"START": "2025-10-06", "END": "2025-10-14", "SUMMARY": "חג סוכות"},
    {
        "START": "2025-10-15",
        "END": "2025-10-15",
        "HIGH": "True",
        "SUMMARY": "אסרו חג סוכות הוא יום לימודים בגני הילדים, בתי הספר היסודיים וחטיבות הביניים ויום חופש בחטיבות העליונות ובתיכונים."
    },
    {"START": "2025-12-16", "END": "2025-12-22", "SUMMARY": "חג החנוכה"},
    {"START": "2026-03-03", "END": "2026-03-04", "SUMMARY": "חופשת חג פורים"},
    {"START": "2026-03-24", "END": "2026-04-08", "SUMMARY": "חופשת חג הפסח"},
    {"START": "2026-04-22", "END": "2026-04-22", "SUMMARY": "יום העצמאות"},
    {
        "START": "2026-05-05",
        "END": "2026-05-05",
        "HIGH": "True",
        "SUMMARY": "ל\"ג בעומר הוא יום לימודים בגני הילדים, בתי הספר היסודיים וחטיבות הביניים, ויום חופש בחטיבות העליונות ובתיכונים (כיתות י'-יב')"
    },
    {"START": "2026-05-21", "END": "2026-05-22", "SUMMARY": "חג השבועות"},
    {"START": "2026-06-19", "END": "2026-06-30", "SUMMARY": "חופשת קיץ תיכון", "HIGH": "True"},
    {"START": "2026-07-01", "END": "2026-08-31", "SUMMARY": "חופשת קיץ"},
]

# Entity names by language
ENTITY_NAMES = {
    "he": {
        "summary": "סטטוס חופשת בתי ספר",
        "elementary_vacation": "חופש בית ספר יסודי",
        "high_vacation": "חופש בית ספר על יסודי",
        "device_name": "חופשות בתי ספר בישראל",
    },
    "en": {
        "summary": "School Status",
        "elementary_vacation": "Elementary School Vacation",
        "high_vacation": "High School Vacation",
        "device_name": "Israel School Holidays",
    },
}

# Sensor types (icons only, names will be dynamic)
SENSOR_TYPES = {
    "summary": {"icon": "mdi:school", "device_class": None}
}

BINARY_SENSOR_TYPES = {
    "elementary_vacation": {"icon": "mdi:school", "device_class": None},
    "high_vacation": {"icon": "mdi:school-outline", "device_class": None},
}

# Status text constants
HEBREW_TEXTS = {
    "big_vacation_high": "חופש גדול - על יסודי",
    "sabbath": "יום שבת",
    "no_classes_high": "אין לימודים - על יסודי",
    "school_day": "יום לימודים",
    "error": "שגיאה",
}

# Error messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_DATA = "invalid_data"
ERROR_UNKNOWN = "unknown"
