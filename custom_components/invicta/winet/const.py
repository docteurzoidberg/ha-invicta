"""Constants and Globals."""
from enum import Enum


class WinetProductModel(Enum):  # type: ignore
    """Product models based on the web-ui"""

    UNSET = 0
    L023_1 = 1
    N100_O047 = 2
    O086 = 3
    L023_2 = 4
    U047 = 5

    def get_message(self) -> str:
        """Get a message associated with the enum."""
        if self.name == "UNSET":
            return "Unset"
        if self.name == "L023_1":
            return "L023 - 1"
        if self.name == "N100_O047":
            return "N100 / O047"
        if self.name == "O086":
            return "O086"
        if self.name == "L023_2":
            return "L023 - 2"
        if self.name == "U047":
            return "U047"
        return "UNKNOWN"


class WinetRegister(Enum):
    """Winet raw registers ids from web ui"""

    STATUS = 2
    ALARMS_BITS = 3
    TEMPERATURE_READ = 0
    TEMPERATURE_SET = 50
    POWER_SET = 51
    FAN_SPEED = 55


class WinetRegisterKey(Enum):
    """'key' parameter for get-registers url"""

    POLL_DATA = "020"
    CHANGE_STATUS = "022"


class WinetRegisterCategory(Enum):
    """'category' parameter for get-registers url"""

    NONE = -1
    POLL_CATEGORY_2 = 2
    POLL_CATEGORY_6 = 6
    POLL_CATEGORY_11 = 11
