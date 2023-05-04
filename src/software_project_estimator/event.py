import uuid

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class Event(BaseModel):
    """
    Event object used to pass messages between an observable and an observer
    """

    id: uuid.UUID = uuid.uuid4()
    tag: str
    data: dict
