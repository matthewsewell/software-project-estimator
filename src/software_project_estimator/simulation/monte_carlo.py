"""This manages all the monte carlo simulation for the project estimator."""


import multiprocessing
from datetime import datetime
from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from software_project_estimator import Project
from software_project_estimator.event import Event
from software_project_estimator.observer import Observable
from software_project_estimator.simulation.models import IterationResultStatus

from software_project_estimator.simulation.iteration import (  # isort: skip
    Iteration,
    IterationResult,
)


class MonteCarloOutcome(BaseModel):  # pylint: disable=too-few-public-methods
    """This class represents the outcome of a monte carlo simulation."""

    total: int
    probability: float


class MonteCarlo(Observable):  # pylint: disable=too-few-public-methods
    """
    This class manages the monte carlo simulation for the project estimator.
    """

    def __init__(self, project: Project, iterations: int):
        """Initialize the monte carlo simulation."""
        self.project = project
        self.iterations = iterations
        super().__init__()

    def run(self) -> dict:
        """
        Run the monte carlo simulation using multiprocessing. Return a
        dictionary of the results.
        """

        start_time = datetime.now()
        self.notify_observers(Event(tag="monte_carlo_start", data={}))
        if self.project and self.project.max_person_days_per_week <= 0:
            # We'll send an event to the observers and raise an error here.
            # that way the observers can do something with the error even
            # if the error is trapped and handled in a different way.
            msg = (
                "The max person days per week must be greater than 0 or the "
                "simulation will never end. This is definately not what you "
                "want!"
            )
            self.notify_observers(Event(tag="monte_carlo_error", data={"message": msg}))
            raise RuntimeError(msg)

        with multiprocessing.Pool() as pool:
            results = []
            for _, result in enumerate(
                pool.imap_unordered(self._run_iteration, range(self.iterations))
            ):
                results.append(result)
                self.notify_observers(
                    Event(
                        tag="monte_carlo_run_iteration",
                        data={"number": i, "result": result},
                    )
                )
        end_time = datetime.now()
        self.notify_observers(
            Event(
                tag="monte_carlo_simulation_end",
                data={"seconds": (end_time - start_time).total_seconds()},
            )
        )
        return self._process_results(results)

    def _run_iteration(self, _) -> Optional[IterationResult]:
        """Run a single iteration of the monte carlo simulation."""
        iteration = Iteration(self.project)
        iteration.run()
        return iteration.result

    def _process_results(self, results: list) -> dict:
        """
        Process the results by iterating through the list of results and
        aggregating the data.
        """
        self.notify_observers(Event(tag="monte_carlo_processing_start", data={}))
        start_time = datetime.now()
        data: dict = {}
        for result in results:
            if result and result.status == IterationResultStatus.SUCCESS:
                end_date = result.attributes.get("end_date")
                if end_date not in data:
                    data[end_date] = 1
                else:
                    data[end_date] += 1
                self.notify_observers(
                    Event(tag="monte_carlo_result_prcessed", data={"result": result})
                )
        self.notify_observers(
            Event(
                tag="monte_carlo_processing_end",
                data={"seconds": (datetime.now() - start_time).total_seconds()},
            )
        )

        start_time = datetime.now()
        self.notify_observers(Event(tag="monte_carlo_outcomes_start", data={}))
        outcomes: dict = {}
        cumulative_count = 0
        for end_date, count in sorted(data.items()):
            cumulative_count += count
            outcomes[end_date] = MonteCarloOutcome(
                total=count, probability=cumulative_count / self.iterations
            )
            self.notify_observers(
                Event(
                    tag="monte_carlo_outcome_created",
                    data={"outcome": outcomes[end_date]},
                )
            )
        self.notify_observers(
            Event(
                tag="monte_carlo_outcomes_end",
                data={"seconds": (datetime.now() - start_time).total_seconds()},
            )
        )

        return outcomes
