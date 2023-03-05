"""Unit tests for the Task class."""
import unittest
from uuid import UUID

from software_project_estimator.task import Task


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
