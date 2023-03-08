"""
Provides the project data model. It should have a number of parameters that
can be set and a number of properties that can be read. Additionally, it can run
the Monte Carlo simulation and return the results.
"""

from datetime import date
from typing import List

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from software_project_estimator.task import Task, TaskGroup

DAYS_IN_A_WEEK = 5
WEEKS_IN_A_YEAR = 52


class Project(BaseModel):
    """
    A software project. This is the main data model for the package. It
    contains a number of parameters that can be set and a number of properties
    that can be read. It also contains a number of methods that can be called
    to perform various calculations.
    """

    name: str = Field(description="The name of the project")
    start_date: date = Field(
        default=date.today(),
        description="The start date of the project",
    )
    developer_count: int = Field(
        default=1,
        description="The number of developers working on the project",
    )
    weeks_off_per_year: float = Field(
        default=2.0,  # 2 weeks off per year
        description="The number of weeks off per year the average developer gets",
    )
    work_days_per_week: float = Field(
        default=5.0,  # 5 days per week
        description="The number of work days per week the average developer works",
    )
    work_hours_per_day: float = Field(
        default=8.0,  # 8 hours per day
        description="The number of work hours per day the average developer works",
    )
    communication_penalty: float = Field(
        default=0.5,
        description=(
            "The communication penalty. This is the average amount of time "
            "per week that a developer has to communicate with another developer "
        ),
    )
    tasks: List[Task] = Field(
        default=[],
        description="The tasks in the project not associeted with a group",
    )
    task_groups: List[TaskGroup] = Field(
        default=[],
        description="The task groups in the project",
    )
    distribution: dict = {}
    endings: dict = {}

    @property
    def work_week_hours(self) -> float:
        """The number of work hours per week."""
        return self.work_days_per_week * self.work_hours_per_day

    @property
    def num_communication_channels(self) -> int:
        """The number of communication channels."""
        return int(self.developer_count * (self.developer_count - 1) / 2)

    @property
    def max_person_days_per_week(self) -> float:
        """
        The maximum number of person days per week, taking into account the loss
        of productivity due to communication.
        """
        base_hours = self.developer_count * self.work_week_hours
        communication_hours = (
            # Each communication channel has two people
            2
            * self.num_communication_channels
            * self.communication_penalty
        )
        return (base_hours - communication_hours) / self.work_hours_per_day
