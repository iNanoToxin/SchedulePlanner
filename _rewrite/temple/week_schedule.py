from typing import List, Union, Tuple, Iterator
from enum import Enum, auto
from datetime import time

WeekTimeType = Union["WeekTime", Tuple["Day", int, int]]
WeekRangeType = Union["WeekRange", Tuple[WeekTimeType, WeekTimeType]]


class Day(Enum):
    Sun = auto(0)
    Mon = auto()
    Tue = auto()
    Wed = auto()
    Thu = auto()
    Fri = auto()
    Sat = auto()

    @staticmethod
    def names() -> List[str]:
        return ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    @classmethod
    def by_name(cls, _name: str):
        """
        Retrieve a Day enum member based on the provided day name.

        Args:
            _name (str): The name of the day (e.g., 'sunday', 'Monday', 'TUESDAY').

        Returns:
            Day: The corresponding Day enum member if the name is valid.

        Raises:
            ValueError: If the provided name is not a valid day name.
        """
        if isinstance(_name, str) and _name.lower() in cls.names():
            return list(cls)[cls.names().index(_name.lower())]
        raise ValueError("Invalid day name")


class WeekTime:
    day: Day
    hour: int
    minute: int

    def __init__(self, _day: Day, _hour: int, _minute: int):
        assert 0 <= _hour <= 23, "hour must be in the range 0 - 23"
        assert 0 <= _minute <= 59, "minute must be in the range 0 - 59"
        self.day = _day
        self.hour = _hour
        self.minute = _minute

    def total_minutes(self) -> int:
        """Return total minutes since the beginning of the week."""
        return self.day.value * 24 * 60 + self.hour * 60 + self.minute

    def to_minutes(self) -> int:
        return self.hour * 60 + self.minute

    def to_hours(self) -> float:
        return self.hour + self.minute / 60

    def format(self) -> str:
        return time(self.hour, self.minute).strftime("%I:%M %p")

    def __eq__(self, _other: "WeekTime") -> bool:
        return self.total_minutes() == _other.total_minutes()

    def __le__(self, _other: "WeekTime") -> bool:
        return self.total_minutes() <= _other.total_minutes()

    def __lt__(self, _other: "WeekTime") -> bool:
        return self.total_minutes() < _other.total_minutes()

    def __hash__(self) -> int:
        return self.total_minutes()

    def __repr__(self) -> str:
        return f"WeekTime({self.day}, {self.hour}, {self.minute})"

    def __str__(self) -> str:
        return f"WeekTime({self.day.name} {self.format()})"


class WeekRange:
    start: WeekTime
    end: WeekTime

    def __init__(self, _start: WeekTimeType, _end: WeekTimeType):
        self.start = WeekTime(*_start) if isinstance(_start, tuple) else _start
        self.end = WeekTime(*_end) if isinstance(_end, tuple) else _end
        assert self.start <= self.end, "Start time must be before end time"

    def duration_minutes(self) -> int:
        return self.end.total_minutes() - self.start.total_minutes()

    def overlaps(self, _other: "WeekRange") -> bool:
        """Check if this time range overlaps with another."""
        return self.end > _other.start and _other.end > self.start

    def split(self, _other: "WeekRange") -> List["WeekRange"]:
        """Split this time range based on another time range."""
        results = []

        # Before the overlap
        if self.start < _other.start:
            results.append(WeekRange(self.start, _other.start))

        # After the overlap
        if self.end > _other.end:
            results.append(WeekRange(_other.end, self.end))

        return results

    def __eq__(self, _other: "WeekRange") -> bool:
        return hash(self) == hash(_other)

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __repr__(self) -> str:
        return f"WeekRange({repr(self.start)}, {repr(self.end)})"

    def __str__(self) -> str:
        return f"WeekRange({self.start.day.name} {self.start.format()} - {self.end.day.name} {self.end.format()})"


