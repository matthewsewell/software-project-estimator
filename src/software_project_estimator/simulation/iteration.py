"""
This provides a single iteration for the monte carlo simulation. Much of this
was inspired by the article on the state pattern at
https://refactoring.guru/design-patterns/state.
"""

import datetime
import logging
from typing import Optional

import numpy

from software_project_estimator import Project
from software_project_estimator.simulation.models import IterationResult
from software_project_estimator.simulation.states import (
    IterationBaseState, IterationStateUninitialized)

logger = logging.getLogger(__name__)


WEEKS_IN_A_YEAR = 52


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
    _state: Optional[IterationBaseState] = None

    def transition_to(self, state: IterationBaseState):
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
