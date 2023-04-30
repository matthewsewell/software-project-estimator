"""Unit tests for the Simulator."""
import unittest
from datetime import date
from unittest import mock

from software_project_estimator.project import WEEKS_IN_A_YEAR, Project
from software_project_estimator.simulation.models import IterationResultStatus
from software_project_estimator.task import Task, TaskGroup

from software_project_estimator.simulation.iteration import (  # isort: skip
    Iteration,
    IterationBaseState,
)

from software_project_estimator.simulation.monte_carlo import (  # isort: skip
    MonteCarlo,
    MonteCarloOutcome,
)

from software_project_estimator.simulation.states import (  # isort: skip
    IterationStateCalculatingDays,
    IterationStateCalculatingWeeks,
    IterationStateError,
    IterationStateFinalizing,
)


class TestIteration(unittest.TestCase):
    """Unit tests for the Iteration class."""

    def test_iteration_requires_a_project_to_complete(self):
        """Ensure that the iteration requires a project to complete."""
        iteration = Iteration(project=None)
        iteration.run()
        self.assertIsNotNone(iteration.result)
        self.assertEqual(iteration.result.status, "failure")
        self.assertEqual(iteration.result.message, "No project was provided.")

    def test_iteration_requires_tasks_to_complete(self):
        """Ensure that the iteration requires tasks to complete."""
        project = Project(name="Test")
        iteration = Iteration(project)
        iteration.run()
        self.assertIsNotNone(iteration.result)
        self.assertEqual(iteration.result.status, "failure")
        self.assertEqual(
            iteration.result.message, "No tasks were present in the project."
        )

    def test_iteration_completes_successfully(self):
        """Ensure that the iteration completes."""
        project = Project(name="Test")
        project.tasks = [Task(name="Test", optimistic=1, likely=2, pessimistic=3)]
        iteration = Iteration(project)
        iteration.run()
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
    def test_calculating_weeks(self, *args):
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
        iteration.run()
        args[0].assert_has_calls(
            [mock.call(date(2020, 1, 8)), mock.call(date(2020, 1, 15))]
        )
        args[1].assert_has_calls([mock.call(), mock.call()])

    def test_calculating_weeks_without_project(self):
        """Ensure that we can't calculate weeks without a project."""
        iteration = Iteration(project=None)
        iteration.context.transition_to(IterationStateCalculatingWeeks())
        iteration.context.process()
        self.assertIsInstance(
            iteration.context._state,  # pylint: disable=protected-access
            IterationStateError,
        )

    def test_calculating_days_without_project(self):
        """Ensure that we can't calculate days without a project."""
        iteration = Iteration(project=None)
        iteration.context.transition_to(IterationStateCalculatingDays())
        iteration.context.process()
        self.assertIsInstance(
            iteration.context._state,  # pylint: disable=protected-access
            IterationStateError,
        )

    def test_calculating_days_without_current_data(self):
        """Ensure that we can't calculate days without a current date."""
        iteration = Iteration(project=Project(name="Test", developer_count=1))
        iteration.context.current_date = None
        iteration.context.transition_to(IterationStateFinalizing())
        iteration.context.process()
        self.assertIsInstance(
            iteration.context._state,  # pylint: disable=protected-access
            IterationStateError,
        )

    def test_finalizing_without_project(self):
        """Ensure that we can't finalize without a project."""
        iteration = Iteration(project=None)
        iteration.context.transition_to(IterationStateFinalizing())
        iteration.context.process()
        self.assertIsInstance(
            iteration.context._state,  # pylint: disable=protected-access
            IterationStateError,
        )

    def test_finalizing_without_current_data(self):
        """Ensure that we can't finalize without a current date."""
        iteration = Iteration(project=Project(name="Test", developer_count=1))
        iteration.context.current_date = None
        iteration.context.transition_to(IterationStateCalculatingDays())
        iteration.context.process()
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
    def test_skipping_calculating_weeks(self, *args):
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
        iteration.run()
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

    def test_iteration_base_state_handle_process_implemeted(self):
        """Ensure that things actually work if we include the method."""

        class FakeState(IterationBaseState):
            """Totally fake state."""

            def handle_process(self):
                pass

        state = FakeState()
        self.assertEqual(state.handle_process(), None)

    def test_calculating_days(self):
        """
        Ensure that we calculate using the IterationStateCalculatingDays state
        ultiple times before continuing.
        """
        project = Project(name="Test")
        project.developer_count = 1
        project.start_date = date(2020, 1, 1)
        project.weeks_off_per_year = 0

        project.tasks = [
            Task(name="Test", optimistic=12, pessimistic=12, likely=12),
        ]

        iteration = Iteration(project)
        iteration.run()

        # If we started on 1/1/2020, we should have 12 person days. With
        # holidays and weekends that should come out to 17 calendar days.
        # The actual end date would then be the next day after there was any
        # activity. If we had worked through the 17th that would skip over MLK
        # day and end on the next day, which is the 21st.
        expected_end_date = date(2020, 1, 21)
        self.assertIsNotNone(iteration.result)
        self.assertIsNotNone(iteration.result.attributes)
        self.assertIsNotNone(iteration.result.attributes.get("end_date"))
        self.assertEqual(iteration.result.attributes.get("end_date"), expected_end_date)

    def test_calculating_days_with_multiple_devlopers(self):
        """Same thing but with multiple developers."""
        project = Project(name="Test")
        project.developer_count = 2
        project.communication_penalty = 0
        project.start_date = date(2020, 1, 1)
        project.weeks_off_per_year = 0

        project.tasks = [
            Task(name="Test", optimistic=12, pessimistic=12, likely=12),
        ]

        iteration = Iteration(project)
        iteration.run()

        # If we started on 1/1/2020, we should have 12 person days. With two
        # developers who are not communicating, that should be 6 working
        # calendar days. The actual end date would then be the next day after
        # that, which is the 10th when we account for New Year's Day.
        expected_end_date = date(2020, 1, 10)
        self.assertIsNotNone(iteration.result)
        self.assertIsNotNone(iteration.result.attributes)
        self.assertIsNotNone(iteration.result.attributes.get("end_date"))
        self.assertEqual(iteration.result.attributes.get("end_date"), expected_end_date)

    def test_calculating_days_with_multiple_devlopers_communicating(self):
        """Same thing but with multiple developers and communication."""
        project = Project(name="Test")
        project.developer_count = 2
        project.communication_penalty = 0.5
        project.start_date = date(2020, 1, 1)
        project.weeks_off_per_year = 0

        project.tasks = [
            Task(name="Test", optimistic=12, pessimistic=12, likely=12),
        ]

        iteration = Iteration(project)
        iteration.run()

        # If we started on 1/1/2020, we should have 12 person days. With two
        # developers who are communicating, that should be slightly more than
        # 6 working calendar days. The actual end date would then be the next
        # working day after that, which is the 13th.
        expected_end_date = date(2020, 1, 13)
        self.assertIsNotNone(iteration.result)
        self.assertIsNotNone(iteration.result.attributes)
        self.assertIsNotNone(iteration.result.attributes.get("end_date"))
        self.assertEqual(iteration.result.attributes.get("end_date"), expected_end_date)


