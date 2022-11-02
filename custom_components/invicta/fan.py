"""Fan definition for Intellifire."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import math
from typing import Any

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
    int_states_in_range,
)

from .const import DOMAIN, LOGGER, MIN_FAN_SPEED, MAX_FAN_SPEED
from .coordinator import InvictaDataUpdateCoordinator
from .entity import InvictaEntity
from .api import InvictaApiData, InvictaApiClient


@dataclass
class InvictaFanRequiredKeysMixin:
    """Required keys for fan entity."""

    set_fn: Callable[[InvictaApiClient, int], Awaitable]
    value_fn: Callable[[InvictaApiData], bool]
    speed_range: tuple[int, int]


@dataclass
class InvictaFanEntityDescription(FanEntityDescription, InvictaFanRequiredKeysMixin):
    """Describes a fan entity."""


INVICTA_FANS: tuple[InvictaFanEntityDescription, ...] = (
    InvictaFanEntityDescription(
        key="fan",
        name="Room ventilation Fan",
        has_entity_name=True,
        set_fn=lambda control_api, speed: control_api.set_fan_speed(value=speed),
        value_fn=lambda data: True,
        speed_range=(MIN_FAN_SPEED, MAX_FAN_SPEED),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fan"""
    coordinator: InvictaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        InvictaFan(coordinator=coordinator, description=description)
        for description in INVICTA_FANS
    )


class InvictaFan(InvictaEntity, FanEntity):
    """This is Fan entity for the stove."""

    entity_description: InvictaFanEntityDescription
    _attr_supported_features = FanEntityFeature.SET_SPEED

    @property
    def is_on(self) -> bool:
        """Return on or off."""
        return self.entity_description.value_fn(
            self.coordinator.read_api.data.is_heating
        )

    @property
    def percentage(self) -> int | None:
        """Return fan percentage."""

        return ranged_value_to_percentage(
            self.entity_description.speed_range,
            self.coordinator.read_api.data.fan_speed,
        )

    @property
    def speed_count(self) -> int:
        """Count of supported speeds."""
        return int_states_in_range(self.entity_description.speed_range)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        # Calculate percentage steps
        LOGGER.debug("Setting Fan Speed %s", percentage)

        int_value = math.ceil(
            percentage_to_ranged_value(self.entity_description.speed_range, percentage)
        )
        LOGGER.debug("Setting Fan value %d", int_value)
        await self.entity_description.set_fn(self.coordinator.control_api, int_value)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if percentage:
            int_value = math.ceil(
                percentage_to_ranged_value(
                    self.entity_description.speed_range, percentage
                )
            )
        else:
            int_value = 1
        await self.entity_description.set_fn(self.coordinator.control_api, int_value)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan. do nothing since the fan cannot be turned off"""
        await self.entity_description.set_fn(self.coordinator.control_api, 0)
        await self.coordinator.async_request_refresh()
