"""This module contains the IterationStateFinalizing class."""

import datetime

from software_project_estimator.simulation import states

from software_project_estimator.simulation.models import (  # isort: skip
    IterationResult,
    IterationResultStatus,
)


class IterationStateFinalizing(states.IterationBaseState):
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
            self.context.transition_to(states.IterationStateError())
            return
        if self.context.current_date is None:
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No current date was provided.",
            )
            self.context.transition_to(states.IterationStateError())
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
                "end_date": self.context.current_date,
            },
        )

        self.context.transition_to(states.IterationStateSuccessful())
