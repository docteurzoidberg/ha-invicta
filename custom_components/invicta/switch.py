"""Define switch func."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import InvictaDataUpdateCoordinator
from .entity import InvictaEntity
from .api import InvictaApiClient, InvictaApiData


@dataclass()
class InvictaSwitchRequiredKeysMixin:
    """Mixin for required keys."""

    on_fn: Callable[[InvictaApiClient], Awaitable]
    off_fn: Callable[[InvictaApiClient], Awaitable]
    value_fn: Callable[[InvictaApiData], bool]


@dataclass
class InvictaSwitchEntityDescription(
    SwitchEntityDescription, InvictaSwitchRequiredKeysMixin
):
    """Describes a switch entity."""


INVICTA_SWITCHES: tuple[InvictaSwitchEntityDescription, ...] = (
    InvictaSwitchEntityDescription(
        key="on_off",
        name="Turn On",
        on_fn=lambda control_api: control_api.turn_on(),
        off_fn=lambda control_api: control_api.turn_off(),
        value_fn=lambda data: data.is_on,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure switch entities."""
    coordinator: InvictaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        InvictaSwitch(coordinator=coordinator, description=description)
        for description in INVICTA_SWITCHES
    )


class InvictaSwitch(InvictaEntity, SwitchEntity):
    """Define an Invicta Switch."""

    entity_description: InvictaSwitchEntityDescription

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self.entity_description.on_fn(self.coordinator.control_api)
        await self.async_update_ha_state(force_refresh=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self.entity_description.off_fn(self.coordinator.control_api)
        await self.async_update_ha_state(force_refresh=True)

    @property
    def is_on(self) -> bool | None:
        """Return the on state."""
        return self.entity_description.value_fn(self.coordinator.read_api.data)
