"""
Loads a CSV file of tasks into a project and prints out the results of a
monte carlo simulation.
"""
import csv
import os

from software_project_estimator import Project, Task
from software_project_estimator.simulation.monte_carlo import MonteCarlo

def main():
    file_directory = os.path.dirname(os.path.realpath(__file__))
    csv_file = os.path.join(file_directory, "assets", "fake-project.csv")
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        tasks = []
        for row in reader:
            row['optimistic'] = float(row['optimistic'])
            row['pessimistic'] = float(row['pessimistic'])
            row['likely'] = float(row['likely'])
            tasks.append(Task(**row))
    project = Project(
        name="This is an example project",
        tasks=tasks,
        developer_count=3,
        work_hours_per_day=6.5,
        communication_penalty=0.5,
    )
    monte = MonteCarlo(project, 100_000)
    results = monte.run()

    for day, result in results.items():
        print(f"{day}: {result}")


if __name__ == "__main__":
    main()
