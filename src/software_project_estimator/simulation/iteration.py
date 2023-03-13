"""
This provides a single iteration for the monte carlo simulation.
"""

import datetime
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from software_project_estimator import Project

logger = logging.getLogger(__name__)


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

    async def run(self) -> None:
        """Run the iteration."""
        self.context.transition_to(IterationStateUninitialized())
        while self.context.result is None:
            await self.context.process()


class IterationContext:
    """
    The IterationContext defines the interface for running a full iteration.
    """

    project: Optional[Project] = None
    attributes: dict = {}
    person_days_remaining: Optional[float] = None
    result: Optional[IterationResult] = None

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

    async def process(self):
        """
        The Context delegates part of its behavior to the current State object.
        """
        await self._state.handle_process()


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
    async def handle_process(self) -> None:
        """Just a gentle reminder to set this method on every state."""
        raise NotImplementedError


class IterationStateUninitialized(IterationBaseState):
    """
    The Uninitialized state is the initial state of the iteration.
    """

    async def has_valid_project(self) -> bool:
        """Check if the project is valid."""
        if not self.context.project or not isinstance(self.context.project, Project):
            return False
        return True

    async def has_tasks_or_task_groups(self) -> bool:
        """Check if the project has tasks or task groups."""
        if all(
            [
                not self.context.project.tasks,
                not self.context.project.task_groups,
            ]
        ):
            return False
        return True

    async def handle_process(self) -> None:
        """This is where we initialize the iteration."""
        logger.debug("Iteration is initializing.")
        if not await self.has_valid_project():
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No project was provided.",
            )
            self.context.transition_to(IterationStateError())
            return

        if not await self.has_tasks_or_task_groups():
            self.context.provisional_result = IterationResult(
                status=IterationResultStatus.FAILURE,
                message="No tasks were present in the project.",
            )
            self.context.transition_to(IterationStateError())
            return

        # Set all initial values
        self.context.attributes["start_date"] = self.context.project.start_date
        self.context.attributes["end_date"] = None
        self.context.person_days_remaining = \
        self.context.project.random_estimated_project_person_days()

        self.context.transition_to(IterationStateSuccessful())


class IterationStateError(IterationBaseState):
    """
    The Error state is the state of the iteration when an error has occurred.
    """

    async def handle_process(self) -> None:
        logger.debug("Iteration has encountered an error.")
        self.context.result = self.context.provisional_result or IterationResult(
            status=IterationResultStatus.FAILURE,
            message="Iteration failed unexpectedly. Someone should fix this.",
        )


class IterationStateSuccessful(IterationBaseState):
    """
    The Successful state is the final state of the iteration.
    """

    async def handle_process(self) -> None:
        logger.debug("Iteration was successful.")
        self.context.result = IterationResult(
            status=IterationResultStatus.SUCCESS,
            message="Iteration completed successfully.",
            attributes=self.context.attributes,
        )
