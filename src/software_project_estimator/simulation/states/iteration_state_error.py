"""This module contains the IterationStateError class."""

import logging

from software_project_estimator.simulation import states

from software_project_estimator.simulation.models import (  # isort: skip
    IterationResult,
    IterationResultStatus,
)

logger = logging.getLogger(__name__)


class IterationStateError(states.IterationBaseState):
    """
    The Error state is the state of the iteration when an error has occurred
    """

    def handle_process(self) -> None:
        logger.debug("Iteration has encountered an error.")
        self.context.result = self.context.provisional_result or IterationResult(
            status=IterationResultStatus.FAILURE,
            message="Iteration failed unexpectedly. Someone should fix this.",
        )
