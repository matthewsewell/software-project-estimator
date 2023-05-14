"""
Loads a CSV file of tasks into a project and prints out the results of a
monte carlo simulation.

IMPORTANT: While the underlying model is backwards compatible to Python 3.9,
this example script requires Python 3.10 due to the use of structural pattern
matching. If you are using Python 3.9, you should use `if` statements instead
of the match statement.
"""
import csv
import os

from software_project_estimator import Project, Task
from software_project_estimator.event import Event
from software_project_estimator.observer import Observer
from software_project_estimator.simulation.monte_carlo import MonteCarlo

NUMBER_OF_ITERATIONS = 100_000


class ProgressIndicator(Observer):  # pylint: disable=too-few-public-methods
    """This is an observer class that watches our progress and reports it."""

    def __init__(self, total: int):
        self.total = total

    def update(self, event: Event):
        """Update the observer with the event."""
        match event.tag:
            case "monte_carlo_run_iteration":
                if current := event.data.get("number"):
                    # We don't need total granularity here. We just want
                    # to show progress to a tenth of a percent.
                    if current % (NUMBER_OF_ITERATIONS / 1_000) == 0:
                        percentage = current / self.total * 100
                        print(f"Simulation: {percentage:.1f}% complete\r", end="")
            case "monte_carlo_simulation_endgrep":
                print(
                    "Monte Simulation: 100% complete. Processing results...\r",
                    end="",
                )
            case "monte_carlo_processing_end":
                print("\n")


def main():
    """
    Load a CSV file of tasks into a project and run a monte carlo simulation.
    """
    file_directory = os.path.dirname(os.path.realpath(__file__))
    csv_file = os.path.join(file_directory, "assets", "fake-project.csv")
    with open(csv_file, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        tasks = []
        for row in reader:
            row["optimistic"] = float(row["optimistic"])
            row["pessimistic"] = float(row["pessimistic"])
            row["likely"] = float(row["likely"])
            tasks.append(Task(**row))
    project = Project(
        name="This is an example project",
        tasks=tasks,
        developer_count=3,
        work_hours_per_day=6.5,
        communication_penalty=0.5,
    )
    monte = MonteCarlo(project, NUMBER_OF_ITERATIONS)
    progress = ProgressIndicator(NUMBER_OF_ITERATIONS)
    monte.register_observer(progress)
    results = monte.run()

    for day, result in results.items():
        print(f"{day}: {result}")


if __name__ == "__main__":
    main()
