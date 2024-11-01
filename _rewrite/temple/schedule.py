from ratemyprofessor.database import RateMyProfessor, Teacher
from datetime import datetime
from dateutil import parser
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import math
import random


class Schedule:
    """Class representing a schedule containing multiple events."""

    def __init__(self, _schedule: list[dict[str, any]]):
        self.classes: dict[str, Class] = {
            "online": [],
            "normal": [],
        }
        self.add_schedule(_schedule)

    def __eq__(self, _other: object) -> bool:
        return self.classes == _other.classes

    def __hash__(self) -> int:
        return hash(tuple(self.classes))

    def add_schedule(self, _schedule: list[dict[str, any]]):
        """Adds events to the schedule from a list of courses."""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        for section in _schedule:
            if section["instructionalMethod"] == "CLAS":
                for meeting in section["meetingsFaculty"]:
                    for day in days:
                        if meeting["meetingTime"][day]:
                            time_beg = meeting["meetingTime"]["beginTime"]
                            time_beg = time_beg[:2] + ":" + time_beg[2:]
                            time_beg = parser.parse(time_beg)

                            time_end = meeting["meetingTime"]["endTime"]
                            time_end = time_end[:2] + ":" + time_end[2:]
                            time_end = parser.parse(time_end)

                            self.classes["normal"].append(Class(section, day, time_beg, time_end))
            elif section["instructionalMethod"] == "OLL":
                self.classes["online"].append(OnlineClass(section))

    def has_overlap(self) -> bool:
        """Checks if any events overlap within the schedule."""

        # Group events by day to check overlaps within each day
        events_by_day = {}
        for event in self.classes["normal"]:
            events_by_day.setdefault(event.day, []).append(event)

        # Check for overlaps within each day
        for events in events_by_day.values():
            events.sort(key=lambda e: e.begin)  # Sort by start time
            for i in range(1, len(events)):
                if events[i - 1].end > events[i].begin:  # Overlap detected
                    return True
        return False

    def get_formatted_time(self, _hour: int) -> str:
        """Returns a formatted time string in AM/PM format."""
        label = "PM" if 12 <= _hour < 24 else "AM"
        _hour = _hour % 12 or 12  # Convert 0 to 12 for midnight
        return f"{_hour}:00 {label}"

    def get_dark_mode_colors(self) -> list:
        """Generates a list of suitable colors for dark mode from XKCD colors."""
        dark_mode_colors = []
        for color_name in mcolors.XKCD_COLORS:
            r, g, b = mcolors.to_rgb(mcolors.XKCD_COLORS[color_name])
            luminance = (r * 0.299 + g * 0.587 + b * 0.114) * 255
            if 50 <= luminance <= 80:
                dark_mode_colors.append(mcolors.XKCD_COLORS[color_name])

        dark_mode_colors.sort()
        random.seed(2024)
        random.shuffle(dark_mode_colors)
        return dark_mode_colors

    def get_range(self) -> tuple[float, float]:
        """Returns the minimum and maximum times of events in the schedule."""
        time_min = 24
        time_max = 0

        for event in self.classes["normal"]:
            time_min = min(time_min, event.begin.hour + event.begin.minute / 60)
            time_max = max(time_max, event.end.hour + event.end.minute / 60)
        return time_min, time_max

    def get_schedule_time(self, time: datetime) -> float:
        """Converts a datetime object to a float representing hours left in the day."""
        return 24 - (time.hour + time.minute / 60)

    def show(self):
        """Displays the weekly schedule using matplotlib."""
        plt.style.use("dark_background")
        plt.figure(figsize=(20, 8))

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        # times = ["{0}:00".format(hour) for hour in range(24, -1, -1)]
        times = [self.get_formatted_time(hour) for hour in range(24, -1, -1)]

        plt.xticks(np.arange(len(days)), days)
        plt.yticks(np.arange(len(times)), times)
        plt.ylabel("Time")
        plt.xlabel("Day")
        plt.title("Weekly Schedule")
        plt.tick_params(axis="both", which="major", pad=15)

        dark_mode_colors = self.get_dark_mode_colors()
        event_colors: dict[str, any] = {}

        if len(self.classes["normal"]) > 0:
            range_min, range_max = self.get_range()
            range_min = 24 - math.floor(range_min) + 0.25
            range_max = 24 - math.ceil(range_max) - 0.25
            plt.ylim(range_max, range_min)
            # plt.ylim(0, 24)

            CELL_WIDTH = 0.98

            for event in self.classes["normal"]:
                beg: float = self.get_schedule_time(event.begin)
                end: float = self.get_schedule_time(event.end)

                if event.name not in event_colors:
                    event_colors[event.name] = dark_mode_colors.pop(0)

                plt.bar(
                    event.day,
                    height=(end - beg),
                    bottom=beg,
                    width=CELL_WIDTH,
                    color=event_colors[event.name],
                    edgecolor="black",
                )
                plt.text(event.day, (beg + end) / 2, event.name, ha="center", va="center", fontsize=8)

                def to_hm(time: datetime):
                    label = "PM" if 12 <= time.hour < 24 else "AM"
                    return "{0}:{1:0>2} {2}".format(time.hour % 12 or 12, time.minute, label)

                plt.text(
                    event.day - CELL_WIDTH / 2 + 0.02, beg - 0.05, to_hm(event.begin), ha="left", va="top", fontsize=8
                )
                plt.text(
                    event.day - CELL_WIDTH / 2 + 0.02,
                    end + 0.05,
                    to_hm(event.end),
                    ha="left",
                    va="bottom",
                    fontsize=8,
                    fontfamily="monospace",
                )
                plt.text(
                    event.day + CELL_WIDTH / 2 - 0.02,
                    beg - 0.05,
                    f"Section: {event.section}",
                    ha="right",
                    va="top",
                    fontsize=8,
                )
                plt.text(
                    event.day + CELL_WIDTH / 2 - 0.02,
                    end + 0.05,
                    event.subject_course,
                    ha="right",
                    va="bottom",
                    fontsize=8,
                )
        plt.show()


