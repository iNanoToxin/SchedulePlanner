from matplotlib.font_manager import FontProperties
from school.week_schedule import WeekSchedule, Day
from school.courses import CourseSection
from util.colors import get_dark_mode_colors
from util.display import render_table
from typing import Dict, List, Tuple, Union
from datetime import time
import matplotlib.pyplot as plt
import math


class SchedulePlot:
    _time_slot: Dict[WeekSchedule, CourseSection]
    _school_id: str

    def __init__(self, _courses: List[CourseSection], *, school_id: str):
        self._time_slot = {course.get_schedule(): course for course in _courses}
        self._school_id = school_id

    def get_range_x(self) -> Tuple[float, float]:
        """Returns the minimum and maximum times of events in the schedule."""
        if not self._time_slot:
            return 0, 6

        day_min = 6
        day_max = 0

        for schedule in self._time_slot.keys():
            for time_range in schedule:
                day_min = min(day_min, time_range.start.day.value)
                day_max = max(day_max, time_range.end.day.value)
        return day_min, day_max

    def get_range_y(self) -> Tuple[float, float]:
        """Returns the minimum and maximum times of events in the schedule."""
        if not self._time_slot:
            return 0, 24

        time_min = 24
        time_max = 0

        for schedule in self._time_slot.keys():
            for time_range in schedule:
                time_min = min(time_min, time_range.start.to_hours())
                time_max = max(time_max, time_range.end.to_hours())
        return time_min, time_max

    def plot(
        self,
        *,
        title: str = "Semester Schedule",
        size: Tuple[float, float] = (24, 8),
        min_distance: Tuple[float, float] = (32, 16),
        font: Union[List[str], str] = ["Cambria", "Arial"],
        font_size: int = 16,
    ):
        """Displays the weekly schedule using matplotlib."""

        assert min_distance[0] > 0 and min_distance[1] > 0, "minimum distance between text must be greater than zero"
        assert size[0] > 0 and size[1] > 0, "plot size must be greater than zero"
        assert font_size > 0, "font size must be greater than zero"

        plt.style.use("dark_background")
        figure = plt.figure(figsize=size)

        day_label = [day.capitalize() for day in Day.names()]
        time_label = [time(hour % 24, 0).strftime("%I:%M %p") for hour in range(24, -1, -1)]
        # time_label = [f"{hour}:00" for hour in range(24, -1, -1)]

        font_properties = FontProperties(family=font, size=font_size)

        plt.xticks(range(len(day_label)), day_label, font_properties=font_properties)
        plt.yticks(range(len(time_label)), time_label, font_properties=font_properties)
        plt.title(title, font_properties=font_properties)
        plt.tick_params(axis="both", which="major", pad=15)

        dark_mode_colors = get_dark_mode_colors()

        course_colors: Dict[str, str] = {
            course.subjectCourse: dark_mode_colors.pop(0)
            for course in sorted(self._time_slot.values(), key=lambda c: c.subjectCourse)
        }

        cell_width = 0.98

        range_min_x, range_max_x = self.get_range_x()
        plt.xlim(range_min_x - 0.5 - (1 - cell_width), range_max_x + 0.5 + (1 - cell_width))
        # plt.xlim(0, 6)

        range_min_y, range_max_y = self.get_range_y()
        range_min_y = 24 - math.floor(range_min_y) + 0.25
        range_max_y = 24 - math.ceil(range_max_y) - 0.25
        plt.ylim(range_max_y, range_min_y)
        # plt.ylim(0, 24)

        distances_x = []
        distances_y = []

        for schedule, course in self._time_slot.items():
            for time_range in schedule:
                day_index = time_range.start.day.value
                class_color = course_colors[course.subjectCourse]
                section_title = f"Section: {course.sequenceNumber}"

                beg: float = 24 - time_range.start.to_hours()
                end: float = 24 - time_range.end.to_hours()

                l_side = day_index - cell_width / 2 + 0.02
                r_side = day_index + cell_width / 2 - 0.02
                t_padding = beg - 0.05
                b_padding = end + 0.05
                middle = (beg + end) / 2

                # Class time range
                bar = plt.bar(day_index, end - beg, cell_width, beg, color=class_color, edgecolor="black")

                # Course title middle
                title_text = plt.text(
                    day_index,
                    middle,
                    course.courseTitle,
                    ha="center",
                    va="center",
                    font_properties=font_properties,
                )

                # Hijack get_figure function used by matplotlib Text class to return
                # the bar's rect instead of the window's rect
                title_text.set_wrap(True)
                title_text.get_figure = lambda bar_rect=bar[0]: bar_rect

                # Start time formatted top left
                start_time_text = plt.text(
                    l_side,
                    t_padding,
                    time_range.start.format(),
                    ha="left",
                    va="top",
                    font_properties=font_properties,
                )

                # End time formatted bottom left
                end_time_text = plt.text(
                    l_side,
                    b_padding,
                    time_range.end.format(),
                    ha="left",
                    va="bottom",
                    font_properties=font_properties,
                )

                # Section number top right
                section_text = plt.text(
                    r_side,
                    t_padding,
                    section_title,
                    ha="right",
                    va="top",
                    font_properties=font_properties,
                )

                # Subject course buttom right
                subject_text = plt.text(
                    r_side,
                    b_padding,
                    course.subjectCourse,
                    ha="right",
                    va="bottom",
                    font_properties=font_properties,
                )

                distances_x.append(
                    lambda t1=start_time_text, t2=section_text: t2.get_window_extent().x0 - t1.get_window_extent().x1
                )
                distances_x.append(
                    lambda t1=end_time_text, t2=subject_text: t2.get_window_extent().x0 - t1.get_window_extent().x1
                )

                distances_y.append(
                    lambda t1=title_text, t2=start_time_text: t2.get_window_extent().y0 - t1.get_window_extent().y1
                )
                distances_y.append(
                    lambda t1=end_time_text, t2=title_text: t2.get_window_extent().y0 - t1.get_window_extent().y1
                )

        while distances_x and (x_dist := min(distances_x, key=lambda f: f()))() < min_distance[0]:
            while x_dist() < min_distance[0]:
                figure.set_figwidth(figure.get_figwidth() + 0.05)

        while distances_y and (y_dist := min(distances_y, key=lambda f: f()))() < min_distance[1]:
            while y_dist() < min_distance[1]:
                figure.set_figheight(figure.get_figheight() + 0.05)

        plt.show()

    def print_stats(self):
        def hm_fmt(_hours):
            # Calculate total seconds
            total_seconds = _hours * 3600

            # Calculate hours, minutes, and seconds
            h = int(total_seconds // 3600)
            m = int((total_seconds % 3600) // 60)

            return f"{h} hr{"s" if h != 1 else ""} {m} min{"s" if m != 1 else ""}"

        print(
            f"WEEK_RANGE({hm_fmt(ScheduleCompare.week_range(self) / 60)}), "
            f"WEEK_TOTAL({hm_fmt(ScheduleCompare.week_total(self) / 60)}), "
            f"BREAK_TOTAL({hm_fmt(ScheduleCompare.between_total(self) / 60)})"
        )

        rows = [
            (
                course.courseTitle,
                course.subjectCourse,
                course.sequenceNumber,
                ("\n").join([teacher.get_name() for teacher in course.get_teachers(self._school_id)]),
                ("\n").join([f"{teacher.avgRatingRounded:.2f}" for teacher in course.get_teachers(self._school_id)]),
                ("\n").join([f"{teacher.numRatings}" for teacher in course.get_teachers(self._school_id)]),
                "In-person" if course.instructionalMethod == "CLAS" else "Online",
                str(course.creditHours or course.creditHourLow or course.creditHourHigh),
                f"{course.seatsAvailable} / {course.maximumEnrollment}",
                f"{course.waitAvailable} / {course.waitCapacity}",
            )
            for course in sorted(self._time_slot.values(), key=lambda c: c.subjectCourse)
        ]

        render_table(
            [
                "Title",
                "Class",
                "Section",
                "Teachers",
                "Ratings",
                "Number of Ratings",
                "Type",
                "Credits",
                "Seats Available",
                "Waitlist Seats Available",
            ],
            rows,
        )

        print(f"OVERALL_RATING: {ScheduleCompare.teacher_rating(self):.3f} avg")


class ScheduleCompare:
    """Class representing a function used to compare schedules for sorting."""

    def week_range(_s: SchedulePlot):
        min, max = _s.get_range_y()
        return int((max - min) * 60)

    def week_total(_s: SchedulePlot):
        total_time = 0
        for schedule in _s._time_slot.keys():
            for time_range in schedule:
                total_time += time_range.end.total_minutes() - time_range.start.total_minutes()
        return total_time

    def between_total(_s: SchedulePlot):
        ranges_by_day = {}

        for schedule in _s._time_slot.keys():
            for time_range in schedule:
                assert time_range.start.day == time_range.end.day, "Must start and end on the same day"

                # Collect all time ranges by day
                ranges_by_day.setdefault(time_range.start.day, []).append(time_range)

        total_time = 0

        # Calculate the time between classes for each day
        for time_ranges in ranges_by_day.values():
            # Sort time ranges by start time
            time_ranges.sort(key=lambda x: x.start)

            # Calculate time between consecutive classes
            for i in range(len(time_ranges) - 1):
                end_of_current = time_ranges[i].end
                start_of_next = time_ranges[i + 1].start
                total_time += start_of_next.total_minutes() - end_of_current.total_minutes()

        return total_time

    def teacher_rating(_s: SchedulePlot, *, penalty_rating=0.0, penalty_num_ratings=100.0):
        found_class = set()

        sum_rating = 0
        sum_num_ratings = 0

        for course in _s._time_slot.values():
            if course.subjectCourse not in found_class:
                found_class.add(course.subjectCourse)

                teachers = course.get_teachers(_s._school_id)
                if len(teachers) == 0:
                    # Penalty for not having a rating
                    sum_rating += penalty_rating * penalty_num_ratings
                    sum_num_ratings += penalty_num_ratings
                else:
                    for teacher in teachers:
                        sum_rating += teacher.avgRatingRounded * teacher.numRatings
                        sum_num_ratings += teacher.numRatings

        if sum_num_ratings == 0:
            return 0
        return sum_rating / sum_num_ratings
