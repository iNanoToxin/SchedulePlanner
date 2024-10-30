from enum import Flag, auto
from typing import Optional
from collections import defaultdict


class Day(Flag):
    Sun = auto()
    Mon = auto()
    Tue = auto()
    Wed = auto()
    Thu = auto()
    Fri = auto()
    Sat = auto()
    All = Sun | Mon | Tue | Wed | Thu | Fri | Sat


class Time:
    day: Day  # The day of the week, represented as a Day flag
    hour: int  # The hour of the time, in the range 0 - 24
    minute: int  # The minute of the time, in the range 0 - 59

    def __init__(self, _day: Day, _hour: int, _minute: int):
        """
        Initialize a Time object with a specified day, hour, and minute.

        Parameters:
            _day (Day): The day of the week.
            _hour (int): The hour of the day (0-24).
            _minute (int): The minute of the hour (0-59).

        Raises:
            AssertionError: If the hour or minute is out of range, or if the hour is 24 and minute is not 0.
        """
        assert 0 <= _hour <= 24, "Hour must be in the range 0 - 24."
        assert 0 <= _minute <= 59, "Minute must be in the range 0 - 59."
        if _hour == 24:
            assert _minute == 0, "Minute must be 0 when hour is 24."
        self.day = _day  # Assign the day of the week
        self.hour = _hour  # Assign the hour
        self.minute = _minute  # Assign the minute

    def __str__(self) -> str:
        """
        Return a string representation of the Time object.

        Returns:
            str: A formatted string representing the time.
        """
        return f"Time({self.day}, {self.hour}, {self.minute})"

    def __hash__(self) -> int:
        """
        Calculate the hash value for the Time object.

        Returns:
            int: A hash value that represents the total minutes since the beginning of the week.
        """
        return self.day.value * 24 * 60 + self.hour * 60 + self.minute


class Range:
    begin: Time  # The starting point of the time range
    end: Time  # The ending point of the time range

    def __init__(self, _begin: Time, _end: Time):
        """
        Initialize a Range object with a begin and end time.

        Parameters:
            _begin (Time): The starting time of the range.
            _end (Time): The ending time of the range.
        """

        if _begin.day == Day.All or _end.day == Day.All:
            assert _begin.day == _end.day, "All days must be selected for both beginning and end time."

        self.begin = _begin  # Assign the starting time
        self.end = _end  # Assign the ending time

    def __str__(self):
        """
        Return a string representation of the Range object.

        Returns:
            str: A string that shows the start and end times of the range.
        """
        return f"Range({self.begin}, {self.end})"  # Format the output for easy readability

    def contains(self, _time: Time) -> bool:
        """
        Check if a given time is within the range.

        The method handles the case where the range spans over multiple days
        by comparing the days represented by the Time objects. If the
        range starts on a later day than it ends, it indicates that the range
        wraps around the week (e.g., from Thursday to Tuesday).

        Parameters:
            _time (Time): The time to check for containment within the range.

        Returns:
            bool: True if the time is within the range, False otherwise.
        """

        # Create new time object so the hash is the same for Day.All
        if self.begin.day == Day.All and self.end.day == Day.All and _time.day != Day.All:
            return self.contains(Time(Day.All, _time.hour, _time.minute))

        # Check if the range wraps around the week
        if self.begin.day.value > self.end.day.value:
            # If the range wraps, check if the time is either after the start or before the end
            return hash(_time) >= hash(self.begin) or hash(_time) <= hash(self.end)

        # For a regular range, check if the time is between the begin and end times
        return hash(self.begin) <= hash(_time) <= hash(self.end)


class Event:
    pass


class Schedule:
    events: dict[Day, list[Event]]
    # classes: list[Class]

    def __init__(self):
        self.events = defaultdict(list[Event])
        self.classes = {}


for day in Day:
    print(day)