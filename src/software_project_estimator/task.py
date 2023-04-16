"""
Provides a task data model. A task has a name and various estimates
"""

import math
from typing import List
from uuid import UUID, uuid4

from pydantic import (  # pylint: disable=no-name-in-module # isort: skip
    BaseModel,
    Field,
    root_validator,
)


class TaskGroup(BaseModel):
    """
    A group of tasks. This acts as a container for tasks. A task can be in more
    than one group but it will then be processed multiple times. This may be
    what you want if, for example, you have a QA task that always has the same
    estimates and you want to include it in multiple sections of work.
    """

    name: str = Field(description="The name of the task group")
    id_: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the task group",
    )
    tasks: List["Task"] = Field(
        default=[],
        description="The tasks in the group",
    )

    @property
    def task_count(self) -> int:
        """Return the number of tasks in the group."""
        return len(self.tasks)

    def add_task(self, task: "Task") -> bool:
        """Add a task to the group. Return True if the task was added."""
        if task in self.tasks:
            return False
        self.tasks.append(task)
        return True


class Task(BaseModel):
    """Data model for our task object"""

    id_: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the task group",
    )
    name: str
    optimistic: float  # Optimistic estimate in person days
    pessimistic: float  # Pessimistic estimate in person days
    likely: float  # Most likely estimate in person days

    @root_validator(pre=True)
    def ensure_estimates_are_sane(
        cls, values: dict
    ):  # pylint: disable=no-self-argument
        """Ensure that the estimates are sane"""
        try:
            optimistic = values["optimistic"]
            likely = values["likely"]
            pessimistic = values["pessimistic"]
        except KeyError:
            # We'll get here if a previous validator has already raised an error
            return values
        if optimistic < 0:
            raise ValueError("Optimistic estimate must be zero or more")
        if likely < optimistic:
            raise ValueError(
                "Likely estimate must be equal to or greater than the optimistic estimate"
            )
        if pessimistic < likely:
            raise ValueError(
                "Pessimistic estimate must be equal to or greater than the likely estimate"
            )
        return values

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
