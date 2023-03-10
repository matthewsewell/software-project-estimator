"""Unit tests for the Task class."""
import unittest
from uuid import UUID

from software_project_estimator.task import Task, TaskGroup


class TestTask(unittest.TestCase):
    """Test the Task class."""

    def test_task(self):
        """Test the Task class happy path."""
        task = Task(name="Test", optimistic=1, pessimistic=2, likely=3)
        self.assertEqual(task.name, "Test")
        self.assertEqual(task.optimistic, 1)
        self.assertEqual(task.pessimistic, 2)
        self.assertEqual(task.likely, 3)
        self.assertIsInstance(task.id_, UUID)

    def test_required_fields(self):
        """
        Test that the Task class requires name, optimistic, pessimistic and
        likely.
        """
        with self.assertRaises(ValueError):
            Task()

    def test_average(self):
        """Test the average property."""
        task = Task(name="Test", optimistic=3, pessimistic=10, likely=5)
        self.assertEqual(task.average, 5.5)

    def test_stddev(self):
        """Test the stddev property."""
        task = Task(name="Test", optimistic=3, pessimistic=10, likely=5)
        self.assertAlmostEqual(task.stddev, 1.1667, places=4)

    def test_variance(self):
        """Test the variance property."""
        task = Task(name="Test", optimistic=3, pessimistic=10, likely=5)
        self.assertAlmostEqual(task.variance, 1.0801, places=4)


class TestTaskGroup(unittest.TestCase):
    """Test the TaskGroup class."""

    def test_task_group(self):
        """Test the TaskGroup class happy path."""
        task_group = TaskGroup(name="Test")
        self.assertEqual(task_group.name, "Test")
        self.assertIsInstance(task_group.id_, UUID)

    def test_required_fields(self):
        """Test that the TaskGroup class requires a name."""
        with self.assertRaises(ValueError):
            TaskGroup()

    def test_add_task_list(self):
        """Test the adding a list of tasks."""
        task_group = TaskGroup(name="Test")
        task_list = []
        for index in range(30):
            task_list.append(
                Task(
                    name=f"Test {index}",
                    optimistic=index,
                    pessimistic=index + 1,
                    likely=index + 0.5,
                )
            )
        task_group.tasks = task_list

        self.assertEqual(task_group.tasks, task_list)

    def test_add_task(self):
        """Test the add_task method."""
        task_group = TaskGroup(name="Test")
        task = Task(name="Test", optimistic=1, pessimistic=2, likely=3)
        added = task_group.add_task(task)
        self.assertTrue(added)
        self.assertEqual(task_group.tasks, [task])

    def test_add_task_twice_fails(self):
        """
        Test the add_task method when the task is already in the group.
        """
        task_group = TaskGroup(name="Test")
        task = Task(name="Test", optimistic=1, pessimistic=2, likely=3)
        added = task_group.add_task(task)
        self.assertTrue(added)
        added_again = task_group.add_task(task)
        self.assertFalse(added_again)
        self.assertEqual(task_group.tasks, [task])

    def test_task_count(self):
        """Test the task_count property."""
        task_group = TaskGroup(name="Test")
        self.assertEqual(task_group.task_count, 0)
        task = Task(name="Test", optimistic=1, pessimistic=2, likely=3)
        task_group.add_task(task)
        self.assertEqual(task_group.task_count, 1)
