from pydantic import Json
from typing import List
from school.courses import CourseSection, Term
import requests


class SchoolPage:
    # Urls that get information about courses and terms
    Terms: str
    CourseInfo: str

    # Post urls that are required to getting new information
    PlanMode: str
    ResetDataForm: str

    # Pages that you are required to visit (otherwise you cannot search for courses)
    Login: str
    Home: str
    Registration: str


class SchoolSession:
    _session: requests.Session
    _authenticated: bool

    def __init__(self):
        self._session = requests.Session()
        self._authenticated = False

    def login(self):
        raise NotImplementedError

    def get_course_sections(self) -> List[CourseSection]:
        raise NotImplementedError

    def get_terms(self) -> List[Term]:
        raise NotImplementedError

    def fetch(self, _url: str, _query_params: Json) -> Json:
        assert self._authenticated, "user is not logged in"

        response = self._session.get(_url, params=_query_params)

        assert response.status_code == 200, f"failed to retrieve the page: code={response.status_code}"

        return response.json()

    def fetch_all(self, _url: str, _query_params: Json) -> List[Json]:
        _query_params["pageOffset"] = 0
        _query_params["pageMaxSize"] = 2000

        data_list: List[Json] = []

        while True:
            result = self.fetch(_url, _query_params)

            assert result["data"], "no data found"

            # Appened all results
            data_list.extend(result["data"])

            # Update page offset by length of the data
            _query_params["pageOffset"] += len(result["data"])

            if _query_params["pageOffset"] >= result["totalCount"]:
                break
        return data_list

    def send(self, _url: str, _data: Json) -> requests.Response:
        assert self._authenticated, "user is not logged in"

        return self._session.post(_url, _data)
