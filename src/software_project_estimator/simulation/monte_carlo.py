"""This manages all the monte carlo simulation for the project estimator."""


import multiprocessing
from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from software_project_estimator import Project
from software_project_estimator.simulation.models import IterationResultStatus

from software_project_estimator.simulation.iteration import (  # isort: skip
    Iteration,
    IterationResult,
)


class MonteCarloOutcome(BaseModel):  # pylint: disable=too-few-public-methods
    """This class represents the outcome of a monte carlo simulation."""

    total: int
    probability: float


class MonteCarlo:  # pylint: disable=too-few-public-methods
    """
    This class manages the monte carlo simulation for the project estimator.
    """

    def __init__(self, project: Project, iterations: int):
        """Initialize the monte carlo simulation."""
        self.project = project
        self.iterations = iterations

    def run(self) -> dict:
        """
        Run the monte carlo simulation using multiprocessing. Return a
        dictionary of the results.
        """
        with multiprocessing.Pool() as pool:
            results = pool.map(self._run_iteration, range(self.iterations))
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
        data: dict = {}
        for result in results:
            if result and result.status == IterationResultStatus.SUCCESS:
                end_date = result.attributes.get("end_date")
                if end_date not in data:
                    data[end_date] = 1
                else:
                    data[end_date] += 1

        outcomes: dict = {}
        cumulative_count = 0
        for end_date, count in sorted(data.items()):
            cumulative_count += count
            outcomes[end_date] = MonteCarloOutcome(
                total=count, probability=cumulative_count / self.iterations
            )

        return outcomes
