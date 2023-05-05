"""Data model for events"""
import datetime
import uuid

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class Event(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Event object used to pass messages between an observable and an observer
    """

    id: uuid.UUID = uuid.uuid4()
    ts: datetime.datetime = datetime.datetime.now()
    tag: str
    data: dict
