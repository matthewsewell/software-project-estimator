"""Unit tests for the Task class."""
import unittest
from datetime import date

from software_project_estimator.project import Project


class TestProject(unittest.TestCase):  # pylint: disable=too-many-public-methods
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

    def test_custom_work_days_per_week(self):
        """Test that we can set custom work days"""
        project = Project(name="Test", weekly_work_days=[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(project.work_days_per_week, 7.0)

    def test_default_weekly_work_days(self):
        """Test the default weekly_work_days property."""
        project = Project(name="Test")
        self.assertEqual(
            project.weekly_work_days,
            [  # pylint: disable=R0801
                0,
                1,
                2,
                3,
                4,
            ],
        )

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

    def test_is_christmas_a_holiday(self):
        """Test the is_holiday method with some cheer."""
        project = Project(name="Test")
        self.assertTrue(project.is_holiday(date(2023, 12, 25)))
        self.assertFalse(project.is_holiday(date(2023, 12, 26)))

    def test_person_days_lost_to_holidays_this_week(self):
        """Test the person_days_lost_to_holidays_this_week method."""
        project = Project(name="Test", developer_count=5)
        self.assertEqual(
            project.person_days_lost_to_holidays_this_week(date(2023, 12, 22)), 5
        )

    def test_person_days_not_lost_to_holidays_this_week(self):
        """This is the same as the test above but with holidays turned off"""
        project = Project(name="Test", developer_count=5, country_code=None)
        self.assertEqual(
            project.person_days_lost_to_holidays_this_week(date(2023, 12, 23)), 0
        )

    def test_person_days_lost_to_holidays_this_week_with_none_date(self):
        """Test the person_days_lost_to_holidays_this_week method."""
        project = Project(name="Test", developer_count=5)
        self.assertEqual(project.person_days_lost_to_holidays_this_week(None), 0)

    def test_working_days_whis_week(self):
        """Test the working_days_this_week method."""
        project = Project(name="Test")
        self.assertEqual(
            project.working_days_this_week(date(2020, 1, 1)),
            [
                date(2020, 1, 2),
                date(2020, 1, 3),
                date(2020, 1, 6),
                date(2020, 1, 7),
            ],
        )
        project.start_date = date(2020, 1, 6)
        self.assertEqual(
            project.working_days_this_week(date(2020, 1, 6)),
            [
                date(2020, 1, 6),
                date(2020, 1, 7),
                date(2020, 1, 8),
                date(2020, 1, 9),
                date(2020, 1, 10),
            ],
        )

    def test_failure_on_stupid_country_code(self):
        """Test that the country code must be a valid ISO 3166-1 alpha-2 code."""
        project = Project(name="Test", country_code="UK")
        with self.assertRaises(ValueError):
            project.country_code = "XX"
            project.is_holiday(date(2023, 12, 25))
