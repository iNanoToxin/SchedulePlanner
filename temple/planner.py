from temple.session import TUSession, TUPage

class TUPlanner:
    _session: TUSession

    def __init__(self, **kwargs):
        self._session = TUSession(**kwargs)

    def get_course_sections(self, _course_name: str, _term_code: int):
        # Refresh courses and sections (otherwise the server will cache the results)
        self._session.send(TUPage.PlanMode, {"term": _term_code})
        self._session.send(TUPage.ResetDataForm, {"resetCourses": True, "resetSections": True})

        # Fetch all section info for selected courses
        return self._session.fetch_all(
            TUPage.CourseInfo,
            {
                # Format expamples: CIS1057, SCTC1001, ENG0802
                "txt_subjectcoursecombo": _course_name,
                "txt_term": _term_code,
            },
            # Filter out classes that are not on the main campus or are not in person
            filter=lambda c: c["campusDescription"] == "Main" and c["instructionalMethod"] == "CLAS",
        )

    def get_terms(self, _max: int):
        return self._session.fetch(TUPage.Terms, {"offset": 0, "max": _max})

    def print_terms(self, _max: int):
        success, result = self.get_terms(_max)

        if not success:
            print("Error getting term codes:", result)
        else:
            for term in result:
                print(f"CODE: {term["code"]}, TITLE: {term["description"]}")