"""Unit tests for the Task class."""
import unittest
from datetime import date
from unittest import mock

from software_project_estimator.project import WEEKS_IN_A_YEAR, Project
from software_project_estimator.task import Task, TaskGroup

from software_project_estimator.simulation.iteration import (  # isort: skip
    Iteration,
    IterationBaseState,
    IterationStateCalculatingWeeks,
    IterationStateError,
)


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

    def test_probabilistic_weekly_person_days_lost_to_vacations(self):
        """
        Test the random_weekly_person_days_lost_to_vacations method. Warning:
        this test is probabilistic and may fail occasionally.
        """
        project = Project(name="Test", developer_count=1)

        project.weeks_off_per_year = 1
        iteration = Iteration(project)

        total_days = 0
        for _index in range(WEEKS_IN_A_YEAR):
            total_days += (
                iteration.context.probabilistic_weekly_person_days_lost_to_vacations()
            )
        self.assertTrue(0 <= total_days <= 20)

        project.weeks_off_per_year = 0
        total_days = 0
        for _index in range(WEEKS_IN_A_YEAR):
            total_days += (
                iteration.context.probabilistic_weekly_person_days_lost_to_vacations()
            )
        self.assertEqual(total_days, 0)

        # Ensure that test covereage is 100%.
        project.weeks_off_per_year = 26
        total_days = 0
        for _index in range(WEEKS_IN_A_YEAR):
            total_days += (
                iteration.context.probabilistic_weekly_person_days_lost_to_vacations()
            )
        self.assertTrue(total_days > 0)

    def test_probablistic_estimated_project_person_days_requires_a_project(self):
        """
        Test the probabilistic_estimated_person_days method requires a project.
        """
        iteration = Iteration(project=None)
        self.assertEqual(
            iteration.context.probabilistic_estimated_project_person_days(),
            0.0,
        )

    def test_probabilistic_estimated_project_person_days(self):
        """
        Test the probabilistic_estimated_project_person_days method.
        Warning: this test is probabilistic and may fail occasionally.
        """
        project = Project(name="Test", developer_count=1)
        project.developer_count = 1

        project.tasks = [
            Task(name="Test", optimistic=1, pessimistic=3, likely=2),
        ]
        task_group = TaskGroup(name="Test")
        task_group.tasks = [
            Task(name="Test", optimistic=1, pessimistic=3, likely=2),
            Task(name="Test", optimistic=1, pessimistic=3, likely=2),
        ]
        project.task_groups = [task_group]

        iteration = Iteration(project)

        for _index in range(1000):
            estimated_days = (
                iteration.context.probabilistic_estimated_project_person_days()
            )
            # We should be getting a random number between 3 and 9
            self.assertTrue(3 <= estimated_days <= 9)

    @mock.patch(
        "software_project_estimator.simulation.iteration.IterationContext."
        "probabilistic_weekly_person_days_lost_to_vacations",
        return_value=0,
    )
    @mock.patch(
        "software_project_estimator.Project.person_days_lost_to_holidays_this_week",
        return_value=0,
    )
    async def test_calculating_weeks(self, *args):
        """
        Ensure that we calculate using the IterationStateCalculatingWeeks state
        twice before continuing. The mock calls are the best indicator of this.
        """
        project = Project(name="Test", developer_count=1)
        project.developer_count = 1
        project.start_date = date(2020, 1, 1)

        project.tasks = [
            Task(name="Test", optimistic=12, pessimistic=12, likely=12),
        ]
        iteration = Iteration(project)
        await iteration.run()
        args[0].assert_has_calls(
            [mock.call(date(2020, 1, 8)), mock.call(date(2020, 1, 15))]
        )
        args[1].assert_has_calls([mock.call(), mock.call()])

    async def test_calculating_weeks_without_project(self):
        """Ensure that we can't calculate weeks without a project."""
        iteration = Iteration(project=None)
        iteration.context.transition_to(IterationStateCalculatingWeeks())
        await iteration.context.process()
        self.assertIsInstance(
            iteration.context._state,  # pylint: disable=protected-access
            IterationStateError,
        )

    @mock.patch(
        "software_project_estimator.simulation.iteration.IterationContext."
        "probabilistic_weekly_person_days_lost_to_vacations",
        return_value=0,
    )
    @mock.patch(
        "software_project_estimator.Project.person_days_lost_to_holidays_this_week",
        return_value=0,
    )
    async def test_skipping_calculating_weeks(self, *args):
        """
        If these mocks only get called once, it means that we skipped the weekly
        and went straight to calculating days.
        """
        project = Project(name="Test", developer_count=1)
        project.developer_count = 1
        project.start_date = date(2020, 1, 1)

        project.tasks = [
            Task(name="Test", optimistic=1, pessimistic=1, likely=1),
        ]
        iteration = Iteration(project)
        await iteration.run()
        args[0].assert_called_once()
        args[1].assert_called_once()

    def test_iteration_base_state_handle_process_not_implemented(self):
        """Ensure that the base state raises an exception."""

        class FakeState(IterationBaseState):
            """Totally fake state."""

        with self.assertRaisesRegex(
            TypeError,
            (
                "Can't instantiate abstract class FakeState with abstract "
                "method handle_process"
            ),
        ):
            FakeState()  # pylint: disable=abstract-class-instantiated

    async def test_iteration_base_state_handle_process_implemeted(self):
        """Ensure that things actually work if we include the method."""

        class FakeState(IterationBaseState):
            """Totally fake state."""

            async def handle_process(self):
                pass

        state = FakeState()
        self.assertEqual(await state.handle_process(), None)
