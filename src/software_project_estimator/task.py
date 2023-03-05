"""
Provides a task data model. A task has a name, estimates and an optional
task group identifier.
"""

import math
from uuid import UUID, uuid4

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Task(BaseModel):
    """Data model for our task object"""

    id_: UUID = Field(default_factory=uuid4)
    name: str
    optimistic: float  # Optimistic estimate in person days
    pessimistic: float  # Pessimistic estimate in person days
    likely: float  # Most likely estimate in person days

    @property
    def average(self) -> float:
        """
        Property representing a wieghted average where the most likely
        estimate is weighted 4 times the other estimates.
        """
        return (
            float(self.optimistic) + float(self.pessimistic) + 4 * float(self.likely)
        ) / 6

    @property
    def stddev(self) -> float:
        """
        Property representing the standard deviation defined as the difference
        between the optimistic and pessimistic estimates divided by 6.
        """
        return (float(self.pessimistic) - float(self.optimistic)) / 6

    @property
    def variance(self) -> float:
        """
        Property representing the variance, which is the square root of the
        standard deviation.
        """
        return math.sqrt(self.stddev)
