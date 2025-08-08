Israel School Holidays - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/rt400/School-Vacation.svg)](https://github.com/rt400/School-Vacation/releases)
[![License](https://img.shields.io/github/license/rt400/School-Vacation.svg)](LICENSE)


A Home Assistant custom integration that tracks Israeli school vacation periods for both elementary and high schools.


Features:

• 🏫 **Separate tracking** for elementary and high school vacations

• 📅 **Real-time status** with automatic updates from official data

• 🌐 **Bilingual support** - Hebrew and English status messages

• ⚙️ **Configurable options** through the UI

• 🔄 **Automatic data updates** with customizable intervals

• 📱 **HACS compatible** for easy installation and updates


Why This Integration?

In Israel, school vacation periods differ between elementary and high schools. For example:

• High schools typically end on June 22nd

• Elementary schools end on July 1st

• High schools often have no classes on Fridays



This integration allows you to create separate automations for each school type and get accurate vacation information.


Installation

HACS Installation (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/rt400/School-Vacation`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Israel School Holidays" in HACS and install it
9. Restart Home Assistant


Manual Installation
1. Download the latest release from [GitHub releases](https://github.com/rt400/School-Vacation/releases)
2. Extract the files to your `custom_components/school_holidays/` directory
3. Restart Home Assistant


Configuration

Adding the Integration
1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Israel School Holidays"**
4. Configure your preferences:
- **Display Language**: Choose Hebrew or English for status messages
- **Elementary School**: Enable tracking for elementary school vacations
- **High School**: Enable tracking for high school vacations  
- **Friday High School**: High schools have no classes on Fridays
- **Update Interval**: How often to check for data updates (1-168 hours)


Configuration Options

Option	Description	Default
`Display Language`	Language for status messages (Hebrew/English)	Hebrew
`Elementary School`	Track elementary school vacations	Enabled
`High School`	Track high school vacations	Enabled
`Friday High School`	No high school classes on Fridays	Enabled
`Update Interval`	Data update frequency in hours	24 hours

Entities Created

The integration creates the following entities:


Sensors
• **`sensor.school_status`** - Current school status summary
- States: "School Day", "Sabbath", "Summer Vacation", etc.


Binary Sensors
• **`binary_sensor.elementary_school_vacation`** - Elementary school vacation status
- `on`: Vacation day
- `off`: School day

• **`binary_sensor.high_school_vacation`** - High school vacation status
- `on`: Vacation day  
- `off`: School day


Usage Examples

Basic Automation - School Mode

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


Input Boolean Helper

input_boolean:
  school_mode:
    name: "School Mode"
    icon: mdi:school


Lovelace Card Example

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


Template Examples

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


Advanced Configuration

Notifications

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


Conditional Automations

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


Troubleshooting

Common Issues
1. **Integration not appearing**: Make sure you've restarted Home Assistant after installation
2. **No data**: Check your internet connection - the integration fetches data from GitHub
3. **Entities not updating**: Check the update interval in integration options


Debug Logging

Add this to your `configuration.yaml` for debug information:


logger:
  logs:
    custom_components.school_holidays: debug


Data Source

This integration uses official Israeli school vacation data maintained at:
https://github.com/rt400/School-Vacation/blob/master/data.json


The data is automatically updated and cached locally for reliability.


Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


Support
• 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rt400/School-Vacation/issues)
• 💡 **Feature Requests**: [GitHub Issues](https://github.com/rt400/School-Vacation/issues)
• 📖 **Documentation**: [GitHub Wiki](https://github.com/rt400/School-Vacation/wiki)


Changelog

Version 3.0.0
• Complete rewrite as a modern Home Assistant integration
• Added HACS support
• UI-based configuration with Config Flow
• Bilingual support (Hebrew/English)
• Improved reliability with local data caching
• Separate binary sensors for each school type


⸻


**Made with ❤️ for the Israeli Home Assistant community**
