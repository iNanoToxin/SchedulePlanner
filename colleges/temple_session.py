from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from school.session import SchoolSession
from school.courses import CourseSection, Term
from functools import cache
from typing import List, Optional


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


class TUSession(SchoolSession):
    @property
    def id(self) -> str:
        return "U2Nob29sLTk5OQ=="

    def login(
        self,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        disable_gui: bool = False,
    ):
        try:
            options = Options()
            options.add_argument("--start-maximized")  # Start maximized

            if disable_gui:
                options.add_argument("--headless")  # Runs without GUI

            # Initialize browser and redirect to login page
            driver = webdriver.Chrome(options=options)
            # driver.maximize_window()
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
            self._session.cookies.update(
                {
                    "JSESSIONID": driver.get_cookie("JSESSIONID")["value"],
                    "BIGipServerprd_xereg_8180_pool": driver.get_cookie("BIGipServerprd_xereg_8180_pool")["value"],
                }
            )
            self._authenticated = True
            # print(json.dumps({cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}, indent=4))

            # The browser is no longer required after the session is created
            driver.quit()
        except WebDriverException as error:
            print("Webdriver session failed:", error.msg)
        except Exception as error:
            print("Failed to create session:", error)

    @cache
    def get_course_sections(self, _course: str, *, term: int) -> List[CourseSection]:
        # Refresh courses and sections (otherwise the server will cache the results)
        self.send(TUPage.PlanMode, {"term": term})
        self.send(TUPage.ResetDataForm, {"resetCourses": True, "resetSections": True})

        # Fetch all section info for selected courses
        return [
            CourseSection(**course)
            for course in self.fetch_all(TUPage.CourseInfo, {"txt_subjectcoursecombo": _course, "txt_term": term})
        ]

    @cache
    def get_terms(self, *, max: int) -> List[Term]:
        # Fetch info for available terms
        return [Term(**term) for term in self.fetch(TUPage.Terms, {"offset": 0, "max": max}, json=True)]
