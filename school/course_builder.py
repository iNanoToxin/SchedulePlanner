from typing import Dict, List, Set, Iterator, Callable, Optional, Union, Tuple, Literal, Any
from pydantic import BaseModel, StringConstraints, ValidationError
from school.courses import CourseSection
from school.session import SchoolSession
from school.schedule import SchedulePlot
from typing_extensions import Annotated
from itertools import product

CourseConstraint = Annotated[str, StringConstraints(pattern=r"^[A-Z]+\d+$")]
SectionConstraint = Annotated[str, StringConstraints(pattern=r"^\d+$")]
TeacherConstraint = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]


class CourseSelect(BaseModel, frozen=True):
    course: CourseConstraint
    section: Optional[SectionConstraint] = None

    def should_accept(self, _course_section: CourseSection):
        return self.section == _course_section.sequenceNumber


class CourseIgnore(BaseModel, frozen=True):
    course: CourseConstraint
    section: Optional[Union[Tuple[SectionConstraint], SectionConstraint]] = None
    teacher: Optional[Union[Tuple[TeacherConstraint], TeacherConstraint]] = None
    instructional_method: Optional[Literal["CLAS", "OLL"]] = None
    waitlist: Optional[bool] = None

    def should_ignore(self, _course_section: CourseSection) -> bool:
        """
        Determine if the course section should be ignored based on section, teacher, or instructional method.
        """

        # Check section constraint
        if self.section:
            section_numbers = self.section if isinstance(self.section, list) else [self.section]
            if _course_section.sequenceNumber in section_numbers:
                return True

        # Check teacher constraint
        if self.teacher:
            faculty_names = {faculty.get_name().lower() for faculty in _course_section.faculty}
            teacher_names = set(self.teacher) if isinstance(self.teacher, list) else {self.teacher}
            if faculty_names & teacher_names:
                return True

        # Check instructional method constraint
        if self.instructional_method == _course_section.instructionalMethod:
            return True

        # Check waitlist method constraint
        if self.waitlist is not None:
            if self.waitlist:
                if _course_section.seatsAvailable == 0:
                    return True
            else:
                if _course_section.seatsAvailable > 0:
                    return True

        return False


class CourseBuilder:
    _session: SchoolSession
    _term: int
    _courses_select: Set[CourseSelect]
    _courses_ignore: Dict[str, Set[CourseIgnore]]

    def __init__(self, _session: SchoolSession):
        self._session = _session
        self._courses_select = set()
        self._courses_ignore = {}
        self._term = -1

    def select_term(self, _term: int):
        self._term = _term

    def select(self, _selected_courses: List[CourseSelect]):
        self._courses_select = set(_selected_courses)

    def ignore(self, _ignored_courses: List[CourseIgnore]):
        self._courses_ignore.clear()

        for ignored_course in _ignored_courses:
            self._courses_ignore.setdefault(ignored_course.course, set()).add(ignored_course)

    def plot(
        self,
        *,
        sort: Optional[Callable[[SchedulePlot], Any]] = None,
        max: Optional[int] = None,
        **kwargs,
    ):
        schedules = [SchedulePlot(course, school_id=self._session.id) for course in self._get_combinations()]

        if sort is not None:
            schedules = sorted(schedules, key=sort)

        for index, schedule in enumerate(schedules):
            if max is not None and index >= max:
                break
            schedule.print_stats()
            schedule.plot(title=f"Semester Schedule {index + 1}", **kwargs)

    def _get_combinations(
        self,
        *,
        predicate: Optional[Callable[[CourseSection], bool]] = None,
    ) -> Iterator[List[CourseSection]]:
        assert self._term > 0, "term not selected"

        all_sections: List[List[CourseSection]] = []

        for selected_course in self._courses_select:
            try:
                course_sections = self._session.get_course_sections(selected_course.course, term=self._term)
            except ValidationError:
                raise
            except Exception:
                raise AssertionError(f"{selected_course.course} is not a valid course")

            # Course already registered
            if selected_course.section:
                course_sections = list(filter(selected_course.should_accept, course_sections))

                assert course_sections, f"{selected_course.course} has no section numbered {selected_course.section}"
            else:
                course_sections = list(filter(self._section_ignore_filter, course_sections))

                if predicate is not None:
                    course_sections = list(filter(predicate, course_sections))

                assert course_sections, f"{selected_course.course} has no available sections"

            # Append list of sections for each course so that we can get the cartesian product
            all_sections.append(course_sections)

        # Get the cartesian product of all sections
        return filter(self._section_overlap_filter, product(*all_sections))

    def _section_ignore_filter(self, _section: CourseSection) -> bool:
        # Make sure only main campus classes classes are allowed
        if _section.campusDescription != "Main":
            return False

        # Make sure only in-person clasess and online classes are allowed
        if _section.instructionalMethod != "CLAS" and _section.instructionalMethod != "OLL":
            return False

        # Make sure all unwanted courses are ignored
        if _section.subjectCourse in self._courses_ignore:
            return not any(course.should_ignore(_section) for course in self._courses_ignore[_section.subjectCourse])

        # All checks passed
        return True

    def _section_overlap_filter(self, _sections: List[CourseSection]) -> bool:
        # Dictionary to store occupied time slots for each day
        occupied_times = {
            "monday": set(),
            "tuesday": set(),
            "wednesday": set(),
            "thursday": set(),
            "friday": set(),
            "saturday": set(),
            "sunday": set(),
        }

        # Check each section for time conflicts
        for section in _sections:
            for meeting in section.meetingsFaculty:
                mt = meeting.meetingTime

                # Calculate time slot range based on start and end times
                if mt.beginTime and mt.endTime:
                    time_range = (mt.beginTime, mt.endTime)

                    # Check and add occupied time slots for each relevant day
                    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                        if getattr(mt, day):
                            # Check for conflicts on this day
                            if any(start < time_range[1] and end > time_range[0] for start, end in occupied_times[day]):
                                return False  # Overlap detected

                            # Add this time range to the occupied times for this day
                            occupied_times[day].add(time_range)
        # No overlaps found
        return True
