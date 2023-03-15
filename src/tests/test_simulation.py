"""Unit tests for the Task class."""
import unittest

from software_project_estimator.project import Project
from software_project_estimator.simulation.iteration import Iteration
from software_project_estimator.task import Task


class TestIteration(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the Iteration class."""

    async def test_iteration_requires_a_project_to_complete(self):
        """Ensure that the iteration requires a project to complete."""
        iteration = Iteration(project=None)
        await iteration.run()
        self.assertIsNotNone(iteration.result)
        self.assertEqual(iteration.result.status, "failure")
        self.assertEqual(iteration.result.message, "No project was provided.")

    async def test_iteration_requires_tasks_to_complete(self):
        """Ensure that the iteration requires tasks to complete."""
        project = Project(name="Test")
        iteration = Iteration(project)
        await iteration.run()
        self.assertIsNotNone(iteration.result)
        self.assertEqual(iteration.result.status, "failure")
        self.assertEqual(
            iteration.result.message, "No tasks were present in the project."
        )

    async def test_iteration_completes_successfully(self):
        """Ensure that the iteration completes."""
        project = Project(name="Test")
        project.tasks = [Task(name="Test", optimistic=1, likely=2, pessimistic=3)]
        iteration = Iteration(project)
        await iteration.run()
        self.assertIsNotNone(iteration.result)
        self.assertEqual(iteration.result.status, "success")
