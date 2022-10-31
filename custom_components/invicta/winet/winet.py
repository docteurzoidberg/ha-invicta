"""Winet-Control API"""
from __future__ import annotations
import logging

from json import JSONDecodeError

import aiohttp
from aiohttp import (
    ClientConnectorError,
    ClientOSError,
    ServerDisconnectedError,
)

from .model import WinetGetRegisterResult
from .const import (
    WinetRegister,
    WinetRegisterKey,
    WinetRegisterCategory,
)

LOGGER = logging.getLogger(__package__)


class WinetAPILocal:
    """Bottom level API. handle http communication with the local winet module"""

    def __init__(self, session: aiohttp.ClientSession, stove_ip: str) -> None:
        """Initialize Winet local api."""
        self._session = session
        self._stove_ip = stove_ip

    async def get_registers(
        self,
        key: WinetRegisterKey,
        category: WinetRegisterCategory = WinetRegisterCategory.NONE,
    ):
        """Poll registers"""
        async with aiohttp.ClientSession() as session:

            url = f"http://{self._stove_ip}/ajax/get-registers"
            data = {"key": key.value}

            if category != WinetRegisterCategory.NONE:
                data["category"] = str(category.value)

            headers = {
                "Access-Control-Request-Method": "POST",
                "Host": f"{self._stove_ip}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json; charset=utf-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": f"http://{self._stove_ip}",
                "Referer": f"http://{self._stove_ip}/management.html",
            }
            LOGGER.debug(f"Querying {url} with data={data}")
            try:
                async with session.post(url, data=data, headers=headers) as response:
                    try:
                        if response.status != 200:
                            LOGGER.warning(f"Error accessing {url} - {response.status}")
                            raise ConnectionError(
                                f"Communication error - Response status {response.status}"
                            )
                        try:
                            json_data = await response.json(content_type=None)
                            LOGGER.debug("Received: %s", json_data)

                            if "result" in json_data:
                                # handle an action's result
                                if json_data["result"] is False:
                                    LOGGER.warning("Api result is False")
                            else:
                                try:
                                    return WinetGetRegisterResult(**json_data)
                                except Exception:
                                    LOGGER.warning("Error parsing poll data")
                                    LOGGER.debug(f"Received: {json_data}")
                            # TODO: what about model check exceptions ?
                        except JSONDecodeError:
                            LOGGER.warning("Error decoding JSON: [%s]", response.text)

                    except ConnectionError as exc:
                        LOGGER.warning(f"Connection Error accessing {url}")
                        raise ConnectionError(
                            "ConnectionError - host not found"
                        ) from exc
            except (
                ServerDisconnectedError,
                ClientConnectorError,
                ClientOSError,
                ConnectionError,
                UnboundLocalError,
            ):
                raise ConnectionError()
            except Exception as unknown_error:
                LOGGER.error("Unhandled Exception %s", type(unknown_error))

    async def set_register(
        self, registerid: WinetRegister, value: int, key="002", memory=1
    ):
        """send raw register values !!!"""
        # data exemple: key=002&memory=1&regId=51&value=3
        async with aiohttp.ClientSession() as session:
            url = f"http://{self._stove_ip}/ajax/set-register"
            data = {
                "key": key,
                "memory": str(memory),
                "regId": str(registerid.value),
                "value": str(value),
            }
            headers = {
                "Access-Control-Request-Method": "POST",
                "Host": f"{self._stove_ip}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json; charset=utf-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": f"http://{self._stove_ip}",
                "Referer": f"http://{self._stove_ip}/management.html",
            }
            LOGGER.debug(f"Posting to {url}, data={data}")
            try:
                async with session.post(url, data=data, headers=headers) as response:
                    try:
                        # TODO: log others error responses codes
                        if response.status != 200:
                            # Valid address - but poll endpoint not found
                            LOGGER.warning(f"Error accessing {url} - {response.status}")
                            raise ConnectionError(
                                f"Error accessing {url} - {response.status}"
                            )
                        try:
                            # returns {'result': False} if failed (or True if success)
                            json_data = await response.json(content_type=None)
                            if json_data["result"] is not True:
                                LOGGER.debug("Received: %s", json_data)

                        except JSONDecodeError:
                            LOGGER.warning("Error decoding JSON: [%s]", response.text)
                    except ConnectionError as exc:
                        LOGGER.warning(f"Connection Error accessing {url}")
                        raise ConnectionError(
                            "ConnectionError - host not found"
                        ) from exc

            except (
                ServerDisconnectedError,
                ClientConnectorError,
                ClientOSError,
                ConnectionError,
                UnboundLocalError,
            ) as exc:
                raise ConnectionError() from exc
            except Exception as unknown_error:
                LOGGER.error("Unhandled Exception %s", type(unknown_error))
