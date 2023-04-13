"""Thhis module contains the IterationStateUninitialized class."""

import logging

from software_project_estimator.project import Project
from software_project_estimator.simulation import states

from software_project_estimator.simulation.models import (  # isort: skip
    IterationResult,
    IterationResultStatus,
)

logger = logging.getLogger(__name__)


class IterationStateUninitialized(states.IterationBaseState):
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
            self.context.transition_to(states.IterationStateError())
            return

        if not self.has_tasks_or_task_groups():
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No tasks were present in the project.",
            )
            self.context.transition_to(states.IterationStateError())
            return

        # Set all initial values. We can ignore the type here because we can't
        # get to this section of code without a project.
        self.context.current_date = self.context.project.start_date  # type: ignore
        self.context.person_days_remaining = (  # type: ignore
            self.context.probabilistic_estimated_project_person_days()
        )

        self.context.transition_to(states.IterationStateCalculatingWeeks())
