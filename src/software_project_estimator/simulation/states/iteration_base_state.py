"""The base state for the Iteration state machine."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from software_project_estimator.simulation.iteration import \
        IterationContext


class IterationBaseState(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    @property
    def context(
        self,
    ) -> "IterationContext":  # pylint: disable=missing-function-docstring
        """Return the context for this state."""
        return self._context

    @context.setter
    def context(
        self, context: "IterationContext"
    ) -> None:  # pylint: disable=missing-function-docstring
        self._context = context

    @abstractmethod
    def handle_process(self) -> None:
        """Just a gentle reminder to set this method on every state."""
        raise NotImplementedError
