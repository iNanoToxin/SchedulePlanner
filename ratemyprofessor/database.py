from functools import cache
from pydantic import BaseModel, Json
from typing import List, Dict, Optional
import requests
import base64


def b64decode(_str: str):
    return base64.b64decode(_str.encode()).decode()


def b64encode(_str: str):
    return base64.b64encode(_str.encode()).decode()


class Department(BaseModel):
    id: str
    name: str

    def __str__(self):
        return f"Department({self.name})"


class SchoolSummary(BaseModel):
    campusCondition: float
    campusLocation: float
    careerOpportunities: float
    clubAndEventActivities: float
    foodQuality: float
    internetSpeed: float
    libraryCondition: float
    schoolReputation: float
    schoolSafety: float
    schoolSatisfaction: float
    socialActivities: float

    def __str__(self):
        return f"SchoolSummary({self.campusCondition}, {self.campusLocation})"


class School(BaseModel):
    avgRatingRounded: float
    city: str
    country: str
    departments: List[Department]
    id: str
    legacyId: int
    name: str
    numRatings: int
    state: str
    summary: SchoolSummary

    def __str__(self):
        return f"School({self.name}, {self.avgRatingRounded:.2f}, {self.city}, {self.state})"


class Teacher(BaseModel):
    avgDifficultyRounded: float
    avgRatingRounded: float
    department: str
    departmentId: Optional[str]
    firstName: str
    id: str
    isSaved: bool
    lastName: str
    legacyId: int
    numRatings: int
    school: School
    wouldTakeAgainPercentRounded: float

    def __str__(self):
        return f"Teacher({self.firstName} {self.lastName}, {self.avgRatingRounded:.2f}, {self.numRatings})"

    def get_name(self):
        return f"{self.firstName} {self.lastName}"


class RateMyProfessor:
    Auth = f"Basic {b64encode("test:test")}"
    Url = "https://www.ratemyprofessors.com/graphql"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"Authorization": self.Auth})

        with open("ratemyprofessor/query.gql", "r") as file:
            self._query = file.read()

    def query(self, _json: Dict[str, any]) -> Optional[Json]:
        response = self._session.post(self.Url, json=_json)
        if response.status_code == 200:
            result = response.json()
            if "errors" not in result:
                return result
        return None

    @cache
    def get_schools(self, _search: str, *, offset=-1, max=10) -> List[School]:
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
            return [School(**school["node"]) for school in result["data"]["search"]["schools"]["edges"]]
        return None

    @cache
    def get_teachers(self, _search: str, _school_id: str, *, offset=-1, max=10) -> List[Teacher]:
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
            return [Teacher(**teacher["node"]) for teacher in result["data"]["search"]["teachers"]["edges"]]
        return None

    @cache
    def get_school(self, _id: str) -> Optional[School]:
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
            return School(**result["data"]["node"])
        return None

    @cache
    def get_teacher(self, _id: str) -> Optional[Teacher]:
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
            return Teacher(**result["data"]["node"])
        return None

    @cache
    def get_schema(self) -> Optional[Json]:
        with open("ratemyprofessor/schema.gql", "r") as file:
            return self.query({"query": file.read()})
