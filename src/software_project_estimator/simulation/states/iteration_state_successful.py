"""This module contains the IterationStateSuccessful class."""

import logging

from software_project_estimator.simulation import states
from software_project_estimator.simulation.models import (
    IterationResult, IterationResultStatus)

logger = logging.getLogger(__name__)


class IterationStateSuccessful(states.IterationBaseState):
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
