"""Flame height number sensors."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER, MAX_POWER, MIN_POWER
from .coordinator import InvictaDataUpdateCoordinator
from .entity import InvictaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up power"""
    coordinator: InvictaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    description = NumberEntityDescription(
        key="power",
        name="Power Control",
        icon="mdi:arrow-expand-vertical",
    )

    async_add_entities(
        [InvictaPowerControlEntity(coordinator=coordinator, description=description)]
    )


@dataclass
class InvictaPowerControlEntity(InvictaEntity, NumberEntity):
    """Power control entity."""

    _attr_native_max_value: float = MAX_POWER
    _attr_native_min_value: float = MIN_POWER
    _attr_native_step: float = 1
    _attr_mode: NumberMode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: InvictaDataUpdateCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize Power Sensor."""
        super().__init__(coordinator, description)

    @property
    def native_value(self) -> float | None:
        """Return the current power number value."""
        # TODO DRZOID: check possible values
        value = self.coordinator.read_api.data.power_set
        return value

    async def async_set_native_value(self, value: float) -> None:
        """Slider change."""
        # TODO DRZOID: check possible values
        value_to_send: int = int(value)
        LOGGER.debug(
            "%s set power to %d with raw value %s",
            self._attr_name,
            value,
            value_to_send,
        )
        await self.coordinator.control_api.set_power(value=value_to_send)
        await self.coordinator.async_refresh()
