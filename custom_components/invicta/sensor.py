"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import InvictaDataUpdateCoordinator
from .entity import InvictaEntity
from .api import InvictaApiData


@dataclass
class InvictaSensorRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[InvictaApiData], float | int | str | datetime | None]


@dataclass
class InvictaSensorEntityDescription(
    SensorEntityDescription,
    InvictaSensorRequiredKeysMixin,
):
    """Describes a sensor entity."""


Invicta_SENSORS: tuple[InvictaSensorEntityDescription, ...] = (
    InvictaSensorEntityDescription(
        key="power_set",
        icon="mdi:fire-circle",
        name="Power",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.power_set,
    ),
    InvictaSensorEntityDescription(
        key="temperature_set",
        name="Set Temperature",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value_fn=lambda data: data.temperature_set,
    ),
    InvictaSensorEntityDescription(
        key="temperature_read",
        name="Read Temperature",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value_fn=lambda data: data.temperature_read,
    ),
    InvictaSensorEntityDescription(
        key="status",
        name="Status",
        value_fn=lambda data: data.status.get_message(),
    ),
    InvictaSensorEntityDescription(
        key="alarms",
        name="Alarms",
        value_fn=lambda data: "TODO",
    ),
    InvictaSensorEntityDescription(
        key="name",
        name="Name",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.name,
    ),
    InvictaSensorEntityDescription(
        key="host",
        name="Host",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.host,
        entity_registry_enabled_default=False,
    ),
    InvictaSensorEntityDescription(
        key="wifi_signal",
        name="Wifi Signal Strength",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.signal,
        entity_registry_enabled_default=False,
    ),
    InvictaSensorEntityDescription(
        key="product_model",
        name="Product model",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.model.get_message(),
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Define setup entry call."""

    coordinator: InvictaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        InvictaSensor(coordinator=coordinator, description=description)
        for description in Invicta_SENSORS
    )


class InvictaSensor(InvictaEntity, SensorEntity):
    """Extends InvictaEntity with Sensor specific logic."""

    entity_description: InvictaSensorEntityDescription

    @property
    def native_value(self) -> int | str | datetime | None:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator.read_api.data)
