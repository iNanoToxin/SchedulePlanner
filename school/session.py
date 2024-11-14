from school.courses import CourseSection, Term
from util.display import render_table
from abc import ABC, abstractmethod
from pydantic import Json
from typing import List, Union
import requests


class SchoolSession(ABC):
    _session: requests.Session
    _authenticated: bool

    def __init__(self):
        self._session = requests.Session()
        self._authenticated = False

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def get_course_sections(self) -> List[CourseSection]:
        pass

    @abstractmethod
    def get_terms(self) -> List[Term]:
        pass

    def print_terms(self, *, max: int):
        terms = self.get_terms(max=max)
        render_table(["Code", "Description"], [(term.code, term.description) for term in terms])

    def fetch(self, _url: str, _query_params: Json, *, json: bool = False) -> Union[Json, str]:
        assert self._authenticated, "user is not logged in"

        response = self._session.get(_url, params=_query_params)

        assert response.status_code == 200, f"failed to retrieve the page: code={response.status_code}"

        return response.json() if json else response.text

    def fetch_all(self, _url: str, _query_params: Json) -> List[Json]:
        _query_params["pageOffset"] = 0
        _query_params["pageMaxSize"] = 2000

        data_list: List[Json] = []

        while True:
            result = self.fetch(_url, _query_params, json=True)

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