class TestMonteCarlo(unittest.TestCase):
    """Test the Monte Carlo simulation."""

    def test_monte_carlo(self):
        """Ensure that we can run a Monte Carlo simulation."""
        project = Project(name="Test")
        project.developer_count = 1
        project.start_date = date(2020, 1, 1)
        project.weeks_off_per_year = 0

        project.tasks = [
            Task(name="Test", optimistic=5, pessimistic=16, likely=12),
        ]

        monte = MonteCarlo(project, 1_000)
        results = monte.run()

        self.assertTrue(len(results))  # We should have some results.
        # MLK day should not be one of them
        self.assertIsNone(results.get(date(2020, 1, 20)))
        count = 0
        for result in results.values():
            count += result.total
            self.assertIsInstance(result, MonteCarloOutcome)
        self.assertEqual(count, 1_000)

    def test_monte_carlo_cumulative_probabilities(self):
        """
        Ensure that the Monte Carlo simulation runs multiple outocmes with
        increasing cumulative probabilities eventually finishing at 100%.
        """
        project = Project(name="Test")
        project.developer_count = 1
        project.start_date = date(2020, 1, 1)
        project.weeks_off_per_year = 0

        project.tasks = [
            Task(name="Test", optimistic=5, pessimistic=16, likely=12),
        ]

        monte = MonteCarlo(project, 100)
        results = monte.run()
        cumulative_probability = 0.0
        for result in results.values():
            self.assertGreater(result.probability, cumulative_probability)
            cumulative_probability = result.probability
        self.assertAlmostEqual(cumulative_probability, 1.0)

    def test_monte_carlo_run_iteration(self):
        """
        Ensure that we can run a single iteration from a Monte Carlo simulation.
        """
        project = Project(name="Test")
        project.developer_count = 1
        project.start_date = date(2020, 1, 1)
        project.weeks_off_per_year = 0

        project.tasks = [
            Task(name="Test", optimistic=5, pessimistic=16, likely=12),
        ]

        monte = MonteCarlo(project, 0)
        result = monte._run_iteration(0)  # pylint: disable=protected-access
        self.assertAlmostEqual(result.status, IterationResultStatus.SUCCESS)

    def test_monte_carlo_preflight(self):
        """
        Ensure that we can run a Monte Carlo simulation with a preflight check.
        """
        project = Project(name="Test")

        # Set up a preflight that will always fail because the maximum weekly
        # hours is 0
        project.developer_count = 2
        project.weekly_work_days = [0]
        project.work_hours_per_day = 1
        project.communication_penalty = 1

        project.tasks = [
            Task(name="Test", optimistic=5, pessimistic=16, likely=12),
        ]

        with self.assertRaises(RuntimeError):
            MonteCarlo(project, 1_000).run()
