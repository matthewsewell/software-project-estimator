"""
Provides the project data model. It should have a number of parameters that
can be set and a number of properties that can be read. Additionally, it can run
the Monte Carlo simulation and return the results.
"""

from datetime import date, timedelta
from typing import List, Optional

import holidays

from pydantic import (  # pylint: disable=no-name-in-module # isort: skip
    BaseModel,
    Field,
    validator,
)

from software_project_estimator.task import Task, TaskGroup  # isort: skip


DAYS_IN_A_WEEK = 7
WEEKS_IN_A_YEAR = 52


class Project(BaseModel):  # pylint: disable=too-many-instance-attributes
    """
    A software project. This is the main data model for the package. It
    contains a number of parameters that can be set and a number of properties
    that can be read. It also contains a number of methods that can be called
    to perform various calculations.
    """

    class Config:  # pylint: disable=too-few-public-methods
        """This class configures the project data model."""

        # This ensures that the validators are run when the model is updated
        validate_assignment = True

    name: str = Field(description="The name of the project")
    start_date: date = Field(
        default=date.today(),
        description="The start date of the project",
    )
    developer_count: int = Field(
        default=1,
        description="The number of developers working on the project",
    )
    country_code: Optional[str] = Field(
        default="US",
        description="The 2-digit country code for the holiday schedule",
    )
    weeks_off_per_year: float = Field(
        default=2.0,  # 2 weeks off per year
        description="The number of weeks off per year the average developer gets",
    )
    weekly_work_days: List[int] = Field(
        default=[
            0,
            1,
            2,
            3,
            4,
        ],
        description=(
            "Days of the week that are considered work days. "
            "These start on Monday and are zero-indexed."
        ),
    )
    work_hours_per_day: float = Field(
        default=8.0,  # 8 hours per day
        description="The number of work hours per day the average developer works",
    )
    communication_penalty: float = Field(
        default=0.5,
        description=(
            "The communication penalty. This is the average amount of time "
            "(in hours) per week that a developer has to communicate with "
            "another developer."
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
    _work_holidays: dict = {}

    @validator("developer_count")
    def _validate_developer_count(  # pylint: disable=no-self-argument
        cls, value: int
    ) -> int:
        """Validate the developer count."""
        if value < 1:
            raise ValueError("The developer count must be greater than 0")
        return value

    @validator("weeks_off_per_year")
    def _validate_weeks_off_per_year(  # pylint: disable=no-self-argument
        cls, value: float
    ) -> float:
        """
        Validate the weeks off per year. They need to be positive and less
        than 52.
        """
        if value < 0:
            raise ValueError("The weeks off per year must be 0 or greater")
        if value >= WEEKS_IN_A_YEAR:
            raise ValueError(
                "The weeks off per year must be less than 52 weeks per year"
            )
        return value

    @validator("weekly_work_days")
    def _validate_weekly_work_days(  # pylint: disable=no-self-argument
        cls, value: List[int]
    ) -> List[int]:
        """
        Validate that the weekly work days is a list of at least one integer
        between 0 and 6.
        """
        if not value:
            raise ValueError("The weekly work days must be a non-empty list")
        if any(day not in range(DAYS_IN_A_WEEK) for day in value):
            raise ValueError(
                "The weekly work days must be a list of integers between 0 and 6"
            )
        return value

    @validator("work_hours_per_day")
    def _validate_work_hours_per_day(  # pylint: disable=no-self-argument
        cls, value: float
    ) -> float:
        """
        Validate the work hours per day. They need to be more than 1 and less
        than 16.
        """
        if value < 1:
            raise ValueError("The work hours per day must be one or more")
        if value >= 16:
            raise ValueError("The work hours per day must be less than 16")
        return value

    @validator("communication_penalty")
    def _validate_communication_penalty(  # pylint: disable=no-self-argument
        cls, value: float
    ) -> float:
        """
        Validate the communication penalty. It needs to be positive and less
        than 10.
        """
        if value < 0:
            raise ValueError("The communication penalty must be greater than 0")
        if value >= 10:  # 10 hours is a lot of communication
            raise ValueError("The communication penalty must be less than 10")
        return value

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
        if self.country_code is None:
            return False
        try:
            holidays_this_year = self._work_holidays[this_date.year]
        except KeyError:
            try:
                holidays_this_year = holidays.country_holidays(
                    self.country_code, years=[this_date.year]
                )
            except NotImplementedError as err:
                raise ValueError(
                    f"Unsupported country code: {self.country_code}"
                ) from err
            self._work_holidays[this_date.year] = holidays_this_year
        return this_date in holidays_this_year

    def person_days_lost_to_holidays_this_week(self, start_date: Optional[date]) -> int:
        """Returns the number of person days lost to holidays this week."""
        if start_date is None:
            return 0
        days_lost = 0
        current_date = start_date
        for _day in range(DAYS_IN_A_WEEK):
            if self.is_holiday(current_date):
                days_lost += self.developer_count
            current_date += timedelta(days=1)
        return days_lost

    def working_days_this_week(self, start_date: date) -> list:
        """Returns all the days this week that are work days."""
        working_days = []
        for _day in range(DAYS_IN_A_WEEK):
            if start_date.weekday() in self.weekly_work_days and not self.is_holiday(
                start_date
            ):
                working_days.append(start_date)
            start_date += timedelta(days=1)
        return working_days
