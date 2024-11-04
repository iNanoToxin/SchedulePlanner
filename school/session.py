from pydantic import Json
from typing import Tuple, List, Optional, Callable, Union
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

    def login(self, *, username: str = "", password: str = ""):
        raise NotImplementedError("Subclasses must implement this method")

    def fetch(self, _url: str, _query_params: Json) -> Tuple[bool, Union[Json, str]]:
        if not self._authenticated:
            return False, "You are not logged in."

        try:
            response = self._session.get(_url, params=_query_params)

            if response.status_code != 200:
                return False, f"Failed to retrieve the page. Status code: {response.status_code}"
            return True, response.json()
        except ValueError:
            return False, "You are not logged in."
        except Exception as error:
            return False, error.with_traceback()

    def fetch_all(
        self,
        _url: str,
        _query_params: Json,
        *,
        filter: Optional[Callable[[Json], bool]] = None,
        output: bool = False,
    ) -> Tuple[bool, Union[List[Json], str]]:
        _query_params["pageOffset"] = 0
        _query_params["pageMaxSize"] = 2000
        data: List[Json] = []

        while True:
            success, result = self.fetch(_url, _query_params)
            if not success:
                return success, result
            if not result["success"] or not result["data"]:
                return False, "Fetch failed. Data not found."

            if filter:
                # Only append filtered values
                data.extend(item for item in result["data"] if filter(item))
            else:
                # Appened all results
                data.extend(result["data"])

            # Update page offset by length of the data
            _query_params["pageOffset"] += len(result["data"])

            if output:
                print(f"Fetched data ({_query_params["pageOffset"]} out of {result["totalCount"]}).")

            if _query_params["pageOffset"] >= result["totalCount"]:
                break
        return True, data

    def send(self, _url: str, _data: Json) -> requests.Response:
        return self._session.post(_url, _data)
