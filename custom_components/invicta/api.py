"""API Client."""
import asyncio
from asyncio import Task
from enum import Enum
import time
import aiohttp
from aiohttp import ClientOSError

from custom_components.invicta.winet.model import WinetGetRegisterResult
from custom_components.invicta.winet.winet import WinetAPILocal
from custom_components.invicta.winet.const import (
    WinetRegister,
    WinetRegisterKey,
    WinetRegisterCategory,
    WinetProductModel,
)

from .const import LOGGER


def clamp(value, valuemin, valuemax):
    """clamp value between min and max"""
    return valuemin if value < valuemin else valuemax if value > valuemax else value


class InvictaDeviceStatus(Enum):  # type: ignore
    """Status Class based on the web-ui"""

    OFF = 0
    WAIT_FOR_FLAME = 1, 2
    POWER_ON = 3
    WORK = 4
    BRAZIER_CLEANING = 5
    FINAL_CLEANING = 6
    STANDBY = 7
    ALARM = 8
    ALARM_MEMORY = 9
    UNKNOWN = -1

    def get_message(self) -> str:
        """Get a message associated with the enum."""
        if self.name == "OFF":
            return "Off"
        if self.name == "WAIT_FOR_FLAME":
            return "Waiting flame"
        if self.name == "POWER_ON":
            return "Power on"
        if self.name == "WORK":
            return "Working"
        if self.name == "BRAZIER_CLEANING":
            return "Brazzier cleaning"
        if self.name == "FINAL_CLEANING":
            return "Final cleaning"
        if self.name == "STANDBY":
            return "Standby"
        if self.name == "ALARM":
            return "Alarm"
        if self.name == "ALARM_MEMORY":
            return "Alarm memory"
        if self.name == "UNKNOWN":
            return "Unknown"
        return f"Unknown status{self.name}"


class InvictaDeviceAlarm(Enum):  # type: ignore
    """Winet alarm bits"""

    SMOKE_PROBE_FAILURE = 0
    SMOKE_OVERTEMPERATURE = 1
    EXTRACTOR_MALFUNCTION = 2
    FAILED_IGNITION = 3
    NO_PELLETS = 4
    LACK_OF_PRESSURE = 5
    THERMAL_SAFETY = 6
    OPEN_PELLET_COMPARTMENT = 7

    def get_message(self) -> str:
        """Get a message associated with the enum."""
        if self.name == "SMOKE_PROBE_FAILURE":
            return "Smoke probe failure !"
        if self.name == "SMOKE_OVERTEMPERATURE":
            return "Smoke over-temperature !"
        if self.name == "EXTRACTOR_MALFUNCTION":
            return "Extractor malfunction !"
        if self.name == "FAILED_IGNITION":
            return "Failed ignition"
        if self.name == "NO_PELLETS":
            return "No pellets"
        if self.name == "LACK_OF_PRESSURE":
            return "Lacks of pressure !"
        if self.name == "THERMAL_SAFETY":
            return "Thermal safety !"
        if self.name == "OPEN_PELLET_COMPARTMENT":
            return "Pellet compartment is open !"
        return "UNKNOWN"