class ScheduleCompare:
    """Class representing a function used to compare schedules for sorting."""

    def not_overlap(_s: Schedule):
        return not _s.has_overlap()

    def week_range(_s: Schedule):
        min, max = _s.get_range()
        return max - min

    def week_total(_s: Schedule):
        events_by_day = {}
        for event in _s.classes["normal"]:
            events_by_day.setdefault(event.day, []).append(event)

        total_time = 0
        for events in events_by_day.values():
            events.sort(key=lambda e: e.begin)
            prev_time = events[0].begin.hour + events[0].begin.minute / 60
            curr_time = events[-1].end.hour + events[-1].end.minute / 60
            total_time += curr_time - prev_time
        return total_time

    def between_total(_s: Schedule):
        events_by_day = {}
        for event in _s.classes["normal"]:
            events_by_day.setdefault(event.day, []).append(event)

        total_time = 0
        for events in events_by_day.values():
            events.sort(key=lambda e: e.begin)
            for i in range(1, len(events)):
                prev_time = events[i - 1].end.hour + events[i - 1].end.minute / 60
                curr_time = events[i].begin.hour + events[i].begin.minute / 60
                total_time += curr_time - prev_time
        return total_time

    def teacher_rating(_s: Schedule, *, penalty_rating=2.0, penalty_num_ratings=1.0):
        found_class = set()

        sum_rating = 0
        sum_num_ratings = 0

        for class_type in _s.classes.values():
            for _class in class_type:
                if _class.subject_course not in found_class:
                    found_class.add(_class.subject_course)

                    teachers: list[Teacher] = _class.get_teachers()
                    if len(teachers) == 0:
                        # Penalty for not having a rating
                        sum_rating += penalty_rating * penalty_num_ratings
                        sum_num_ratings += penalty_num_ratings
                    else:
                        for teacher in teachers:
                            sum_rating += teacher.avg_rating_rounded * teacher.num_ratings
                            sum_num_ratings += teacher.num_ratings
        return sum_rating / sum_num_ratings
