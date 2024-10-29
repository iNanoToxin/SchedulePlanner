from temple.session import TUSession, TUPage
from functools import cache
from itertools import product


class TUPlanner:
    _session: TUSession

    def __init__(self, **kwargs):
        self._session = TUSession(**kwargs)
        self._courses = []
        self._section_filter = {}
        self._teacher_filter = {}
        self._filter = lambda _: True

    @cache
    def get_course_sections(self, _course_name: str):
        # Refresh courses and sections (otherwise the server will cache the results)
        self._session.send(TUPage.PlanMode, {"term": self._term})
        self._session.send(TUPage.ResetDataForm, {"resetCourses": True, "resetSections": True})

        def section_filter(_section: dict[str, any]):
            return (
                _section["campusDescription"] == "Main"
                and _section["status"]["sectionOpen"]
                and (_section["seatsAvailable"] > 0 or _section["waitAvailable"] > 0)
                and (_section["instructionalMethod"] == "CLAS" or _section["instructionalMethod"] == "OLL")
            )

        # Fetch all section info for selected courses
        return self._session.fetch_all(
            TUPage.CourseInfo,
            {
                # Format expamples: CIS1057, SCTC1001, ENG0802
                "txt_subjectcoursecombo": _course_name,
                "txt_term": self._term,
            },
            # Filter out classes that are not on the main campus or are not available
            filter=section_filter,
        )

    @cache
    def get_terms(self, _max: int):
        return self._session.fetch(TUPage.Terms, {"offset": 0, "max": _max})

    def print_terms(self, _max: int):
        success, result = self.get_terms(_max)

        if not success:
            print("Error getting term codes:", result)
        else:
            for term in result:
                print(f"CODE: {term["code"]}, TITLE: {term["description"]}")

    def select_term(self, _term: int):
        self._term = _term

    def select_courses(self, _courses: list[str]):
        self._courses = _courses

    def filter_sections(self, _sections: dict[str, list[str]]):
        self._section_filter.update(_sections)

    def filter_teachers(self, _teachers: dict[str, list[str]]):
        self._teacher_filter.update(_teachers)

    def set_filter(self, _filter: any):
        self._filter = _filter

    def get_combinations(self):
        def is_valid_section(_section: dict[str, any]):
            key = _section["subjectCourse"]
            num = _section["sequenceNumber"]

            if self._section_filter.get(key):
                if num in self._section_filter[key]:
                    return False

            if self._teacher_filter.get(key) and _section.get("faculty"):
                for teacher in _section["faculty"]:
                    if teacher["displayName"] in self._teacher_filter[key]:
                        return False
            return self._filter(_section)

        all_sections = []
        for course_name in set(self._courses):
            # Fetch all section info for selected courses
            success, result = self.get_course_sections(course_name)

            if success:
                # Append list of sections for each course so that we can get the cartesian product
                all_sections.append((section for section in result if is_valid_section(section)))

        # Get the cartesian product of all sections
        return list(product(*all_sections))