class InvictaApiData:
    """Usable api data for the home assistant integration"""

    def __init__(self, host: str):
        """init unset data"""
        self._rawdata = WinetGetRegisterResult()
        self.signal = self._rawdata.signal
        self.name = self._rawdata.name
        self.host = host
        self.model = WinetProductModel(self._rawdata.model).get_message()
        self.status = InvictaDeviceStatus.UNKNOWN
        self.alarms = []
        self.temperature_read = 0.0
        self.temperature_set = 0.0
        self.power_set = 0
        self.fan_speed = 0

    def update(self, newdata: WinetGetRegisterResult, decode: bool = True):
        """Update or add data to rawdata"""

        # convert actual data to dict
        newparamsdict = {}
        for oldparam in self._rawdata.params:
            key = oldparam[0]
            value = oldparam[1]
            newparamsdict[key] = value

        # overwrite or add new key/values
        for newparam in newdata.params:
            key = newparam[0]
            value = newparam[1]
            newparamsdict[key] = value

        # convert back to list of int,int
        newparams = []
        for key, val in newparamsdict.items():
            newparams.append([key, val])

        # update class data
        self._rawdata.params = newparams
        self._rawdata.cat = newdata.cat
        self._rawdata.signal = newdata.signal
        self._rawdata.bk = newdata.bk
        self._rawdata.authLevel = newdata.authLevel
        self._rawdata.model = newdata.model
        self._rawdata.name = newdata.name

        if decode:
            self.signal = newdata.signal
            self.name = newdata.name
            self.model = WinetProductModel(newdata.model)
            self._decode_status()
            self._decode_alarms()
            self._decode_temperature_read()
            self._decode_temperature_set()
            self._decode_power_set()
            self._decode_fan_speed()

    def _get_register_value(self, registerid: WinetRegister) -> int:
        """Parse all data (memory banks?) to find a register's value"""
        for param in self._rawdata.params:
            if param[0] == registerid.value:
                return param[1]
        LOGGER.error(f"RegisterId {registerid.value} not found in data")
        LOGGER.debug(self._rawdata)
        raise Exception("RegisterId not found in data")

    def _decode_status(self) -> None:
        """Decode status register"""
        status = self._get_register_value(WinetRegister.STATUS)
        if status in (1, 2):
            self.status = InvictaDeviceStatus.WAIT_FOR_FLAME
        else:
            self.status = InvictaDeviceStatus(status)

    def _decode_alarms(self) -> None:
        """Decode alarm register byte into individual alarms"""
        alarmsbyte = self._get_register_value(WinetRegister.ALARMS_BITS)
        LOGGER.debug(f"Alarm byte value is {alarmsbyte}")
        if alarmsbyte < 0:
            LOGGER.error("Cannot decode alarms")
            return
        for i in range(8):
            temp = alarmsbyte >> i
            if temp & 1:
                self.alarms.append(InvictaDeviceAlarm(i))

    def _decode_temperature_read(self) -> None:
        """
        Decodes Temperature read register
        reg. value is two time the temperature in celsius
        """
        param = self._get_register_value(WinetRegister.TEMPERATURE_READ)
        self.temperature_read = param / 2

    def _decode_temperature_set(self) -> None:
        """
        Decodes Temperature set register
        reg. value is two time the temperature in celsius
        """
        param = self._get_register_value(WinetRegister.TEMPERATURE_SET)
        self.temperature_set = param / 2

    def _decode_power_set(self) -> None:
        """Power set"""
        self.power_set = self._get_register_value(WinetRegister.POWER_SET)

    def _decode_fan_speed(self) -> None:
        """Room vent fan speed"""
        self.fan_speed = self._get_register_value(WinetRegister.FAN_SPEED)

    @property
    def is_on(self) -> bool:
        """Is stove on ?"""
        return self.status in [
            InvictaDeviceStatus.POWER_ON,
            InvictaDeviceStatus.WAIT_FOR_FLAME,
            InvictaDeviceStatus.STANDBY,
        ]

    @property
    def is_heating(self) -> bool:
        """Is heating ?"""
        return self.status in [InvictaDeviceStatus.WORK]

    @property
    def error_offline(self) -> bool:
        """Is offline ?"""
        # TODO: another way to check if offline ???
        return self.status == InvictaDeviceStatus.UNKNOWN

    @property
    def alarm_extractor_malfunction(self) -> bool:
        """Alarm bit for extractor malfunction is set ?"""
        return InvictaDeviceAlarm.EXTRACTOR_MALFUNCTION in self.alarms

    @property
    def alarm_failed_ignition(self) -> bool:
        """Alarm bit for failed ignition is set ?"""
        return InvictaDeviceAlarm.FAILED_IGNITION in self.alarms

    @property
    def alarm_lack_of_pressure(self) -> bool:
        """.alarm bit for lack of pressure is set ?"""
        return InvictaDeviceAlarm.LACK_OF_PRESSURE in self.alarms

    @property
    def alarm_no_pellets(self) -> bool:
        """Alarm bit for no pellets is set ?"""
        return InvictaDeviceAlarm.NO_PELLETS in self.alarms

    @property
    def alarm_open_pellet_compartment(self) -> bool:
        """Alarm bit for open pellet compartment is set ?"""
        return InvictaDeviceAlarm.OPEN_PELLET_COMPARTMENT in self.alarms

    @property
    def alarm_smoke_overtemp(self) -> bool:
        """Alarm bit for smoke temperature is set ?"""
        return InvictaDeviceAlarm.SMOKE_OVERTEMPERATURE in self.alarms

    @property
    def alarm_smoke_probe_failure(self) -> bool:
        """Alarm bit for smoke probe failure is set?"""
        return InvictaDeviceAlarm.SMOKE_PROBE_FAILURE in self.alarms

    @property
    def alarm_thermal_safety(self) -> bool:
        """Alarm bit for thermal safety is set?"""
        return InvictaDeviceAlarm.THERMAL_SAFETY in self.alarms


