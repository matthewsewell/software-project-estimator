"""This module contains the models used by the simulation package."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class IterationResultStatus(str, Enum):
    """The status of the iteration result."""

    SUCCESS = "success"
    FAILURE = "failure"


class IterationResult(BaseModel):  # pylint: disable=too-few-public-methods
    """The result of an iteration."""

    status: IterationResultStatus
    message: Optional[str] = None
    attributes: Optional[dict] = None
