from enum import Enum, auto
from typing import List, Set, Union, Tuple, Iterator
from util.print import pprint

WeekTimeType = Union["WeekTime", Tuple["Day", int, int]]
WeekTimeRangeType = Union["WeekTimeRange", Tuple[WeekTimeType, WeekTimeType]]


class Day(Enum):
    Sun = auto(0)
    Mon = auto()
    Tue = auto()
    Wed = auto()
    Thu = auto()
    Fri = auto()
    Sat = auto()


class WeekTime:
    day: Day
    hour: int
    minute: int

    def __init__(self, _day: Day, _hour: int, _minute: int):
        assert 0 <= _hour <= 24, "Hour must be in the range 0 - 24."
        assert 0 <= _minute <= 59, "Minute must be in the range 0 - 59."
        if _hour == 24:
            assert _minute == 0, "Minute must be 0 when hour is 24."
        self.day = _day
        self.hour = _hour
        self.minute = _minute

    def total_minutes(self) -> int:
        """Return total minutes since the beginning of the week."""
        return self.day.value * 24 * 60 + self.hour * 60 + self.minute

    def formatted_time(self) -> str:
        label = "PM" if 12 <= self.hour < 24 else "AM"
        hour = self.hour % 12 or 12
        return f"{hour:02}:{self.minute:02} {label}"

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
        return f"WeekTime({self.day.name} {self.formatted_time()})"


class WeekTimeRange:
    start: WeekTime
    end: WeekTime

    def __init__(self, _start: WeekTimeType, _end: WeekTimeType):
        self.start = WeekTime(*_start) if isinstance(_start, tuple) else _start
        self.end = WeekTime(*_end) if isinstance(_end, tuple) else _end
        assert self.start <= self.end, "Start time must be before end time"

    def duration_minutes(self) -> int:
        return self.end.total_minutes() - self.start.total_minutes()

    def overlaps(self, _other: "WeekTimeRange") -> bool:
        """Check if this time range overlaps with another."""
        return self.end > _other.start and _other.end > self.start

    def split(self, _other: "WeekTimeRange") -> List["WeekTimeRange"]:
        """Split this time range based on another time range."""
        results = []

        # Before the overlap
        if self.start < _other.start:
            results.append(WeekTimeRange(self.start, _other.start))

        # After the overlap
        if self.end > _other.end:
            results.append(WeekTimeRange(_other.end, self.end))

        return results

    def __eq__(self, _other: "WeekTimeRange") -> bool:
        return hash(self) == hash(_other)

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __repr__(self) -> str:
        return f"WeekTimeRange({repr(self.start)}, {repr(self.end)})"

    def __str__(self) -> str:
        return f"WeekTimeRange({self.start.day.name} {self.start.formatted_time()} - {self.end.day.name} {self.end.formatted_time()})"


class WeekTimeFilter:
    _ranges: List[WeekTimeRange]
    _iterator: Iterator[WeekTimeRange]

    def __init__(self):
        self._ranges = []

    def add_day(self, _day: Day):
        self.add_range(WeekTime(_day, 0, 0), WeekTime(_day, 24, 0))

    def sub_day(self, _day: Day):
        self.sub_range(WeekTime(_day, 0, 0), WeekTime(_day, 24, 0))

    def add_range(self, _start: WeekTimeType, _end: WeekTimeType):
        """Add a new time range."""
        time_range = WeekTimeRange(_start, _end)

        if time_range not in self._ranges:
            self._ranges.append(time_range)
            self.merge()

    def sub_range(self, _start: WeekTimeType, _end: WeekTimeType):
        """Subtract a time range from the existing ranges, splitting as necessary."""
        subtract_range = WeekTimeRange(_start, _end)

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
                previous = WeekTimeRange(previous.start, max(previous.end, time_range.end))
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
                invert_ranges.append(WeekTimeRange(previous, time_range.start))

            # Move the current start to the end of the existing range
            previous = time_range.end

        # If there's any time left after the last existing range
        if previous < full_week_end:
            invert_ranges.append(WeekTimeRange(previous, full_week_end))

        self._ranges = invert_ranges

    def overlaps(self, _other: "WeekTimeFilter") -> bool:
        """Check if this filter has any overlapping ranges with another filter."""
        for range_self in self._ranges:
            for range_other in _other._ranges:
                if range_self.overlaps(range_other):
                    return True
        return False

    def __iadd__(self, _other: Union[Day, WeekTimeRangeType]) -> "WeekTimeFilter":
        if isinstance(_other, Day):
            self.add_day(_other)
        elif isinstance(_other, WeekTimeRange):
            self.add_range(_other.start, _other.end)
        elif isinstance(_other, tuple):
            self.add_range(*_other)
        else:
            raise Exception(f"Expected Union[Day, WeekTimeRangeType], got {type(_other).__name__}")
        return self

    def __isub__(self, _other: Union[Day, WeekTimeRangeType]) -> "WeekTimeFilter":
        if isinstance(_other, Day):
            self.sub_day(_other)
        elif isinstance(_other, WeekTimeRange):
            self.sub_range(_other.start, _other.end)
        elif isinstance(_other, tuple):
            self.sub_range(*_other)
        else:
            raise Exception(f"Expected Union[Day, WeekTimeRangeType], got {type(_other).__name__}")
        return self

    def __neg__(self) -> "WeekTimeFilter":
        new_filter = WeekTimeFilter()
        new_filter._ranges = self._ranges.copy()
        new_filter.invert()
        return new_filter

    def __iter__(self) -> "WeekTimeFilter":
        self._iterator = iter(self._ranges)
        return self

    def __next__(self) -> "WeekTimeFilter":
        # if self._index > len(self._ranges):
        #     raise StopIteration
        # item = self._ranges[self._index]
        # self._index += 1
        # return item
        return next(self._iterator)

    def __repr__(self) -> str:
        return f"WeekTimeFilter([\n{",\n".join(" " * 4 + repr(r) for r in self)}\n])"

    def __str__(self) -> str:
        return f"WeekTimeFilter([\n{",\n".join(" " * 4 + str(r) for r in self)}\n])"



filter = WeekTimeFilter()
filter += Day.Mon
filter += Day.Wed
filter += Day.Fri

# filter = -filter

# for time_range in filter:
#     print(time_range)

# print(filter)

