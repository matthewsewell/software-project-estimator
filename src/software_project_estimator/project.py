"""
Provides the project data model. It should have a number of parameters that
can be set and a number of properties that can be read. Additionally, it can run
the Monte Carlo simulation and return the results.
"""

from datetime import date, timedelta
from typing import List

import holidays
import numpy
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from software_project_estimator.task import Task, TaskGroup

DAYS_IN_A_WEEK = 7
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
    weekly_work_days: List[int] = Field(
        default=[0, 1, 2, 3, 4, ],
        description=(
            "Days of the week that are considered work days. "
            "These start on Monday and are zero-indexed."
        )
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
    _work_holidays: dict = {}

    @property
    def work_days_per_week(self) -> int:
        """Returns the number of work days per week."""
        return len(self.weekly_work_days)

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

    def is_holiday(self, this_date: date) -> bool:
        """Returns True if this_date is a holiday."""
        try:
            holidays_this_year = self._work_holidays[this_date.year]
        except KeyError:
            holidays_this_year = holidays.UnitedStates(years=[this_date.year])
            self._work_holidays[this_date.year] = holidays_this_year
        return this_date in holidays_this_year

    def person_days_lost_to_holidays_this_week(self, start_date: date) -> int:
        """Returns the number of person days lost to holidays this week."""
        days_lost = 0
        current_date = start_date
        for _day in range(DAYS_IN_A_WEEK):
            if self.is_holiday(current_date):
                days_lost += self.developer_count
            current_date += timedelta(days=1)
        return days_lost

    def random_weekly_person_days_lost_to_vacations(self) -> int:
        """
        Returns a random number of person days theoretically lost to vacations
        within an imagiary week.
        """
        if self.weeks_off_per_year <= 0:
            return 0
        days = 0.0
        for _index in range(self.developer_count):
            maximum = WEEKS_IN_A_YEAR / self.weeks_off_per_year
            if numpy.random.uniform(0.0, maximum) <= 1.0:
                days += self.work_days_per_week
        return int(days)

    def random_estimated_project_person_days(self) -> float:
        """
        Returns a semi-random number of estimated project person days. This is
        based on the probability distribution of the project's tasks and is
        useful in aggregating the results of multiple simulations.
        """
        days = 0.0
        for task_group in self.task_groups:
            for task in task_group.tasks:
                days += numpy.random.normal(task.average, task.stddev)

        for task in self.tasks:
            days += numpy.random.normal(task.average, task.stddev)

        return days
