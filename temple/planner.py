from temple.session import TUSession, TUPage
from school.courses import CourseSection
from functools import cache
from itertools import product
from typing import Dict, List, Callable


class TUPlanner(TUSession):
    _courses: List[str]
    _section_filter: Dict[str, List[str]]
    _teacher_filter: Dict[str, List[str]]
    _filter: Callable[[CourseSection], bool]
    _term: int

    def __init__(self):
        self._courses = []
        self._section_filter = {}
        self._teacher_filter = {}
        self._filter = lambda _: True
        super().__init__()

    @cache
    def get_course_sections(self, _course_name: str, *, term: int, waitlist: bool):
        # Refresh courses and sections (otherwise the server will cache the results)
        self.send(TUPage.PlanMode, {"term": term})
        self.send(TUPage.ResetDataForm, {"resetCourses": True, "resetSections": True})

        def section_filter(_section: dict[str, any]):
            return (
                _section["campusDescription"] == "Main"
                # and _section["status"]["sectionOpen"]
                # and (_section["seatsAvailable"] > 0 or waitlist and _section["waitAvailable"] > 0)
                and (_section["instructionalMethod"] == "CLAS" or _section["instructionalMethod"] == "OLL")
            )

        # Fetch all section info for selected courses
        return self.fetch_all(
            TUPage.CourseInfo,
            {
                # Format expamples: CIS1057, SCTC1001, ENG0802
                "txt_subjectcoursecombo": _course_name,
                "txt_term": term,
            },
            # Filter out classes that are not on the main campus or are not available
            filter=section_filter,
        )

    @cache
    def get_terms(self, _max: int):
        return self.fetch(TUPage.Terms, {"offset": 0, "max": _max})

    def print_terms(self, _max: int):
        success, result = self.get_terms(_max)

        if not success:
            print("Error getting term codes:", result)
        else:
            for term in result:
                print(f"CODE: {term["code"]}, TITLE: {term["description"]}")

    def select_term(self, _term: int):
        self._term = _term

    def select_courses(self, _courses: List[str]):
        self._courses = _courses

    def filter_sections(self, _sections: Dict[str, List[str]]):
        self._section_filter = _sections

    def filter_teachers(self, _teachers: Dict[str, List[str]]):
        self._teacher_filter = _teachers

    def set_filter(self, _filter: Callable[[CourseSection], bool]):
        self._filter = _filter

    def get_combinations(self, *, waitlist: bool = False) -> List[List[CourseSection]]:
        def section_filter(_section: CourseSection):
            key = _section.subjectCourse
            num = _section.sequenceNumber

            if self._section_filter.get(key):
                if num in self._section_filter[key]:
                    return False

            if self._teacher_filter.get(key):
                for faculty in _section.faculty:
                    if faculty.displayName in self._teacher_filter[key]:
                        return False
            return self._filter(_section)

        def overlap_filter(_sections: List[CourseSection]):
            for i in range(len(_sections)):
                for j in range(i + 1, len(_sections)):
                    if _sections[i].overlaps(_sections[j]):
                        return False
            return True

        all_sections = []
        for course_name in set(self._courses):
            # Fetch all section info for selected courses
            success, result = self.get_course_sections(course_name, term=self._term, waitlist=waitlist)

            if success:
                assert len(result) > 0, f"{course_name} has no available sections"
                # Append list of sections for each course so that we can get the cartesian product
                all_sections.append(
                    (
                        course_section
                        for section in result
                        if section_filter(course_section := CourseSection(**section))
                    )
                )
            else:
                raise AssertionError(f"{course_name} is not a valid course")

        # Get the cartesian product of all sections
        cartesian_product = list(product(*all_sections))
        return list(filter(overlap_filter, cartesian_product))
