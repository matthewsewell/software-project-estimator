from abc import ABC, abstractmethod

from software_project_estimator.event import Event


class Observer(ABC):
    """
    Observer class used to observe an observable object
    """

    @abstractmethod
    def update(self, event: Event):
        """
        Update the observer with the event
        """
        raise NotImplementedError


class Observable(ABC):
    """
    Observable class used to notify observers of events
    """

    def __init__(self):
        self._observers = []

    def register_observer(self, observer: Observer):
        """
        Register an observer
        """
        self._observers.append(observer)

    def notify_observers(self, event: Event):
        """
        Notify all observers of an event
        """
        for observer in self._observers:
            observer.update(event)

    def unregister_observer(self, observer: Observer):
        """
        Unregister an observer
        """
        self._observers.remove(observer)
