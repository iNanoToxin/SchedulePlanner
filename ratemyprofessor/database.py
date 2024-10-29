from functools import cache
import requests
import base64


def b64decode(_str: str):
    return base64.b64decode(_str.encode()).decode()


def b64encode(_str: str):
    return base64.b64encode(_str.encode()).decode()


class School:
    def __init__(self, _data: dict[str, any]):
        self.id = _data.get("id")
        self.legacy_id = _data.get("legacyId")
        self.num_ratings = _data.get("numRatings")
        self.name = _data.get("name")
        self.avg_rating_rounded = _data.get("avgRatingRounded")
        self.city = _data.get("city")
        self.state = _data.get("state")

        if "departments" in _data:
            self.departments = [Department(department) for department in _data.get("departments")]

        if "summary" in _data:
            self.summary = SchoolSummary(_data.get("summary"))

    def __str__(self):
        return f"School({self.id}, {self.name}, {self.avg_rating_rounded}, {self.city}, {self.state})"


class Teacher:
    def __init__(self, _data: dict[str, any]):
        self.id = _data.get("id")
        self.legacy_id = _data.get("legacyId")
        self.first_name = _data.get("firstName")
        self.last_name = _data.get("lastName")
        self.avg_rating_rounded = _data.get("avgRatingRounded")
        self.avg_difficulty_rounded = _data.get("avgDifficultyRounded")
        self.num_ratings = _data.get("numRatings")
        self.would_take_again_percent_rounded = _data.get("wouldTakeAgainPercentRounded")
        self.department = _data.get("department")
        self.department_id = _data.get("departmentId")
        self.is_saved = _data.get("isSaved")

        if "school" in _data:
            self.school = School(_data.get("school"))

    def __str__(self):
        return f"Teacher({self.first_name} {self.last_name}, {self.avg_rating_rounded}, {self.num_ratings})"


class Department:
    def __init__(self, _data: dict[str, any]):
        self.id = _data.get("id")
        self.name = _data.get("name")

    def __str__(self):
        return f"Department({self.name})"


class SchoolSummary:
    def __init__(self, _data: dict[str, any]):
        self.campus_condition = _data.get("campusCondition")
        self.campus_location = _data.get("campusLocation")
        self.career_opportunities = _data.get("careerOpportunities")
        self.club_and_event_activities = _data.get("clubAndEventActivities")
        self.food_quality = _data.get("foodQuality")
        self.internet_speed = _data.get("internetSpeed")
        self.library_condition = _data.get("libraryCondition")
        self.school_reputation = _data.get("schoolReputation")
        self.school_safety = _data.get("schoolSafety")
        self.school_satisfaction = _data.get("schoolSatisfaction")
        self.social_activities = _data.get("socialActivities")

    def __str__(self):
        return f"SchoolSummary({self.campus_condition}, {self.campus_location})"


class RateMyProfessor:
    Auth = f"Basic {b64encode("test:test")}"
    Url = "https://www.ratemyprofessors.com/graphql"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"Authorization": self.Auth})

        with open("ratemyprofessor/query.gql", "r") as file:
            self._query = file.read()

    def query(self, _json: dict[str, any]) -> dict[str, any] | None:
        response = self._session.post(self.Url, json=_json)
        if response.status_code == 200:
            result = response.json()
            if "errors" not in result:
                return result
        return None

    @cache
    def get_schools(self, _search: str, *, offset=-1, max=10):
        result = self.query(
            {
                "query": self._query,
                "variables": {
                    "count": max,
                    "cursor": b64encode(f"arrayconnection:{offset}"),
                    "query": {
                        "text": _search,
                    },
                },
                "operationName": "SchoolSearchPaginationQuery",
            }
        )
        if result:
            return [School(school["node"]) for school in result["data"]["search"]["schools"]["edges"]]
        return None

    @cache
    def get_teachers(self, _search: str, _school_id: str, *, offset=-1, max=10):
        result = self.query(
            {
                "query": self._query,
                "variables": {
                    "count": max,
                    "cursor": b64encode(f"arrayconnection:{offset}"),
                    "query": {
                        "text": _search,
                        "schoolID": _school_id,
                        "fallback": "true",
                    },
                },
                "operationName": "TeacherSearchPaginationQuery",
            }
        )
        if result:
            return [Teacher(teacher["node"]) for teacher in result["data"]["search"]["teachers"]["edges"]]
        return None

    @cache
    def get_school(self, _id: str):
        result = self.query(
            {
                "query": self._query,
                "variables": {
                    "id": _id,
                },
                "operationName": "SchoolQuery",
            }
        )
        if result:
            return School(result["data"]["node"])
        return None

    @cache
    def get_teacher(self, _id: str):
        result = self.query(
            {
                "query": self._query,
                "variables": {
                    "id": _id,
                },
                "operationName": "TeacherQuery",
            }
        )
        if result:
            return Teacher(result["data"]["node"])
        return None

    @cache
    def get_schema(self):
        with open("ratemyprofessor/schema.gql", "r") as file:
            return self.query({"query": file.read()})
