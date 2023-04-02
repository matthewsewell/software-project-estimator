"""
This provides a single iteration for the monte carlo simulation.
"""

import datetime
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import numpy
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from software_project_estimator import Project

logger = logging.getLogger(__name__)


WEEKS_IN_A_YEAR = 52


class IterationResultStatus(str, Enum):
    """The status of the iteration result."""

    SUCCESS = "success"
    FAILURE = "failure"


class IterationResult(BaseModel):  # pylint: disable=too-few-public-methods
    """The result of an iteration."""

    status: IterationResultStatus
    message: Optional[str] = None
    attributes: Optional[dict] = None


class Iteration:
    """
    A single iteration of the monte carlo simulation. It maintains a context as
    self.context and a result as self.result. The result will be None until the
    iteration is complete. To complete the iteration, call self.run().
    """

    def __init__(self, project: Project) -> None:
        self.context = IterationContext()
        self.context.project = project

    @property
    def result(self) -> Optional[IterationResult]:
        """Return the result of the iteration."""
        return self.context.result

    def run(self) -> None:
        """Run the iteration."""
        self.context.transition_to(IterationStateUninitialized())
        while self.context.result is None:
            self.context.process()


class IterationContext:
    """
    The IterationContext defines the interface for running a full iteration.
    """

    project: Optional[Project] = None
    person_days_remaining: Optional[float] = None
    remainder_days: float = 0.0
    working_days_left: Optional[float] = None
    result: Optional[IterationResult] = None
    current_date: Optional[datetime.date] = None

    # This is the temporary result of the iteration. It is used to store what
    # we think is the result of the iteration until we formatlize it by setting
    # self.result.
    provisional_result: Optional[IterationResult] = None

    # This is the internal state of the context
    _state: Optional["IterationBaseState"] = None

    def transition_to(self, state: "IterationBaseState"):
        """
        The Context allows changing the State object at runtime.
        """

        self._state = state
        self._state.context = self

    def process(self):
        """
        The Context delegates part of its behavior to the current State object.
        """
        self._state.handle_process()

    def probabilistic_weekly_person_days_lost_to_vacations(self) -> int:
        """
        Returns a probabilistic number of person days theoretically lost to
        vacations within a theoretical week.
        """
        if not self.project or self.project.weeks_off_per_year <= 0:
            return 0
        days = 0.0
        for _index in range(self.project.developer_count):
            maximum = WEEKS_IN_A_YEAR / self.project.weeks_off_per_year
            if numpy.random.uniform(0.0, maximum) <= 1.0:
                days += self.project.work_days_per_week
        return int(days)

    def probabilistic_estimated_project_person_days(self) -> float:
        """
        Returns a probabilistic number of estimated project person days. This
        is based on the probability distribution of the project's tasks and is
        useful in aggregating the results of multiple simulations.
        """
        days = 0.0
        if not self.project:
            return days
        for task_group in self.project.task_groups:
            for task in task_group.tasks:
                days += numpy.random.normal(task.average, task.stddev)

        for task in self.project.tasks:
            days += numpy.random.normal(task.average, task.stddev)

        return days


class IterationBaseState(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    @property
    def context(self) -> IterationContext:  # pylint: disable=missing-function-docstring
        return self._context

    @context.setter
    def context(
        self, context: IterationContext
    ) -> None:  # pylint: disable=missing-function-docstring
        self._context = context

    @abstractmethod
    def handle_process(self) -> None:
        """Just a gentle reminder to set this method on every state."""
        raise NotImplementedError


class IterationStateCalculatingWeeks(IterationBaseState):
    """
    This state is responsible for calculating the number of whole weeks in the
    iteration.
    """

    def handle_process(self) -> None:
        """Calculate the number of whole weeks in the iteration."""

        if self.context.project is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No project was provided.",
            )
            self.context.transition_to(IterationStateError())
            return

        current_date = self.context.current_date
        maximum_weekly_days = self.context.project.max_person_days_per_week
        vacation_days = (
            self.context.probabilistic_weekly_person_days_lost_to_vacations()
        )
        holiday_days = self.context.project.person_days_lost_to_holidays_this_week(
            current_date
        )
        probabilistic_person_days_this_week = (
            maximum_weekly_days - vacation_days - holiday_days
        )
        probabilistic_person_days_this_week = (
            0
            if probabilistic_person_days_this_week < 0
            else probabilistic_person_days_this_week
        )
        if (
            self.context.person_days_remaining is not None
            and self.context.person_days_remaining
            <= probabilistic_person_days_this_week
        ):
            # It's now days, not weeks
            self.context.remainder_days = probabilistic_person_days_this_week
            self.context.transition_to(IterationStateCalculatingDays())
            return

        self.context.current_date = (
            current_date + datetime.timedelta(weeks=1)
            if current_date is not None
            else self.context.current_date
        )
        if self.context.person_days_remaining is not None:
            self.context.person_days_remaining -= probabilistic_person_days_this_week


