"""This module contains the IterationStateCalculatingWeeks class."""

import datetime

from software_project_estimator.simulation import states
from software_project_estimator.simulation.models import (
    IterationResult, IterationResultStatus)


class IterationStateCalculatingWeeks(states.IterationBaseState):
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
            self.context.transition_to(states.IterationStateError())
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
            self.context.transition_to(states.IterationStateCalculatingDays())
            return

        self.context.current_date = (
            current_date + datetime.timedelta(weeks=1)
            if current_date is not None
            else self.context.current_date
        )
        if self.context.person_days_remaining is not None:
            self.context.person_days_remaining -= probabilistic_person_days_this_week