class InvictaApiClient:
    """Invicta api client. use winet control api polling as backend"""

    failed_poll_attempts = 0
    is_sending = False
    is_polling_in_background = False
    stove_ip = ""

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        """init"""
        self._host = host
        self._session = session
        self._data = InvictaApiData(host)
        self._winetclient = WinetAPILocal(session, host)
        self._should_poll_in_background = False
        self._bg_task: Task | None = None

        self.stove_ip = host
        self.is_polling_in_background = False
        self.is_sending = False
        self.failed_poll_attempts = 0

    @property
    def data(self) -> InvictaApiData:
        """Returns decoded data from api raw data"""
        if self._data.name == "unset":
            LOGGER.warning("Returning uninitialized poll data")
        return self._data

    def log_status(self) -> None:
        """Log a status message."""
        LOGGER.info(
            "InvictaApiClient Status\n\tis_sending\t[%s]\n\tfailed_polls\t[%d]\n\tBG_Running\t[%s]\n\tBG_ShouldRun\t[%s]",
            self.is_sending,
            self.failed_poll_attempts,
            self.is_polling_in_background,
            self._should_poll_in_background,
        )

    async def start_background_polling(self, minimum_wait_in_seconds: int = 5) -> None:
        """Start an ensure-future background polling loop."""
        if self.is_sending:
            LOGGER.info(
                "!! Suppressing start_background_polling -- sending mode engaged"
            )
            return

        if not self._should_poll_in_background:
            self._should_poll_in_background = True
            # asyncio.ensure_future(self.__background_poll(minimum_wait_in_seconds))
            LOGGER.info("!!  start_background_polling !!")

            self._bg_task = asyncio.create_task(
                self.__background_poll(minimum_wait_in_seconds),
                name="background_polling",
            )

    def stop_background_polling(self) -> bool:
        """Stop background polling - return whether it had been polling."""
        self._should_poll_in_background = False
        was_running = False
        if self._bg_task:
            if not self._bg_task.cancelled():
                was_running = True
                self._bg_task.cancel()
                LOGGER.info("Stopping background task to issue a command")

        return was_running

    async def __background_poll(self, minimum_wait_in_seconds: int = 5) -> None:
        """Perform a polling loop."""
        LOGGER.debug("__background_poll:: Function Called")

        self.failed_poll_attempts = 0

        self.is_polling_in_background = True
        while self._should_poll_in_background:

            start = time.time()
            LOGGER.debug("__background_poll:: Loop start time %f", start)

            try:
                await self.poll()
                self.failed_poll_attempts = 0
                end = time.time()

                duration: float = end - start
                sleep_time: float = minimum_wait_in_seconds - duration

                LOGGER.debug(
                    "__background_poll:: [%f] Sleeping for [%fs]", duration, sleep_time
                )

                LOGGER.debug(
                    "__background_poll:: duration: %f, %f, %.2fs",
                    start,
                    end,
                    (end - start),
                )
                LOGGER.debug(
                    "__background_poll:: Should Sleep For: %f",
                    (minimum_wait_in_seconds - (end - start)),
                )

                await asyncio.sleep(minimum_wait_in_seconds - (end - start))
            except (ConnectionError, ClientOSError):
                self.failed_poll_attempts += 1
                LOGGER.info(
                    "__background_poll:: Polling error [x%d]", self.failed_poll_attempts
                )

        self.is_polling_in_background = False
        LOGGER.info("__background_poll:: Background polling disabled.")

    async def set_fan_speed(self, value):
        """Set air room vent fan speed"""
        # ui min value is 0 (=50% fan) to 10 (=100fan)
        value = clamp(int(value), 0, 10)
        LOGGER.debug(f"Set fan speed to {value}")
        await self._winetclient.set_register(WinetRegister.FAN_SPEED, value)

    async def set_power(self, value):
        """Send set register with key=002&memory=1&regId=51&value={value}"""
        # ui's min value is 2 and maximum is 5
        value = clamp(int(value), 2, 5)
        LOGGER.debug(f"Set power to {value}")
        await self._winetclient.set_register(WinetRegister.POWER_SET, value)

    async def set_temperature(self, value: float):
        """Send set register with key=002&memory=1&regId=50&value={value*2}"""
        # self defined min/max values
        value = clamp(float(value), 0.0, 25.0)
        LOGGER.warning(f"Set temperature to {value}")
        await self._winetclient.set_register(
            WinetRegister.TEMPERATURE_SET, int(value * 2)
        )

    async def turn_on(self):
        """Turn on the stove"""
        if self.data.status != InvictaDeviceStatus.OFF:
            return
        LOGGER.debug("Turn stove on")
        await self._winetclient.get_registers(WinetRegisterKey.CHANGE_STATUS)

    async def turn_off(self):
        """Turn on the stove"""
        if self.data.status == InvictaDeviceStatus.OFF:
            return
        LOGGER.debug("Turn stove off")
        await self._winetclient.get_registers(WinetRegisterKey.CHANGE_STATUS)

    async def poll(self) -> None:
        """Poll the Winet module locally."""
        result = await self._winetclient.get_registers(
            WinetRegisterKey.POLL_DATA, WinetRegisterCategory.POLL_CATEGORY_2
        )
        self._data.update(newdata=result, decode=False)
        result = await self._winetclient.get_registers(
            WinetRegisterKey.POLL_DATA, WinetRegisterCategory.POLL_CATEGORY_11
        )
        self._data.update(newdata=result)
