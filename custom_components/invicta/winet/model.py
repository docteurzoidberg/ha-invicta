"""Model definitions."""
from pydantic import BaseModel, Field


class WinetParam(list[int]):
    """List of registerid and it's value"""


class WinetGetRegisterResult(BaseModel):
    """Base model for Winet stove status data."""

    params: list[WinetParam] = Field(default=[])
    cat: int = Field(default=0)
    signal: int = Field(default=0)
    bk: int = Field(default=0)
    authLevel: int = Field(default=0)
    model: int = Field(default=0)
    name: str = Field(default="unset")