class IterationStateCalculatingDays(IterationBaseState):
    """
    This state is responsible for calculating the number of whole days in the
    iteration.
    """

    def handle_process(self) -> None:
        """
        Calculate the number of days in the iteration once the weeks have been
        calculated.
        """

        if self.context.project is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No project was provided.",
            )
            self.context.transition_to(IterationStateError())
            return
        if self.context.current_date is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No current date was provided.",
            )
            self.context.transition_to(IterationStateError())
            return
        self.context.person_days_remaining = self.context.person_days_remaining or 0
        # The person days remaining are the number of person days left from the
        # estimated person days for the project after we've subtracted off all
        # the whole weeks. Remainder days is the remainder of the probablistic
        # person days calculated for the week. The ratio of the person days
        # remaining to the remainder days is the portion of the week that we
        # need to completed. By multiplying that by the number of work days in
        # a week, we get the number of working (calendar) days left in the
        # week. We only need to caluculate this the first time we're in this
        # state.
        if self.context.working_days_left is None:
            num_working_days = len(
                self.context.project.working_days_this_week(self.context.current_date)
            )
            portion_of_week = (
                self.context.person_days_remaining / self.context.remainder_days
            )
            self.context.working_days_left = portion_of_week * num_working_days

        # Lets consider the day we're on today. If it's a holiday or a weekend,
        # we need to skip it. If it's a working day, we need to decrement the
        # working days left by one. If we've reached zero working days left,
        # we need to transition to the finalizing state.

        if (
            self.context.current_date.weekday()
            not in self.context.project.weekly_work_days
            or self.context.project.is_holiday(self.context.current_date)
        ):
            self.context.current_date += datetime.timedelta(days=1)
        else:
            self.context.working_days_left -= 1
            self.context.current_date += datetime.timedelta(days=1)
            if self.context.working_days_left <= 0:
                self.context.transition_to(IterationStateFinalizing())


class IterationStateFinalizing(IterationBaseState):
    """
    This state is responsible for finalizing the iteration.
    """

    def handle_process(self) -> None:
        """Finalize the iteration."""

        if self.context.project is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No project was provided.",
            )
            self.context.transition_to(IterationStateError())
            return
        if self.context.current_date is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No current date was provided.",
            )
            self.context.transition_to(IterationStateError())
            return

        if (
            self.context.current_date.weekday()
            not in self.context.project.weekly_work_days
            or self.context.project.is_holiday(self.context.current_date)
        ):
            self.context.current_date += datetime.timedelta(days=1)
            return

        self.context.provisional_result = IterationResult(
            status=IterationResultStatus.SUCCESS,
            message="Process completed.",
            attributes={
                "start_date": self.context.current_date,
                "end_date": self.context.current_date
            },
        )

        self.context.transition_to(IterationStateSuccessful())


class IterationStateUninitialized(IterationBaseState):
    """
    The Uninitialized state is the initial state of the iteration.
    """

    def has_valid_project(self) -> bool:
        """Check if the project is valid."""
        if not self.context.project or not isinstance(self.context.project, Project):
            return False
        return True

    def has_tasks_or_task_groups(self) -> bool:
        """Check if the project has tasks or task groups."""
        if all(
            [
                self.context.project and not self.context.project.tasks,
                self.context.project and not self.context.project.task_groups,
            ]
        ):
            return False
        return True

    def handle_process(self) -> None:
        """This is where we initialize the iteration."""
        logger.debug("Iteration is initializing.")
        if not self.has_valid_project():
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No project was provided.",
            )
            self.context.transition_to(IterationStateError())
            return

        if not self.has_tasks_or_task_groups():
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No tasks were present in the project.",
            )
            self.context.transition_to(IterationStateError())
            return

        # Set all initial values. We can ignore the type here because we can't
        # get to this section of code without a project.
        self.context.current_date = self.context.project.start_date  # type: ignore
        self.context.person_days_remaining = (  # type: ignore
            self.context.probabilistic_estimated_project_person_days()
        )

        self.context.transition_to(IterationStateCalculatingWeeks())


class IterationStateError(IterationBaseState):
    """
    The Error state is the state of the iteration when an error has occurred
    """

    def handle_process(self) -> None:
        logger.debug("Iteration has encountered an error.")
        self.context.result = self.context.provisional_result or IterationResult(
            status=IterationResultStatus.FAILURE,
            message="Iteration failed unexpectedly. Someone should fix this.",
        )


class IterationStateSuccessful(IterationBaseState):
    """
    The Successful state is the final state of the iteration.
    """

    def handle_process(self) -> None:
        logger.debug("Iteration was successful.")
        self.context.result = self.context.provisional_result or IterationResult(
            status=IterationResultStatus.FAILURE,
            message=(
                "Iteration succeeded without a result. This should NEVER HAPPEN. "
                "Someone should fix this."
            ),
        )
