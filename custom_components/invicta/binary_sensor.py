"""Support for Invicta Binary Sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import InvictaDataUpdateCoordinator
from .const import DOMAIN
from .entity import InvictaEntity
from .api import InvictaApiData


@dataclass
class InvictaBinarySensorRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[InvictaApiData], bool]


@dataclass
class InvictaBinarySensorEntityDescription(
    BinarySensorEntityDescription, InvictaBinarySensorRequiredKeysMixin
):
    """Describes a binary sensor entity."""


INVICTA_BINARY_SENSORS: tuple[InvictaBinarySensorEntityDescription, ...] = (
    InvictaBinarySensorEntityDescription(
        key="on_off",
        name="Power on",
        icon="mdi:power",
        value_fn=lambda data: data.is_on,
    ),
    InvictaBinarySensorEntityDescription(
        key="heating",
        name="Heating",
        icon="mdi:fire",
        value_fn=lambda data: data.is_heating,
    ),
    InvictaBinarySensorEntityDescription(
        key="error_offline",
        name="Offline Error",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.error_offline,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_extractor_malfunction",
        name="Extractor malfunction Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_extractor_malfunction,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_failed_ignition",
        name="Failed ignition Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_failed_ignition,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_no_pellets",
        name="No pellets Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_no_pellets,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_open_pellet_compartment",
        name="Open pellet compartment Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_open_pellet_compartment,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_thermal_safety",
        name="Thermal safety Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_thermal_safety,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_smoke_overtemp",
        name="Smoke over temperature Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_smoke_overtemp,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    InvictaBinarySensorEntityDescription(
        key="alarm_smoke_probe_failure",
        name="Smoke probe failure Alarm",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_smoke_probe_failure,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Invicta On/Off Sensor."""
    coordinator: InvictaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        InvictaBinarySensor(coordinator=coordinator, description=description)
        for description in INVICTA_BINARY_SENSORS
    )


class InvictaBinarySensor(InvictaEntity, BinarySensorEntity):
    """Extends InvictaEntity with Binary Sensor specific logic."""

    entity_description: InvictaBinarySensorEntityDescription

    @property
    def is_on(self) -> bool:
        """Use this to get the correct value."""
        return self.entity_description.value_fn(self.coordinator.read_api.data)
