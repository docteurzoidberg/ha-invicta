"""Invicta Climate Entities."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import InvictaDataUpdateCoordinator
from .const import (
    DEFAULT_THERMOSTAT_TEMP,
    DOMAIN,
    LOGGER,
    MAX_THERMOSTAT_TEMP,
    MIN_THERMOSTAT_TEMP,
)
from .entity import InvictaEntity
from .api import InvictaDeviceStatus

INVICTA_CLIMATES: tuple[ClimateEntityDescription, ...] = (
    ClimateEntityDescription(key="climate", name="Thermostat"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Climate entity setup"""
    coordinator: InvictaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        InvictaClimate(
            coordinator=coordinator,
            description=description,
        )
        for description in INVICTA_CLIMATES
    )


class InvictaClimate(InvictaEntity, ClimateEntity):
    """Invicta climate entity."""

    entity_description: ClimateEntityDescription

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_min_temp = MIN_THERMOSTAT_TEMP
    _attr_max_temp = MAX_THERMOSTAT_TEMP
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_target_temperature_step = 0.5
    _attr_temperature_unit = TEMP_CELSIUS
    last_temp = DEFAULT_THERMOSTAT_TEMP

    def __init__(
        self,
        coordinator: InvictaDataUpdateCoordinator,
        description: ClimateEntityDescription,
    ) -> None:
        """Configure climate entry - and override last_temp if the thermostat is currently on."""
        super().__init__(coordinator, description)

        self.last_temp = coordinator.data.temperature_set

    @property
    def hvac_mode(self) -> str:
        """Return current hvac mode."""
        status = self.coordinator.read_api.data.status
        if status in [
            InvictaDeviceStatus.WAIT_FOR_FLAME,
            InvictaDeviceStatus.POWER_ON,
            InvictaDeviceStatus.WORK,
        ]:
            return HVACMode.HEAT
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Turn on thermostat by setting a target temperature."""
        raw_target_temp = kwargs[ATTR_TEMPERATURE]
        self.last_temp = raw_target_temp
        LOGGER.warning(
            "Setting target temp to %sc %sf",
            int(raw_target_temp),
            (raw_target_temp * 9 / 5) + 32,
        )
        await self.coordinator.control_api.set_temperature(raw_target_temp)

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return float(self.coordinator.read_api.data.temperature_read)

    @property
    def target_temperature(self) -> float:
        """Return target temperature."""
        return float(self.coordinator.read_api.data.temperature_set)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode to normal or thermostat control."""
        LOGGER.warning(
            "Setting mode to [%s] - using last temp: %s", hvac_mode, self.last_temp
        )

        if hvac_mode == HVACMode.OFF:
            return

        # hvac_mode == HVACMode.HEAT
        # 1) Set the desired target temp
        # await self.coordinator.control_api.set_thermostat_c(
        #    temp_c=self.last_temp,
        # )

        # 2) Make sure the fireplace is on!
        # if not self.coordinator.read_api.data.is_on:
        #    await self.coordinator.control_api.flame_on()