class WeekSchedule:
    _ranges: List[WeekRange]
    _iterator: Iterator[WeekRange]

    def __init__(self):
        self._ranges = []

    def add_day(self, _day: Day):
        self.add_range(WeekTime(_day, 0, 0), WeekTime(_day, 24, 0))

    def sub_day(self, _day: Day):
        self.sub_range(WeekTime(_day, 0, 0), WeekTime(_day, 24, 0))

    def add_range(self, _start: WeekTimeType, _end: WeekTimeType):
        """Add a new time range."""
        time_range = WeekRange(_start, _end)

        if time_range not in self._ranges:
            self._ranges.append(time_range)
            self.merge()

    def sub_range(self, _start: WeekTimeType, _end: WeekTimeType):
        """Subtract a time range from the existing ranges, splitting as necessary."""
        subtract_range = WeekRange(_start, _end)

        for time_range in self._ranges.copy():
            if time_range.overlaps(subtract_range):
                # Split existing range into two parts if needed
                self._ranges.remove(time_range)
                self._ranges.extend(time_range.split(subtract_range))
                self.merge()

    def merge(self):
        if not self._ranges:
            return

        sorted_ranges = sorted(self._ranges, key=lambda r: r.start)
        merged_ranges = []

        previous = sorted_ranges[0]
        for time_range in sorted_ranges[1:]:
            if time_range.start <= previous.end:
                previous = WeekRange(previous.start, max(previous.end, time_range.end))
            else:
                merged_ranges.append(previous)
                previous = time_range

        merged_ranges.append(previous)

        self._ranges = merged_ranges

    def invert(self):
        """Invert the filter, returning the time ranges that are not included."""
        sorted_ranges = sorted(self._ranges, key=lambda r: r.start)
        invert_ranges = []

        # Define the full week range (00:00 Sunday to 24:00 Saturday)
        full_week_start = WeekTime(Day.Sun, 0, 0)
        full_week_end = WeekTime(Day.Sat, 24, 0)

        # Start with the full range
        previous = full_week_start
        for time_range in sorted_ranges:
            # If there's a gap between current start and the existing range
            if previous < time_range.start:
                invert_ranges.append(WeekRange(previous, time_range.start))

            # Move the current start to the end of the existing range
            previous = time_range.end

        # If there's any time left after the last existing range
        if previous < full_week_end:
            invert_ranges.append(WeekRange(previous, full_week_end))

        self._ranges = invert_ranges

    def overlaps_range(self, _range: WeekRange):
        """Check if this filter has an overlap with the provided range."""
        return any(time_range.overlaps(_range) for time_range in self._ranges)

    def overlaps(self, _other: "WeekSchedule") -> bool:
        """Check if this filter has any overlapping ranges with another filter."""
        return any(self.overlaps_range(time_range) for time_range in _other._ranges)

    def __iadd__(self, _other: Union[Day, WeekRangeType]) -> "WeekSchedule":
        if isinstance(_other, Day):
            self.add_day(_other)
        elif isinstance(_other, WeekRange):
            self.add_range(_other.start, _other.end)
        elif isinstance(_other, tuple):
            self.add_range(*_other)
        else:
            raise Exception(f"Expected Union[Day, WeekRangeType], got {type(_other).__name__}")
        return self

    def __isub__(self, _other: Union[Day, WeekRangeType]) -> "WeekSchedule":
        if isinstance(_other, Day):
            self.sub_day(_other)
        elif isinstance(_other, WeekRange):
            self.sub_range(_other.start, _other.end)
        elif isinstance(_other, tuple):
            self.sub_range(*_other)
        else:
            raise Exception(f"Expected Union[Day, WeekRangeType], got {type(_other).__name__}")
        return self

    def __neg__(self) -> "WeekSchedule":
        new_filter = WeekSchedule()
        new_filter._ranges = self._ranges.copy()
        new_filter.invert()
        return new_filter

    def __getitem__(self, _index: Union[int, slice]) -> Union[WeekRange, List[WeekRange]]:
        return self._ranges[_index]

    def __iter__(self) -> Iterator[WeekRange]:
        self._iterator = iter(self._ranges)
        return self

    def __next__(self) -> WeekRange:
        return next(self._iterator)

    def __repr__(self) -> str:
        return f"WeekSchedule([\n{",\n".join(" " * 4 + repr(r) for r in self._ranges)}\n])"

    def __str__(self) -> str:
        return f"WeekSchedule([\n{",\n".join(" " * 4 + str(r) for r in self._ranges)}\n])"
