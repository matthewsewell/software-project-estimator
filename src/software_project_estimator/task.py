import math


class Task:
    """Data model for our task object"""

    def __init__(
        self,
        name: str,
        optimistic: float,  # Optimistic estimate in person days
        pessimistic: float,  # Pessimistic estimate in person days
        likely: float,  # Most likely estimate in person days
        group: Optional[str] = None,
    ):
        """
        Initialize a task whith a name, estimates and an optional task group
        identifier.
        """
        self.name = name
        self.optimistic = optimistic
        self.pessimistic = pessimistic
        self.likely = likely
        self.group = group

    @property
    def average(self):
        """property representing the arithmetic mean"""
        return (
            float(self.optimistic) + float(self.pessimistic) + 4 * float(self.likely)
        ) / 6

    @property
    def stddev(self):
        """property representing the standard deviation"""
        return (float(self.pessimistic) - float(self.optimistic)) / 6

    @property
    def variance(self):
        """property representing the variance"""
        return math.sqrt(self.stddev)
