from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
import requests


class TUPage:
    # Urls that get information about courses and terms
    Terms = "https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/plan/getTerms"
    CourseInfo = "https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"

    # Post urls that are required to getting new information
    PlanMode = "https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/term/search?mode=plan"
    ResetDataForm = "https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/courseSearch/resetDataForm"

    # Pages that you are required to visit (otherwise you cannot search for courses)
    Login = "https://tuportal.temple.edu"
    Home = "https://tuportal6.temple.edu/group/home"
    Registration = "https://prd-xereg.temple.edu/StudentRegistrationSsb/ssb/registration"


class TUSession:
    _session: requests.Session

    def __init__(self, *, username="", password=""):
        try:
            # Initialize browser and redirect to login page
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get(TUPage.Login)
            driver_wait = WebDriverWait(driver, 10)

            # Fill out username and password if specified
            if username and password and isinstance(username, str) and isinstance(password, str):
                username_field = driver_wait.until(ec.presence_of_element_located((By.ID, "username")))
                password_field = driver_wait.until(ec.presence_of_element_located((By.ID, "password")))
                username_field.send_keys(username)
                password_field.send_keys(password)
                login_button = driver.find_element(By.CLASS_NAME, "btn-login")
                login_button.click()

            # Detect if user has finished logging in (auto accepts trust browser)
            def finish_login(_driver):
                if button := _driver.find_elements(By.ID, "trust-browser-button"):
                    button[0].click()
                return _driver.current_url == TUPage.Home

            # Redirect to self service banner page once logged in (5 minutes max to login)
            WebDriverWait(driver, 5 * 60).until(finish_login)
            driver.get(TUPage.Registration)

            # Click planning link once it is available
            link = driver_wait.until(ec.element_to_be_clickable((By.ID, "planningLink")))
            link.click()

            # Grab required cookies from current session (required for future requests)
            session = requests.Session()
            session.cookies.update(
                {
                    "JSESSIONID": driver.get_cookie("JSESSIONID")["value"],
                    "BIGipServerprd_xereg_8180_pool": driver.get_cookie("BIGipServerprd_xereg_8180_pool")["value"],
                }
            )
            # print(json.dumps({cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}, indent=4))

            # The browser is no longer required after the session is created
            driver.quit()

            self._session = session
        except WebDriverException as error:
            print("Webdriver session failed:", error.msg)
        except Exception as error:
            print("Failed to create session:", error)

    def fetch(self, _url: str, _query_params) -> tuple[bool, any]:
        if self._session is None:
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

    def fetch_all(self, _url: str, _query_params, *, filter=None, output=False) -> tuple[bool, any]:
        _query_params["pageOffset"] = 0
        _query_params["pageMaxSize"] = 2000
        data = []

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

    def send(self, _url: str, _data: dict[str, any]) -> requests.Response:
        return self._session.post(_url, _data)
