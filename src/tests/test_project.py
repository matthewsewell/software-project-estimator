"""Unit tests for the Task class."""
import unittest
from datetime import date

from software_project_estimator.project import Project


class TestProject(unittest.TestCase):
    """Unit tests for the Project class."""

    def test_project(self):
        """Test the Project happy path."""
        project = Project(name="Test")
        self.assertEqual(project.name, "Test")

    def test_required_fields(self):
        """Test the required_fields property."""
        with self.assertRaises(ValueError):
            Project()

    def test_default_date(self):
        """Test that the date is created with the current date."""
        project = Project(name="Test")
        self.assertEqual(project.start_date, date.today())

    def test_default_developer_count(self):
        """Test that the default developer count is 1."""
        project = Project(name="Test")
        self.assertEqual(project.developer_count, 1)

    def test_default_weeks_off_per_year(self):
        """Test that the default weeks off per year is 2."""
        project = Project(name="Test")
        self.assertEqual(project.weeks_off_per_year, 2.0)

    def test_default_work_days_per_week(self):
        """Test that the default work days per week is 5."""
        project = Project(name="Test")
        self.assertEqual(project.work_days_per_week, 5.0)

    def test_default_work_hours_per_day(self):
        """Test that the default work hours per day is 8."""
        project = Project(name="Test")
        self.assertEqual(project.work_hours_per_day, 8.0)

    def test_default_communication_penalty(self):
        """Test that the default communication penalty is 0.5."""
        project = Project(name="Test")
        self.assertEqual(project.communication_penalty, 0.5)

    def test_default_tasks(self):
        """Test that the default tasks is an empty list."""
        project = Project(name="Test")
        self.assertEqual(project.tasks, [])

    def test_default_task_groups(self):
        """Test that the default task groups is an empty list."""
        project = Project(name="Test")
        self.assertEqual(project.task_groups, [])

    def test_work_week_hours(self):
        """Test the work_week_hours property."""
        project = Project(name="Test")
        self.assertEqual(project.work_week_hours, 40.0)  # 5 days * 8 hours

    def test_num_communication_channels(self):
        """Test the num_communication_channels property."""
        project = Project(name="Test")
        self.assertEqual(project.num_communication_channels, 0)
        project.developer_count = 2
        self.assertEqual(project.num_communication_channels, 1)
        project.developer_count = 3
        self.assertEqual(project.num_communication_channels, 3)
        project.developer_count = 4
        self.assertEqual(project.num_communication_channels, 6)
        project.developer_count = 5
        self.assertEqual(project.num_communication_channels, 10)
        project.developer_count = 6
        self.assertEqual(project.num_communication_channels, 15)

    def test_max_person_days_per_week(self):
        """Test the max_person_days_per_week property."""
        project = Project(name="Test")
        # 1 person working 40 hours per week and 8 hours per day
        # will work 5 days per week
        self.assertEqual(project.max_person_days_per_week, 5.0)
        project.developer_count = 2
        # 2 people each working 40 hours per week and 8 hours per day. They will
        # each lose .5 hours this week due to communication overhead. That gives
        # them collectively 79 hours per week to work. That is 9.875 days per week.
        self.assertEqual(project.max_person_days_per_week, 9.875)
        project.developer_count = 3
        # 3 people each working 40 hours per week and 8 hours per day. They will
        # lose a total of 3 hours this week due to communication overhead. That
        # gives them collectively 117 hours per week to work. That is 14.625 days
        self.assertEqual(project.max_person_days_per_week, 14.625)
