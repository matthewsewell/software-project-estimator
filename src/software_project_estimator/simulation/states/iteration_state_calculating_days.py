"""This module contains the IterationStateCalculatingDays class."""

import datetime

from software_project_estimator.simulation import states

from software_project_estimator.simulation.models import (  # isort: skip
    IterationResult,
    IterationResultStatus,
)


class IterationStateCalculatingDays(states.IterationBaseState):
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
            self.context.transition_to(states.IterationStateError())
            return
        if self.context.current_date is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No current date was provided.",
            )
            self.context.transition_to(states.IterationStateError())
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
                self.context.transition_to(states.IterationStateFinalizing())
