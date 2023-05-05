"""Unit tests for the Task class."""

import unittest

from software_project_estimator.event import Event
from software_project_estimator.observer import Observable, Observer


class MyObservable(Observable):  # pylint: disable=too-few-public-methods
    """Observable class used for testing."""

    def __init__(self):
        super().__init__()
        self.event = Event(tag="test", data={"test": "test"})

    def do_something(self):
        """Do something and notify observers."""
        self.notify_observers(self.event)


class MyObserver(Observer):  # pylint: disable=too-few-public-methods
    """Observer class used for testing."""

    def __init__(self):
        self.event = None

    def update(self, event: Event):
        """Update the observer with the event."""
        self.event = event


class TestObserver(unittest.TestCase):
    """Test the observer class."""

    def test_register_observer(self):
        """Test that an observer can be registered."""
        observable = MyObservable()
        observer = MyObserver()
        observable.register_observer(observer)
        self.assertEqual(
            len(observable._observers), 1  # pylint: disable=protected-access
        )

    def test_unregister_observer(self):
        """Test that an observer can be unregistered."""
        observable = MyObservable()
        observer = MyObserver()
        observable.register_observer(observer)
        observable.unregister_observer(observer)
        self.assertEqual(
            len(observable._observers), 0  # pylint: disable=protected-access
        )

    def test_notify_observers(self):
        """Test that an observer can be notified."""
        observable = MyObservable()
        observer = MyObserver()
        observable.register_observer(observer)
        observable.do_something()
        self.assertEqual(observer.event, observable.event)
