"""Constants for the Invicta integration."""
from __future__ import annotations
import logging
from homeassistant.const import (
    Platform,
)

# Base component constants
NAME = "Invicta Integration"
DOMAIN = "invicta"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.0"
ISSUE_URL = "https://github.com/docteurzoidberg/ha-invicta/issues"

LOGGER = logging.getLogger(__package__)

# Icons
ICON = "mdi:fire"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_HOST = "host"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_THERMOSTAT_TEMP = 21

MIN_THERMOSTAT_TEMP = 15
MAX_THERMOSTAT_TEMP = 25


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
