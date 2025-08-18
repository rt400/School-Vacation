# Israel School Holidays - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/rt400/School-Vacation)](https://github.com/rt400/School-Vacation/releases)
[![License](https://img.shields.io/github/license/rt400/School-Vacation)](LICENSE)

&#x20;&#x20;

A Home Assistant custom integration that tracks Israeli school vacation periods for both elementary and high schools.

---

## Features

- 🏫 **Separate tracking** for elementary and high school vacations
- 📅 **Real-time status** with automatic updates from official data
- 🌐 **Bilingual support** - Hebrew and English status messages
- ⚙️ **Configurable options** through the UI
- 🔄 **Automatic data updates** with customizable intervals
- 📱 **HACS compatible** for easy installation and updates

---

## Why This Integration?

In Israel, school vacation periods differ between elementary and high schools. For example:

- High schools typically end on June 22nd
- Elementary schools end on July 1st
- High schools often have no classes on Fridays

This integration allows you to create separate automations for each school type and get accurate vacation information.

---

## Installation

### Important for Users of the Old YAML Version

If you have the old version installed via YAML, you **must remove your old configuration and restart Home Assistant** before installing the new integration. Failing to do so may cause conflicts.

### HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots in the top right corner → **Custom repositories**
4. Add this repository URL: `https://github.com/rt400/School-Vacation`
5. Select **Integration** as the category
6. Click **Add**
7. Find **Israel School Holidays** in HACS and install it
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub releases](https://github.com/rt400/School-Vacation/releases)
2. Extract the files to your `custom_components/school_holidays/` directory
3. Restart Home Assistant

---

## Configuration

### Adding the Integration

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **Israel School Holidays**
4. Configure your preferences:

| Option             | Description                                   | Default |
| ------------------ | --------------------------------------------- | ------- |
| Display Language   | Language for status messages (Hebrew/English) | Hebrew  |
| Elementary School  | Track elementary school vacations             | Enabled |
| High School        | Track high school vacations                   | Enabled |
| Friday High School | High schools have no classes on Fridays       | Enabled |
| Update Interval    | How often to check for data updates (hours)   | 24      |

---

## Entities Created

### Sensors

- **`sensor.school_status`** – Current school status summary  
  States: `"School Day"`, `"Sabbath"`, `"Summer Vacation"`, etc.

### Binary Sensors

- **`binary_sensor.elementary_school_vacation`** – Elementary school vacation status  
  - `on`: Vacation day  
  - `off`: School day

- **`binary_sensor.high_school_vacation`** – High school vacation status  
  - `on`: Vacation day  
  - `off`: School day

---

## Usage Examples

### Basic Automation - School Mode

```yaml
automation:
  - id: set_school_mode_off
    alias: "Turn Off School Mode During Vacation"
    trigger:
      - platform: state
        entity_id: binary_sensor.elementary_school_vacation
        to: 'on'
    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.school_mode

  - id: set_school_mode_on
    alias: "Turn On School Mode During School Days"
    trigger:
      - platform: state
        entity_id: binary_sensor.elementary_school_vacation
        to: 'off'
    condition:
      - condition: time
        weekday:
          - sun
          - mon
          - tue
          - wed
          - thu
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.school_mode
```

### Input Boolean Helper

```yaml
input_boolean:
  school_mode:
    name: "School Mode"
    icon: mdi:school
```

### Lovelace Card Example

```yaml
type: entities
title: "School Status"
entities:
  - entity: sensor.school_status
    name: "Current Status"
  - entity: binary_sensor.elementary_school_vacation
    name: "Elementary Vacation"
  - entity: binary_sensor.high_school_vacation
    name: "High School Vacation"
  - entity: input_boolean.school_mode
    name: "School Mode"
```

### Template Examples

```yaml
# Check if any school is on vacation
template:
  - binary_sensor:
      - name: "Any School Vacation"
        state: >
          {{ is_state('binary_sensor.elementary_school_vacation', 'on') or
             is_state('binary_sensor.high_school_vacation', 'on') }}

# Get vacation status in Hebrew
  - sensor:
      - name: "School Status Hebrew"
        state: >
          {% if is_state('binary_sensor.elementary_school_vacation', 'on') %}
            חופש
          {% else %}
            לימודים
          {% endif %}
```

---

## Advanced Configuration

### Notifications

```yaml
automation:
  - id: vacation_starts_notification
    alias: "Notify When Vacation Starts"
    trigger:
      - platform: state
        entity_id: binary_sensor.elementary_school_vacation
        from: 'off'
        to: 'on'
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "School Vacation Started! 🎉"
          message: "{{ states('sensor.school_status') }}"
```

### Conditional Automations

```yaml
automation:
  - id: morning_routine_school_day
    alias: "Morning Routine - School Day"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.elementary_school_vacation
        state: 'off'
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - sun
    action:
      - service: script.school_morning_routine
```

---

## Troubleshooting

### Common Issues

1. **Integration not appearing**: Restart Home Assistant after installation
2. **No data**: Check your internet connection
3. **Entities not updating**: Check the update interval in integration options

### Debug Logging

Add this to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.school_holidays: debug
```

---

## Data Source

This integration uses official Israeli school vacation data maintained at:\
[https://github.com/rt400/School-Vacation/blob/master/data.json](https://github.com/rt400/School-Vacation/blob/master/data.json)

Data is automatically updated and cached locally.

---

## Contributing

Contributions are welcome! Submit a Pull Request on GitHub.

---

## License

MIT License – see [LICENSE](LICENSE) file.

---

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rt400/School-Vacation/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/rt400/School-Vacation/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/rt400/School-Vacation/wiki)

---

## Changelog

**Version 3.0.0**

- Complete rewrite as a modern Home Assistant integration
- Added HACS support
- UI-based configuration with Config Flow
- Bilingual support (Hebrew/English)
- Improved reliability with local data caching
- Separate binary sensors for each school type

---

**Made with ❤️ for the Israeli Home Assistant community By Yuval Mejahez**

