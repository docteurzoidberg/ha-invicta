"""The Invicta integration."""
from __future__ import annotations

from datetime import timedelta

from aiohttp import ClientConnectionError
from async_timeout import timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .api import InvictaApiData, InvictaApiClient


class InvictaDataUpdateCoordinator(DataUpdateCoordinator[InvictaApiData]):
    """Class to manage the polling of the fireplace API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: InvictaApiClient,
    ) -> None:
        """Initialize the Coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=1),
        )
        self._api = api

    async def _async_update_data(self) -> InvictaApiData:

        if not self._api.is_polling_in_background:
            LOGGER.info("Starting Invicta Background Polling Loop")
            await self._api.start_background_polling()

            # Don't return uninitialized poll data
            async with timeout(15):
                try:
                    await self._api.poll()
                except (ConnectionError, ClientConnectionError) as exception:
                    raise UpdateFailed from exception

        LOGGER.debug("Failure Count %d", self._api.failed_poll_attempts)
        if self._api.failed_poll_attempts > 10:
            LOGGER.debug("Too many polling errors - raising exception")
            raise UpdateFailed

        return self._api.data

    @property
    def read_api(self) -> InvictaApiClient:
        """Return the Status API pointer."""
        return self._api

    @property
    def control_api(self) -> InvictaApiClient:
        """Return the control API."""
        return self._api

    @property
    def device_info(self) -> DeviceInfo:
        # DRZOID: how to get the sw version?
        """Return the device info."""
        return DeviceInfo(
            manufacturer="Invicta",
            model="Fontica 8",
            name=self.read_api.data.name,
            identifiers={("Invicta", f"{self.read_api.data.productmodel}]")},
            sw_version="1.0",
            configuration_url=f"http://{self._api.stove_ip}/",
        )
