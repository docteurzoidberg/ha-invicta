"""Config flow for Invicta integration."""
from __future__ import annotations
from typing import Any
import voluptuous as vol
from aiohttp import ClientConnectionError

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, LOGGER, CONF_HOST
from .api import InvictaApiClient

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})

MANUAL_ENTRY_STRING = "IP Address"  # Simplified so it does not have to be translated


async def validate_host_input(host: str) -> str:
    """Validate the user input allows us to connect."""
    LOGGER.debug("Instantiating Invicta Winet-Control API with host: [%s]", host)
    api = InvictaApiClient(session=None, host=host)
    await api.poll()
    productmodel = api.data.model.get_message()
    LOGGER.debug("Found a stove: %s", productmodel)
    # Return the serial number which will be used to calculate a unique ID for the device/sensors
    return productmodel


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Invicta."""

    VERSION = 1

    def __init__(self):
        """Initialize the Config Flow Handler."""
        self._host: str = ""
        self._productmodel: str = ""

    # ENTRYPOINT
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Start the user flow (config step entrypoint)"""

        # TODO: Launch stove discovery
        # await self._find_fireplaces()
        LOGGER.debug("STEP: user")
        LOGGER.debug("Running Step: manual_device_entry")
        return await self.async_step_manual_device_entry()

    async def async_step_manual_device_entry(self, user_input=None) -> FlowResult:
        """Handle manual input of local IP configuration."""
        LOGGER.debug("STEP: manual_device_entry")
        errors = {}
        self._host = user_input.get(CONF_HOST) if user_input else None
        if user_input is not None:
            try:
                return await self._async_validate_ip_and_continue(self._host)
            except (ConnectionError, ClientConnectionError):
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="manual_device_entry",
            errors=errors,
            data_schema=vol.Schema({vol.Required(CONF_HOST, default=self._host): str}),
        )

    async def _async_validate_ip_and_continue(self, host: str) -> FlowResult:
        """Validate local config and continue."""
        self._async_abort_entries_match({CONF_HOST: host})
        self._productmodel = await validate_host_input(host)
        await self.async_set_unique_id(self._productmodel, raise_on_progress=False)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})
        # Store current data and jump to next stage
        self._host = host

        return self.async_create_entry(title=self._host, data={CONF_HOST: host})
        # return self.async_show_form(step_id="api_config")
